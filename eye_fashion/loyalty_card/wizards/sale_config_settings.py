# -*- coding: utf-8 -*-
##############################################################################
#
# OdooBro - odoobro.contact@gmail.com
#
##############################################################################

from openerp import api, fields, models
import openerp.addons.decimal_precision as dp


class sale_configuration(models.TransientModel):
    _inherit = 'sale.config.settings'

    lc_point_exchange_rate = fields.Float(
        string='Point Exchange Rate',
        digits=dp.get_precision('Discount'),)

    lc_remind_point_rate = fields.Float(
        string='Remind Point Rate',
        digits=dp.get_precision('Discount'),)

    @api.multi
    def set_lc_point_exchange_rate(self):
        self.ensure_one()
        user = self.env['res.users'].browse(self.env.uid)
        user.company_id.lc_point_exchange_rate = self.lc_point_exchange_rate

    @api.model
    def get_default_lc_point_exchange_rate(self, fields):
        if 'lc_point_exchange_rate' not in fields:
            return {}
        user = self.env['res.users'].browse(self.env.uid)
        lc_point_exchange_rate = user.company_id.lc_point_exchange_rate or 0.0
        res = {'lc_point_exchange_rate': lc_point_exchange_rate}
        return res

    @api.multi
    def set_lc_remind_point_rate(self):
        self.ensure_one()
        user = self.env['res.users'].browse(self.env.uid)
        user.company_id.lc_remind_point_rate = self.lc_remind_point_rate

    @api.model
    def get_default_lc_remind_point_rate(self, fields):
        if 'lc_remind_point_rate' not in fields:
            return {}
        user = self.env['res.users'].browse(self.env.uid)
        lc_remind_point_rate = user.company_id.lc_remind_point_rate or 0.0
        res = {'lc_remind_point_rate': lc_remind_point_rate}
        return res
