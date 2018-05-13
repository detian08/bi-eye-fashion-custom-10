# -*- coding: utf-8 -*-

from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_discount = fields.Boolean('Discount',default=True)
    discount_rate = fields.Float('Discount Rate (%)')