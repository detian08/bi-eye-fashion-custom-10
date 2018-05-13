from __future__ import division
from odoo import models, fields, api
from datetime import datetime, timedelta


class Purchase(models.Model):
    _inherit = 'purchase.order'

    current_rate = fields.Float(string='Current Rate')
    bool_new_rate = fields.Boolean(string='New Rate')

    @api.multi
    @api.onchange('currency_id')
    def onchange_currency(self):
        default_currency = self.env['res.users'].sudo().browse(self.env.uid).company_id.currency_id.id
        if self.currency_id:
            if self.currency_id.id != default_currency:
                self.bool_new_rate = True
                self.current_rate = self.currency_id.rate
            else:
                self.bool_new_rate = False
                self.current_rate = 0.0

    @api.multi
    def button_confirm(self):
        res = super(Purchase, self).button_confirm()
        if res == True:
            default_currency = self.env['res.users'].sudo().browse(self.env.uid).company_id.currency_id.id
            if self.currency_id.id != default_currency:
                if self.current_rate != self.currency_id.rate and self.current_rate > 0.0:
                    date_order = datetime.strptime(self.date_order, "%Y-%m-%d %H:%M:%S")
                    currency_date = date_order - timedelta(seconds=1)
                    self.env['res.currency.rate'].create(
                        {'name': str(currency_date), 'currency_id': self.currency_id.id, 'rate': 1/self.current_rate})
        return res


Purchase()
