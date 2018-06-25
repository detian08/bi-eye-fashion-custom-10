# -*- coding: utf-8 -*-

from odoo.osv import expression
from odoo import models, fields, api

class PosCategoryDiscount(models.Model):
    _name = "pos.category.discount"
    discount_percentage = fields.Float(string="Discount Percentage", help="The default discount percentage")
    discount_category_id = fields.Many2one("product.category", string="Product Category", help="The category used to model the discount")
    discount_program_id = fields.Many2one("pos.discount.program", string="Discount Program")


class PosDiscountProgram(models.Model):
    _name = "pos.discount.program"
    _description = "Discount Program"

    name = fields.Char(string="Name", required=True)
    start_date = fields.Date('Start Date',required=True)
    end_date = fields.Date('Expiration Date',required=True)
    discount_category_ids = fields.One2many("pos.category.discount", "discount_program_id", string='Discount Category')


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_discount = fields.Boolean('Discount',default=False)
    discount_rate = fields.Float('Discount Rate (%)')
    discount_program_id = fields.Many2one("pos.discount.program", string="Discount Program", help="That programm will be applied when corporate is selected")
    start_date = fields.Date(related='discount_program_id.start_date',string='Start Date',readonly=True,store=True)
    end_date = fields.Date(related='discount_program_id.end_date',string='Expiration',readonly=True,store=True)
    corporate_account_id = fields.Many2one('account.account','Corporate Account')
    has_eye_card = fields.Boolean('Has Eye Card ?')
    eye_card_no = fields.Char('Card No.')
    property_product_pricelist = fields.Many2one(
        'product.pricelist', 'Sale Pricelist', compute='_compute_product_pricelist',
        inverse="_inverse_product_pricelist", company_dependent=False)


    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('mobile', 'ilike', name + '%'), ('name', operator, name)]
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = ['&', '!'] + domain[1:]
        accounts = self.search(domain + args, limit=limit)
        return accounts.name_get()


    # @api.multi
    # @api.depends('country_id', 'has_eye_card')
    # def _compute_product_pricelist(self):
    #     for p in self:
    #         if p.has_eye_card:
    #             pricelist = self.env['product.pricelist'].search([('is_eye_card', '=', True)])
    #             if pricelist:
    #                 p.property_product_pricelist = pricelist[0].id
    #             else:
    #                 pricelist = {
    #                                 'name': 'Eye Fashion Card PriceList',
    #                                 'is_eye_card': True,
    #                 }
    #                 pricelist_id = self.env['product.pricelist'].create(pricelist)
    #                 p.property_product_pricelist = pricelist_id
    #         else:
    #             if not isinstance(p.id, models.NewId):  # if not onchange
    #                 p.property_product_pricelist = self.env['product.pricelist']._get_partner_pricelist(p.id)