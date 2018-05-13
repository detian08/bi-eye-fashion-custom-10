# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
from odoo.tools import float_is_zero
from odoo.exceptions import UserError
from odoo.http import request
import odoo.addons.decimal_precision as dp

from datetime import datetime, date

class PosSession(models.Model):
    _inherit = "pos.session"


    def _confirm_orders(self, corporate_journal):
        for session in self:
            company_id = session.config_id.journal_id.company_id.id
            orders = session.order_ids.filtered(lambda order: order.state == 'paid')
            journal_id = self.env['ir.config_parameter'].sudo().get_param(
                'pos.closing.journal_id_%s' % company_id, default=session.config_id.journal_id.id)
            move = self.env['pos.order'].with_context(force_company=company_id)._create_account_move(session.start_at, session.name, int(journal_id), company_id)
            orders.with_context(force_company=company_id)._create_account_move_line(session, move)
            for order in session.order_ids.filtered(lambda o: o.state != 'done'):
                if order.state not in ('paid', 'invoiced'):
                    raise UserError(_("You cannot confirm all orders of this session, because they have not the 'paid' status"))
                order.action_pos_order_done()
            for order in session.order_ids:
                for payment in order.statement_ids:
                    if payment.journal_id == corporate_journal:
                        if order.partner_id.parent_id.is_discount:
                            session.create_discount_journal_entry(order,payment)

    @api.multi
    def create_discount_journal_entry(self, order, payment):
        discount_rate = order.partner_id.parent_id.discount_rate
        discount_amount = discount_rate/100 * payment.amount
        journal_item_credit = {
            'name': 'Discount',
            'account_id': payment.journal_id.default_debit_account_id.id,
            'partner_id': order.partner_id.id,
            'credit': discount_amount,
            'date':date.today(),
        }
        journal_item_debit = {
            'name': 'Discount',
            'account_id': payment.journal_id.discount_account.id,
            'partner_id': order.partner_id.id,
            'debit':discount_amount,
            'date': date.today(),
        }
        account_move_data = {
            'ref': order.name,
            'journal_id': payment.journal_id.id,
            'date': date.today(),
            'line_ids': [(0, 0, journal_item_credit),(0,0,journal_item_debit)]
        }
        move_id = self.env['account.move'].create(account_move_data)
        move_id.post()
        order.adj_account_move = move_id.id



    @api.multi
    def action_pos_session_close(self):
        # Close CashBox
        for session in self:
            corporate_journal = ''
            company_id = session.config_id.company_id.id
            ctx = dict(self.env.context, force_company=company_id, company_id=company_id)
            for st in session.statement_ids:
                if st.journal_id.is_corporate:
                    corporate_journal = st.journal_id
                if abs(st.difference) > st.journal_id.amount_authorized_diff:
                    # The pos manager can close statements with maximums.
                    if not self.env['ir.model.access'].check_groups("point_of_sale.group_pos_manager"):
                        raise UserError(_("Your ending balance is too different from the theoretical cash closing (%.2f), the maximum allowed is: %.2f. You can contact your manager to force it.") % (st.difference, st.journal_id.amount_authorized_diff))
                if (st.journal_id.type not in ['bank', 'cash']):
                    raise UserError(_("The type of the journal for your payment method should be bank or cash "))
                st.with_context(ctx).sudo().button_confirm_bank()
        self.with_context(ctx)._confirm_orders(corporate_journal)
        self.write({'state': 'closed'})
        return {
            'type': 'ir.actions.client',
            'name': 'Point of Sale Menu',
            'tag': 'reload',
            'params': {'menu_id': self.env.ref('point_of_sale.menu_point_root').id},
        }
