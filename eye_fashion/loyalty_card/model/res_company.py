# -*- coding: utf-8 -*-
##############################################################################
#
# OdooBro - odoobro.contact@gmail.com
#
##############################################################################

from openerp import api, fields, models
import openerp.addons.decimal_precision as dp


class ResCompany(models.Model):
    _inherit = 'res.company'

    lc_point_exchange_rate = fields.Float(
        string='Point Exchange Rate',
        digits=dp.get_precision('Discount'),)

    lc_remind_point_rate = fields.Float(
        string='Remind Point Rate',
        digits=dp.get_precision('Discount'),)
