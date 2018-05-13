from __future__ import division
from odoo import models, fields, api
import time
from datetime import datetime, timedelta


class Invoice(models.Model):
    _inherit = 'account.invoice'
    date_time_invoice = fields.Datetime(string='Date', default=lambda self: fields.Datetime.now(), required=True)
    current_rate = fields.Float(string='Current Rate')
    bool_new_rate = fields.Boolean(string='New Rate')

    @api.multi
    @api.onchange('date_invoice')
    def onchange_date_invoice(self):
        if self.date_invoice:
            self.date_time_invoice = self.date_invoice + " " + time.strftime("%H:%M:%S")
        else:
            self.date_time_invoice = fields.Datetime.now()

    @api.multi
    @api.onchange('currency_id')
    def onchange_currency(self):
        default_currency = self.env['res.users'].sudo().browse(self.env.uid).company_id.currency_id.id
        if self.currency_id:
            if self.currency_id.id != default_currency:
                self.bool_new_rate = True
                if self.origin:
                    purchase_id = self.env['purchase.order'].sudo().search([('name', '=', self.origin)])
                    if purchase_id:
                        self.current_rate = purchase_id.current_rate
                    else:
                        self.current_rate = self.currency_id.rate
            else:
                self.bool_new_rate = False
                self.current_rate = 0.0

    @api.multi
    def action_invoice_open(self):
        res = super(Invoice, self).action_invoice_open()
        default_currency = self.env['res.users'].sudo().browse(self.env.uid).company_id.currency_id.id
        if self.currency_id.id != default_currency:
            if self.current_rate != self.currency_id.rate and self.current_rate > 0.00:
                date_invoice = datetime.strptime(self.date_time_invoice, "%Y-%m-%d %H:%M:%S")
                currency_date = date_invoice - timedelta(seconds=1)
                self.env['res.currency.rate'].create(
                    {'name': str(currency_date), 'currency_id': self.currency_id.id, 'rate': 1/self.current_rate})
        return res


Invoice()
