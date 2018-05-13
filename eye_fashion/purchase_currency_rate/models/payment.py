from __future__ import division
from odoo import fields, models, api
import time
from datetime import datetime, timedelta


class Payment(models.Model):
    _inherit = 'account.payment'
    date_time_payment = fields.Datetime(string='Date', default=lambda self: fields.Datetime.now(), required=True)
    current_rate = fields.Float(string='Current Rate')
    bool_new_rate = fields.Boolean(string='New Rate')

    @api.multi
    @api.onchange('date_invoice')
    def onchange_date_invoice(self):
        if self.payment_date:
            self.date_time_payment = self.payment_date + " " + time.strftime("%H:%M:%S")
        else:
            self.date_time_payment = fields.Datetime.now()

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
    def post(self):
        res = super(Payment, self).post()
        default_currency = self.env['res.users'].sudo().browse(self.env.uid).company_id.currency_id.id
        if self.currency_id.id != default_currency:
            if self.current_rate != self.currency_id.rate and self.current_rate > 0.00:
                date_payment = datetime.strptime(self.date_time_payment, "%Y-%m-%d %H:%M:%S")
                currency_date = date_payment - timedelta(seconds=1)
                self.env['res.currency.rate'].create(
                    {'name': str(currency_date), 'currency_id': self.currency_id.id, 'rate': 1/self.current_rate})
        return res


Payment()
