# -*- coding: utf-8 -*-

from odoo import models, fields

class pos_config(models.Model):
    _inherit = 'pos.config'

    direct_delivery = fields.Boolean('Force Direct Delivery', default=True)