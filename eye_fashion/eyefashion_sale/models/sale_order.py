# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools import float_compare
from odoo.exceptions import UserError
from datetime import datetime, date
import odoo.addons.decimal_precision as dp


class SaleOrderPayment(models.Model):
    _name = 'sale.order.payment'

    sale_order = fields.Many2one('sale.order','Sale Order')
    payment_method_id = fields.Many2one('account.journal','Payment Method')
    amount = fields.Float('Amount')


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _get_related_account_payments(self):
        for order in self:
            payment_ids = []
            payment_ids += [purchase.id for purchase in self.env['account.payment'].search([('sale_id', '=', order.id)])]
            order.payment_ids = payment_ids

    @api.onchange('order_line')
    def get_need_medical(self):
        for order in self:
            for line in order.order_line:
                need_medical = 0
                categ = line.product_id.categ_id
                while categ:
                    if categ.need_medical:
                        need_medical = 1
                        break;
                    categ = categ.parent_id
                if need_medical:
                    order.need_medical = True
                    break;

    @api.model
    def _default_warehouse_id(self):
        sales_team_id = self.env.user.sale_team_id.id
        warehouse_ids = self.env['crm.team'].browse(sales_team_id).warehouse_id
        return warehouse_ids

    @api.model
    def _default_team_analytic_id(self):
        sales_team_id = self.env.user.sale_team_id.id
        analytic_account_id = self.env['crm.team'].browse(sales_team_id).analytic_account_id
        return analytic_account_id


    @api.depends('order_line.price_total')
    def _amount_all(self):
        """
        Compute the total amounts of the SO.
        """
        for order in self:
            paid_amount = 0
            refunded_amount = 0
            for payment in order.payment_ids:
                paid_amount += payment.actual_amount
            for invoice in order.invoice_ids:
                if invoice.refund_invoice_id:
                    refunded_amount += invoice.amount_total

            amount_untaxed = amount_tax = 0.0
            for line in order.order_line:
                product = line.product_id.with_context(
                    lang=line.order_id.partner_id.lang,
                    partner=line.order_id.partner_id.id,
                    quantity=line.product_uom_qty,
                    date=line.order_id.date_order,
                    pricelist=line.order_id.pricelist_id.id,
                    uom=line.product_uom.id
                )
                line.price_unit = line.product_id.lst_price
                if line.order_id.pricelist_id and line.order_id.partner_id:
                    line.price_unit = self.env['account.tax']._fix_tax_included_price(line._get_display_price(product),product.taxes_id, line.tax_id)
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax

            rounded_total = round(amount_untaxed + amount_tax)
            order.update({
                'amount_untaxed': order.pricelist_id.currency_id.round(amount_untaxed),
                'amount_tax': order.pricelist_id.currency_id.round(amount_tax),
                'amount_total': amount_untaxed + amount_tax,
                'rounded_total': round(amount_untaxed + amount_tax),
                'rounded_total_after_refund': round(amount_untaxed + amount_tax - refunded_amount),
                'round_off_value': rounded_total - (amount_untaxed + amount_tax),
                'paid_amount': paid_amount,
                'residual': rounded_total - paid_amount,
            })

    # payment_ids = fields.One2many('sale.order.payment','sale_order','Payments')
    corporate_id = fields.Many2one('res.partner','Corporate')
    sale_type = fields.Char('Type')
    is_corporate = fields.Boolean('Is Corporate')
    to_pay = fields.Boolean('To pay',default=True)
    medical_id = fields.Many2one('res.partner.lab','Medical')
    cash_journal_id = fields.Many2one('account.journal','Cash Journal')
    bank_journal_id1 = fields.Many2one('account.journal','Bank Journal')
    bank_journal_id2 = fields.Many2one('account.journal','Bank Journal')
    corporate_journal_id = fields.Many2one('account.journal','Corporate Journal')
    insurance_company_ids = fields.Char(compute='get_insurance_company')
    cash_amount = fields.Float('Cash')
    bank_amount1 = fields.Float('Ahly')
    bank_amount2 = fields.Float('Alex')
    corporate_amount = fields.Float('Corporate')
    cash_memo = fields.Char('Memo')
    bank_memo1 = fields.Char('Memo')
    bank_memo2 = fields.Char('Memo')
    corporate_memo = fields.Char('Memo')
    need_medical = fields.Boolean(string='Need Medical', compute='get_need_medical')
    round_off_value = fields.Float(compute='_amount_all', string='Round off amount')
    rounded_total = fields.Float(compute='_amount_all', string='Rounded Total')
    rounded_total_after_refund = fields.Float(compute='_amount_all', string='Rounded Total After Refund')
    paid_amount = fields.Float(compute='_amount_all',string='Paid')
    residual = fields.Float(compute='_amount_all',string='Amount Due')
    payment_ids = fields.One2many('account.payment', 'sale_id', string='Payments')
    # payment_lines = fields.One2many('sale.payment.line','sale_id','Payment Details')
    payment_count = fields.Integer(string='Payments', compute='_compute_payment_ids')
    discount_rate = fields.Float(related='corporate_id.discount_rate',string='Discount Rate',readonly=True)
    discount_program_id = fields.Many2one(related="corporate_id.discount_program_id", string="Discount Program",readonly=True, help="That programm will be applied when corporate is selected")
    adjusted_account_move = fields.Many2one('account.move','Discount Entry',readonly=True)
    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse',required=True, readonly=True,
                                   states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},default=_default_warehouse_id)
    project_id = fields.Many2one('account.analytic.account', 'Analytic Account', readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
                                 help="The analytic account related to a sales order.",default=_default_team_analytic_id, copy=False)

    sale_promotion_id = fields.Char()



    @api.model
    def create(self, vals):
        # if not vals.get('cash_amount') and not vals.get('bank_amount') and not vals.get('corporate_amount'):
        #     raise UserError(_("Please Complete the payment to confirm the order"))
        if vals['sale_type'] == "pos":
            if 'team_id' in vals:
                team_id = self.env['crm.team'].browse(vals['team_id'])
                sequence_code = team_id.sequence_id.code
            else:
                sequence_code = self.team_id.sequence_id.code
            vals['name'] = self.env['ir.sequence'].next_by_code(sequence_code) or 'New'
            res = super(SaleOrder, self).create(vals)
            if not res.payment_ids and not vals.get('cash_amount') and not vals.get('bank_amount1') and not vals.get('bank_amount2') and not vals.get('corporate_amount'):
            # if not res.payment_ids:
                raise UserError(_("You cannot proceed in the order without any payments."))

            total_amount = res.bank_amount1 + res.bank_amount2 + res.cash_amount + res.corporate_amount
            if total_amount + res.paid_amount > res.rounded_total:
                raise UserError(_("You cannot pay amount that exceed the amount due with %s.") % (total_amount + res.paid_amount - res.rounded_total))
            full_payment_items = ''
            total_payment = total_amount
            amount_needed = 0
            for line in res.order_line:
                categ = line.product_id.categ_id
                while categ:
                    if categ.full_payment:
                        amount_needed += round(line.price_subtotal)
                        full_payment_items += line.product_id.name + ', '
                        break;
                    categ = categ.parent_id
            for payment in res.payment_ids:
                total_payment += payment.amount
            print total_payment
            print amount_needed
            if total_payment < amount_needed:
                raise UserError(_("There are remaining payments with value: %s for items: %s.") % (amount_needed - total_payment,full_payment_items))
        else:
            vals['name'] = self.env['ir.sequence'].next_by_code('sale.order') or 'New'
            res = super(SaleOrder, self).create(vals)
        return res


    @api.onchange('partner_id')
    def onchange_partner_insurance_company_id(self):
        for order in self:
            if order.partner_id:
                medical = self.env['res.partner.lab'].sudo().search([('partner_id', '=', order.partner_id.id)], order="date desc", limit=1)
                if medical:
                    order.medical_id = medical.id
                else:
                    order.medical_id = False
            insurance_companies = ''
            for company in order.partner_id.insurance_company_ids:
                insurance_companies += str(company.id)
                insurance_companies += ','
            order.insurance_company_ids = insurance_companies


    @api.onchange('team_id')
    def onchange_sales_team_id(self):
        for order in self:
            order.warehouse_id = order.team_id.warehouse_id
            order.project_id = order.team_id.analytic_account_id


    def _compute_payment_ids(self):
        for order in self:
            order.update({
                'payment_count': len(order.payment_ids),
            })

    def get_insurance_company(self):
        for order in self:
            order.update({
                'insurance_company_ids': order.partner_id.insurance_company_ids,
            })


    @api.multi
    def action_confirm(self):
        for order in self:
            res = super(SaleOrder, self).action_confirm()
            if order.sale_type == 'pos':
                for line in order.order_line:
                    cat = self.env['product.category'].search([('name', '=', 'Lenses')])
                    if line.product_id.categ_id.parent_id == cat.id:
                        if not order.medical_id:
                            raise UserError(_("You Must Enter Medical To Add Lenses !!"))
                order.create_pos_invoice()
                for invoice in order.invoice_ids:
                    if invoice.type == 'out_invoice':
                        for payment in order.payment_ids:
                            payment.write({'invoice_ids': [(4, invoice.id, None)]})
                            payment.post()
                for picking in order.picking_ids:
                    if picking.state == 'assigned':
                        make_done = True
                        lens_cat = self.env['product.category'].search([('name', '=', 'Lenses')])
                        for move in picking.move_lines:
                            if move.product_id.categ_id.parent_id == lens_cat.id:
                                make_done = False
                        if make_done:
                            order._force_picking_done(picking)
            for picking_id in order.picking_ids:
                picking_id.write({
                        'sale_order_id': order.id,
                        })
        return res


    def _force_picking_done(self, picking):
        """Force picking in order to be set as done."""
        self.ensure_one()
        picking.action_confirm()
        picking.force_assign()
        self.set_pack_operation_lot(picking)
        if not any([(x.product_id.tracking != 'none') for x in picking.pack_operation_ids]):
            picking.action_done()

    def set_pack_operation_lot(self, picking=None):
        """Set Serial/Lot number in pack operations to mark the pack operation done."""
        # StockProductionLot = self.env['stock.production.lot']
        for order in self:
            for pack_operation in (picking or self.picking_id).pack_operation_ids:
                pack_lots = []
                qty_done = pack_operation.product_qty
                pack_operation.write({'pack_lot_ids': map(lambda x: (0, 0, x), pack_lots), 'qty_done': qty_done})

    @api.multi
    def register_payment(self):
        self.ensure_one()
        journal_obj = self.env['account.journal']
        for order in self:
            total_amount = order.bank_amount1 + order.bank_amount2 + order.cash_amount + order.corporate_amount
            if total_amount + order.paid_amount > order.rounded_total:
                raise UserError(_("You cannot pay amount that exceed the amount due with %s.") % (total_amount + order.paid_amount - order.rounded_total))
            if order.bank_amount1:
                journal = order.team_id.bank_journal_id
                if not journal:
                    raise UserError(_("Please define a bank journal for the sales team '%s'.") % (order.team_id.name or '',))
                order._prepare_pos_payment(journal,order.bank_amount1,order.bank_memo1)
            if order.bank_amount2:
                journal = order.team_id.bank_journal_id2
                if not journal:
                    raise UserError(_("Please define a bank journal for the sales team '%s'.") % (order.team_id.name or '',))
                order._prepare_pos_payment(journal,order.bank_amount2,order.bank_memo2)
            if order.cash_amount:
                journal = order.team_id.cash_journal_id
                if not journal:
                    raise UserError(_("Please define a cash journal for the sales team '%s'.") % (order.team_id.name or '',))
                order._prepare_pos_payment(journal,order.cash_amount,order.cash_memo)
            if order.corporate_amount:
                journal = journal_obj.search([('is_corporate', '=', True)], limit=1)
                if not journal:
                    raise UserError(_("Please define a Corporate journal."))
                payment = order._prepare_pos_payment(journal,order.corporate_amount,order.corporate_memo)
                if order.corporate_id.is_discount:
                    order.create_discount_journal_entry(payment)
            order.to_pay = False
            order.bank_amount1 = 0
            order.bank_amount2 = 0
            order.cash_amount = 0
            order.corporate_amount = 0
            order.cash_memo = ''
            order.bank_memo1 = ''
            order.bank_memo2 = ''
            order.corporate_memo = ''
            return True


    @api.multi
    def _prepare_pos_payment(self,journal,amount,memo):
        partner_id = self.partner_id.address_get(['invoice'])['invoice']
        payment_vals = ({
            'journal_id': journal.id,
            'payment_type':'inbound',
            'partner_type': 'customer',
            'payment_method_id':1,
            'amount':amount,
            'communication':memo,
            'partner_id': partner_id,
            'sale_id':self.id,
            'analytic_acc_id': self.project_id.id,
        })
        if journal.is_corporate:
            payment_vals.update({'corporate_id': self.corporate_id.id})
        for invoice in self.invoice_ids:
            if invoice.type == 'out_invoice':
                payment_vals.update({'invoice_ids': [(4, invoice.id, None)]})
        payment = self.env['account.payment'].create(payment_vals)
        if self.invoice_ids:
            payment.post()
        return payment


    @api.multi
    def action_view_account_payment(self):
        self.ensure_one()
        action = self.env.ref('account.action_account_payments')
        list_view_id = self.env.ref('account.view_account_payment_tree').id
        form_view_id = self.env.ref('account.view_account_payment_form').id
        result = {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'views': [[list_view_id, 'tree'], [form_view_id, 'form']],
            'target': action.target,
            'res_model': action.res_model,
        }
        if len(self.payment_ids) > 1:
            result['domain'] = "[('id','in',%s)]" % self.payment_ids.ids
        elif len(self.payment_ids) == 1:
            result['views'] = [(form_view_id, 'form')]
            result['res_id'] = self.payment_ids.id
        else:
            result = {'type': 'ir.actions.act_window_close'}
        return result


    @api.multi
    def create_discount_journal_entry(self, payment):
        discount_rate = self.discount_rate
        discount_program = self.corporate_id.discount_program_id
        journal_items = []
        discount_amount = 0
        current_date = date.today().strftime('%Y-%m-%d')

        if discount_program and discount_program.end_date >= current_date and discount_program.start_date <= current_date:
            for item in self.order_line:
                item_discount = 0
                categ = item.product_id.categ_id
                item_categories = []
                while categ:
                    item_categories.append(categ)
                    categ = categ.parent_id
                for category in discount_program.discount_category_ids:
                    if category.discount_category_id in item_categories:
                        item_discount = category.discount_percentage/100 * payment.amount
                        discount_amount += item_discount

                        journal_items.append((0, 0, {
                            'name': 'Discount (' + item.product_id.name +' / '+category.discount_category_id.name + ')',
                            'account_id': payment.journal_id.discount_account.id,
                            'partner_id': self.corporate_id.id,
                            'debit': item_discount,
                            'date': date.today(),
                        }))
        elif discount_rate:
            discount_amount = discount_rate / 100 * payment.amount
            journal_item_debit = {
                'name': 'Discount',
                'account_id': payment.journal_id.discount_account.id,
                'partner_id': self.corporate_id.id,
                'debit':discount_amount,
                'date': date.today(),
            }
            journal_items.append((0, 0, journal_item_debit))

        if journal_items:
            journal_item_credit = {
                'name': 'Discount',
                'account_id': self.corporate_id.corporate_account_id.id,
                'partner_id': self.corporate_id.id,
                'credit': discount_amount,
                'date':date.today(),
            }
            journal_items.append((0, 0, journal_item_credit))

            account_move_data = {
                'ref': self.name,
                'journal_id': payment.journal_id.id,
                'date': date.today(),
                'line_ids': [ line for line in journal_items]
            }
            move_id = self.env['account.move'].create(account_move_data)
            move_id.post()
            self.adjusted_account_move = move_id.id


    @api.multi
    def create_pos_invoice(self):
        self.ensure_one()
        for order in self:
            invoice_vals = order._prepare_pos_invoice()
            invoice = self.env['account.invoice'].create(invoice_vals)
            for line in order.order_line:
                invoice_line_vals = order._prepare_pos_invoice_line(line, invoice.id)
                self.env['account.invoice.line'].create(invoice_line_vals)
            invoice.compute_taxes()
            invoice.action_invoice_open()
            invoice.message_post_with_view('mail.message_origin_link',
                                           values={'self': invoice, 'origin': order},
                                           subtype_id=self.env.ref('mail.mt_note').id)
            # order.write({'status': 'invoiced','invoice_id':invoice.id})
            return invoice


    @api.multi
    def _prepare_pos_invoice(self):
        journal = self.env['account.journal'].search([('type', '=', 'sale'),('company_id', '=', self.company_id.id)],limit=1)
        if not journal:
            raise UserError(_("Please define a sale journal for the company '%s'.") %(self.company_id.name or '',))
        currency = (
            self.partner_id.property_product_pricelist.currency_id or
            self.company_id.currency_id
        )
        invoice_vals = ({
            'reference': False,
            # 'name': self.name,
            'type': 'out_invoice',
            'partner_id': self.partner_id.address_get(['invoice'])['invoice'],
            'account_id': self.partner_id.property_account_receivable_id.id,
            'currency_id': currency.id,
            'partner_shipping_id': self.partner_shipping_id.id,
            'journal_id': journal.id,
            'payment_term_id': self.payment_term_id.id,
            'fiscal_position_id': self.fiscal_position_id.id or self.partner_id.property_account_position_id.id,
            'team_id': self.team_id.id,
            'comment': self.note,
            'medical_id': self.medical_id.id,
            # 'date_invoice': self.date_deadline,
            'origin': self.name,
            'company_id': self.company_id.id,
            'user_id': self.user_id.id,
            'sale_order_id': self.id,
        })
        return invoice_vals


    @api.model
    def _prepare_pos_invoice_line(self, line, invoice_id):
        self.ensure_one()
        res = {}
        ir_property_obj = self.env['ir.property']

        account_id = False
        if line.product_id.id:
            account_id = line.product_id.property_account_income_id.id
        if not account_id:
            inc_acc = ir_property_obj.get('property_account_income_categ_id', 'product.category')
            account_id = self.fiscal_position_id.map_account(inc_acc).id if inc_acc else False
        if not account_id:
            raise UserError(
                _('There is no income account defined for this product: "%s". You may have to install a chart of account from Accounting app, settings menu.') %
                (line.product_id.name,))

        fpos = self.partner_id.property_account_position_id
        if fpos:
            account = fpos.map_account(account_id)

        if self.fiscal_position_id and line.product_id.taxes_id:
            tax_ids = self.fiscal_position_id.map_tax(line.product_id.taxes_id).ids
        else:
            tax_ids = line.product_id.taxes_id.ids
        invoice_line_vals = ({
            'name': line.product_id.name,
            'origin': self.name,
            'account_id': account_id,
            'invoice_id': invoice_id,
            'price_unit': line.price_unit,
            'quantity': line.product_uom_qty,
            'discount': line.discount,
            'uom_id': self.product_id.uom_id.id,
            'product_id': line.product_id.id,
            'sale_line_ids': [(6, 0, [line.id])],
            'invoice_line_tax_ids': [(6, 0, tax_ids)],
            'account_analytic_id': line.order_id.project_id.id or False,
            'analytic_tag_ids': [(6, 0, line.analytic_tag_ids.ids)],
        })
        return invoice_line_vals

    def show_payment(self):
        for order in self:
            if order.to_pay:
                order.to_pay = False
            else:
                order.to_pay = True


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    has_pricelist_discount = fields.Boolean('Apply Discount')

    @api.onchange('product_uom_qty', 'product_uom', 'route_id')
    def _onchange_product_id_check_availability(self):
        if not self.product_id or not self.product_uom_qty or not self.product_uom:
            self.product_packaging = False
            return {}
        if self.product_id.type == 'product':
            precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
            product_qty = self.product_uom._compute_quantity(self.product_uom_qty, self.product_id.uom_id)
            if float_compare(self.product_id.virtual_available, product_qty, precision_digits=precision) == -1:
                is_available = self._check_routing()
                # if not is_available:
                #     warning_mess = {
                #         'title': _('Not enough inventory!'),
                #         'message' : _('You plan to sell %s %s but you only have %s %s available!\nThe stock on hand is %s %s.') % \
                #             (self.product_uom_qty, self.product_uom.name, self.product_id.virtual_available, self.product_id.uom_id.name, self.product_id.qty_available, self.product_id.uom_id.name)
                #     }
                #     return {'warning': warning_mess}
        return {}

    @api.model
    def create(self, vals):
        res = super(SaleOrderLine, self).create(vals)
        product = res.product_id.with_context(
            lang= res.order_id.partner_id.lang,
            partner= res.order_id.partner_id.id,
            quantity= vals.get('product_uom_qty') or res.product_uom_qty,
            date= res.order_id.date_order,
            pricelist= res.order_id.pricelist_id.id,
            uom= res.product_uom.id
        )
        if res.order_id.pricelist_id and res.order_id.partner_id:
            vals['price_unit'] = res.product_id.lst_price
            res.price_unit = self.env['account.tax']._fix_tax_included_price(res._get_display_price(product), product.taxes_id, res.tax_id)
        return res

    @api.constrains('discount')
    @api.onchange('discount')
    def onchange_line_discount(self):
        for line in self:
            conf = self.env['ir.config_parameter']
            salesman_discount_limit = int(conf.get_param('pos_salesman_discount.salesman_discount_limit'))
            store_mgr_discount_limit = int(conf.get_param('pos_storemgr_discount.store_mgr_discount_limit'))
            apply_discount_limit = conf.get_param('pos_apply_discount.apply_discount_limit')
            if apply_discount_limit and not line.has_pricelist_discount and not line.order_id.sale_promotion_id:
                if self.env.user.has_group('eyefashion_sale.group_pos_store_manager'):
                    if line.discount > store_mgr_discount_limit:
                        raise UserError(_("You cannot exceed the discount limit %s with item %s.")% (store_mgr_discount_limit,line.product_id.name))
		elif self.env.user.has_group('eyefashion_sale.group_pos_salesman'):
                    if line.discount > salesman_discount_limit:
                        raise UserError(_("You cannot exceed the discount limit %s with item %s.")% (salesman_discount_limit,line.product_id.name))

    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        if not self.product_id:
            return {'domain': {'product_uom': []}}

        vals = {}
        domain = {'product_uom': [('category_id', '=', self.product_id.uom_id.category_id.id)]}
        if not self.product_uom or (self.product_id.uom_id.id != self.product_uom.id):
            vals['product_uom'] = self.product_id.uom_id
            vals['product_uom_qty'] = 1.0

        product = self.product_id.with_context(
            lang=self.order_id.partner_id.lang,
            partner=self.order_id.partner_id.id,
            quantity=vals.get('product_uom_qty') or self.product_uom_qty,
            date=self.order_id.date_order,
            pricelist=self.order_id.pricelist_id.id,
            uom=self.product_uom.id
        )

        name = product.name_get()[0][1]
        if product.description_sale:
            name += '\n' + product.description_sale
        vals['name'] = name

        self._compute_tax_id()

        if self.order_id.pricelist_id and self.order_id.partner_id:
            vals['price_unit'] = self.env['account.tax']._fix_tax_included_price(self._get_display_price(product), product.taxes_id, self.tax_id)
            if vals['price_unit'] != product.lst_price and self.order_id.sale_type == 'pos':
                vals['has_pricelist_discount'] = True
            else:
                vals['has_pricelist_discount'] = False

        self.update(vals)

        title = False
        message = False
        warning = {}
        if product.sale_line_warn != 'no-message':
            title = _("Warning for %s") % product.name
            message = product.sale_line_warn_msg
            warning['title'] = title
            warning['message'] = message
            if product.sale_line_warn == 'block':
                self.product_id = False
            return {'warning': warning}
        return {'domain': domain}
