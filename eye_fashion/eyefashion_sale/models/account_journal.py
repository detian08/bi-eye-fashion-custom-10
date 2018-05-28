# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class AccountJournal(models.Model):
    _inherit = 'account.journal'

    is_corporate = fields.Boolean('Corporate',default=False)
    discount_account = fields.Many2one('account.account','Discount Account')

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    @api.depends('amount')
    def _get_actual_amount(self):
        for payment in self:
            if payment.payment_type == 'outbound':
                payment.actual_amount = payment.amount * -1
            else:
                payment.actual_amount = payment.amount

    sale_id = fields.Many2one('sale.order')
    corporate_id = fields.Many2one('res.partner','Corporate')
    actual_amount = fields.Float(string='Payment Amount',compute='_get_actual_amount',store=True)
    team_leader = fields.Many2one('res.users', compute="get_team_leader", string="Team Leader", store=True)

    @api.depends('create_uid')
    def get_team_leader(self):
        for payment in self:
            if payment.create_uid:
                sales_team = payment.create_uid.sale_team_id
                payment.update({
                            'team_leader': sales_team.user_id.id,
                            })

    @api.model
    def default_get(self, fields):
        rec = super(AccountPayment, self).default_get(fields)
        invoice_defaults = self.resolve_2many_commands('invoice_ids', rec.get('invoice_ids'))
        if invoice_defaults and len(invoice_defaults) == 1:
            invoice = invoice_defaults[0]
            if invoice['refund_invoice_id']:
                refund_origin_invoice = self.env['account.invoice'].browse(invoice['refund_invoice_id'][0])
                if refund_origin_invoice.sale_order_id:
                    rec['sale_id'] = refund_origin_invoice.sale_order_id.id
                    rec['amount'] = invoice['amount_total'] - refund_origin_invoice.residual
                else:
                    rec['amount'] = invoice['residual']
            else:
                rec['amount'] = invoice['residual']
        return rec

    @api.onchange('payment_type')
    def _onchange_payment_type(self):
        if not self.invoice_ids:
            # Set default partner type for the payment type
            if self.payment_type == 'inbound':
                self.partner_type = 'customer'
            elif self.payment_type == 'outbound':
                self.partner_type = 'supplier'
        # Set payment method domain
        res = self._onchange_journal()
        if not res.get('domain', {}):
            res['domain'] = {}
        res['domain']['journal_id'] = self.payment_type == 'inbound' and [('at_least_one_inbound', '=', True)] or [('at_least_one_outbound', '=', True)]
        if self.payment_type == 'outbound':
            cash_journal = self.env['res.users'].browse(self.env.uid).sale_team_id.cash_journal_id.id
            res['domain']['journal_id'].append(('id', '=', cash_journal))
        else:
            res['domain']['journal_id'].append(('type', 'in', ('bank', 'cash')))
        return res

    @api.multi
    def post(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_("Only a draft payment can be posted. Trying to post a payment in state %s.") % rec.state)

            if any(inv.state != 'open' for inv in rec.invoice_ids):
                raise ValidationError(_("The payment cannot be processed because the invoice is not open!"))

            # Use the right sequence to set the name
            if rec.payment_type == 'transfer':
                sequence_code = 'account.payment.transfer'
            else:
                if rec.partner_type == 'customer':
                    if rec.payment_type == 'inbound':
                        sequence_code = 'account.payment.customer.invoice'
                    if rec.payment_type == 'outbound':
                        sequence_code = 'account.payment.customer.refund'
                if rec.partner_type == 'supplier':
                    if rec.payment_type == 'inbound':
                        sequence_code = 'account.payment.supplier.refund'
                    if rec.payment_type == 'outbound':
                        sequence_code = 'account.payment.supplier.invoice'
            rec.name = self.env['ir.sequence'].with_context(ir_sequence_date=rec.payment_date).next_by_code(sequence_code)

            # Create the journal entry
            amount = rec.amount * (rec.payment_type in ('outbound', 'transfer') and 1 or -1)
            move = rec._create_payment_entry(amount)

            # In case of a transfer, the first journal entry created debited the source liquidity account and credited
            # the transfer account. Now we debit the transfer account and credit the destination liquidity account.
            if rec.payment_type == 'transfer':
                transfer_credit_aml = move.line_ids.filtered(lambda r: r.account_id == rec.company_id.transfer_account_id)
                transfer_debit_aml = rec._create_transfer_entry(amount)
                (transfer_credit_aml + transfer_debit_aml).reconcile()

            for inv in rec.invoice_ids:
                if inv.refund_invoice_id.sale_order_id:
                    rec.write({'sale_id': inv.refund_invoice_id.sale_order_id.id})
            rec.write({'state': 'posted', 'move_name': move.name})


    def _get_liquidity_move_line_vals(self, amount):
        name = self.name
        if self.payment_type == 'transfer':
            name = _('Transfer to %s') % self.destination_journal_id.name
        if self.corporate_id.corporate_account_id:
            account = self.corporate_id.corporate_account_id.id
        else:
            account = self.payment_type in ('outbound','transfer') and self.journal_id.default_debit_account_id.id or self.journal_id.default_credit_account_id.id
        vals = {
            'name': name,
            'account_id': account,
            'payment_id': self.id,
            'journal_id': self.journal_id.id,
            'currency_id': self.currency_id != self.company_id.currency_id and self.currency_id.id or False,
        }

        # If the journal has a currency specified, the journal item need to be expressed in this currency
        if self.journal_id.currency_id and self.currency_id != self.journal_id.currency_id:
            amount = self.currency_id.with_context(date=self.payment_date).compute(amount, self.journal_id.currency_id)
            debit, credit, amount_currency, dummy = self.env['account.move.line'].with_context(date=self.payment_date).compute_amount_fields(amount, self.journal_id.currency_id, self.company_id.currency_id)
            vals.update({
                'amount_currency': amount_currency,
                'currency_id': self.journal_id.currency_id.id,
            })

        return vals

class AccountInvoiceRefund(models.TransientModel):

    _inherit = "account.invoice.refund"

    @api.multi
    def invoice_refund(self):
        data_refund = self.read(['filter_refund'])[0]['filter_refund']
        inv_obj = self.env['account.invoice']
        context = dict(self._context or {})
        for inv in inv_obj.browse(context.get('active_ids')):
            for picking in inv.sale_order_id.picking_ids:
                if picking.state != 'done':
                    picking.action_cancel()
                else:
                    if picking.location_dest_id.usage == 'customer':
                        # create new picking for returned products
                        picking_type_id = picking.picking_type_id.return_picking_type_id.id or picking.picking_type_id.id
                        new_picking = picking.copy({
                            'move_lines': [],
                            'picking_type_id': picking_type_id,
                            'state': 'draft',
                            'origin': picking.name,
                            'location_id': picking.location_dest_id.id,
                            'location_dest_id': picking.location_id.id})
                        new_picking.message_post_with_view('mail.message_origin_link',
                                                           values={'self': new_picking, 'origin': picking},
                                                           subtype_id=self.env.ref('mail.mt_note').id)
                        for move in picking.move_lines:
                            move.copy({
                                'product_id': move.product_id.id,
                                'product_uom_qty': move.product_uom_qty,
                                'picking_id': new_picking.id,
                                'state': 'draft',
                                'location_id': move.location_dest_id.id,
                                'location_dest_id': move.location_id.id,
                                'picking_type_id': picking_type_id,
                                'warehouse_id': picking.picking_type_id.warehouse_id.id,
                                'origin_returned_move_id': move.id,
                                'procure_method': 'make_to_stock',
                            })
                        new_picking.action_confirm()
                        new_picking.action_assign()

        return self.compute_refund(data_refund)