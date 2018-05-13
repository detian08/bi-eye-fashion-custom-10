# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools import float_compare

class ProductBrand(models.Model):
    _name = 'product.brand'

    name = fields.Char('Brand Name', required=True, translate=True)
    description = fields.Text('Description', translate=True)
    logo = fields.Binary('Logo File')
    product_ids = fields.One2many('product.template', 'product_brand_id', string='Brand Products')
    products_count = fields.Integer(string='Number of products', compute='_get_products_count')

    @api.one
    @api.depends('product_ids')
    def _get_products_count(self):
        self.products_count = len(self.product_ids)

class ProductTemplate(models.Model):
    _inherit = "product.template"

    product_brand_id = fields.Many2one('product.brand', string='Brand', help='Select a brand for this product')
    v_type = fields.Char('V Type')
    photo_x = fields.Char('Photo X')
    coating = fields.Char('Coating')
    index = fields.Char('Index')
    avl = fields.Char('AVL')
    design = fields.Char('Design')
    range_power = fields.Char('Range Power')


class ProductCategory(models.Model):
    _inherit = "product.category"

    need_medical = fields.Boolean('Need Medical',default=False)
    full_payment = fields.Boolean('Full Payment',default=False)