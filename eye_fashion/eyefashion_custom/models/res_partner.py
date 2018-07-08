# -*- coding: utf-8 -*-

from odoo.osv import expression
from odoo import models, fields, api

class ResPartnerInherit(models.Model):
    _inherit = 'res.partner'

    has_eye_card = fields.Boolean('Has Eye Card ?')
    eye_card_no = fields.Char('Card No.')
    property_product_pricelist = fields.Many2one(
        'product.pricelist', 'Sale Pricelist', compute='_compute_product_pricelist',
        inverse="_inverse_product_pricelist", company_dependent=False)


    @api.multi
    @api.depends('country_id', 'has_eye_card')
    def _compute_product_pricelist(self):
        for p in self:
            if p.has_eye_card:
                pricelist = self.env['product.pricelist'].search([('is_eye_card', '=', True)])
                if pricelist:
                    p.property_product_pricelist = pricelist[0].id
                else:
                    pricelist = {
                                    'name': 'Eye Fashion Card PriceList',
                                    'is_eye_card': True,
                    }
                    pricelist_id = self.env['product.pricelist'].create(pricelist)
                    p.property_product_pricelist = pricelist_id
            else:
                if not isinstance(p.id, models.NewId):  # if not onchange
                    p.property_product_pricelist = self.env['product.pricelist']._get_partner_pricelist(p.id)