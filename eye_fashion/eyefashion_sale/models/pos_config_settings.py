# -*- coding: utf-8 -*-

from odoo import api, fields, models

class PosConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    _name = 'pos.config.settings'

    apply_discount_limit = fields.Boolean('Apply Discount Limit',implied_group='product.group_product_variant')
    salesman_discount_limit = fields.Integer('Salesman Limit',implied_group='product.group_product_variant',)
    store_mgr_discount_limit = fields.Integer('Store Manager Limit',implied_group='product.group_product_variant',)

    @api.model
    def get_default_discount_limit(self, fields):
        conf = self.env['ir.config_parameter']
        return {
            'salesman_discount_limit': int(conf.get_param('pos_salesman_discount.salesman_discount_limit')),
            'store_mgr_discount_limit': int(conf.get_param('pos_storemgr_discount.store_mgr_discount_limit')),
            'apply_discount_limit': conf.get_param('pos_apply_discount.apply_discount_limit'),
        }

    @api.one
    def set_pos_discount_limit_values(self):
        conf = self.env['ir.config_parameter']
        conf.set_param('pos_salesman_discount.salesman_discount_limit', str(self.salesman_discount_limit))
        conf.set_param('pos_storemgr_discount.store_mgr_discount_limit', str(self.store_mgr_discount_limit))
        conf.set_param('pos_apply_discount.apply_discount_limit', self.apply_discount_limit)