from odoo import models


class AccountMove(models.Model):
    _inherit = 'account.move'

    def have_lines_analytic(self, lines):
        bool_check = False
        for record in lines:
            if record.analytic_account_id:
                bool_check = True
        return bool_check

    def have_lines_amount(self, lines):
        bool_check = False
        for record in lines:
            if record.amount_currency:
                bool_check = True
        return bool_check


AccountMove()
