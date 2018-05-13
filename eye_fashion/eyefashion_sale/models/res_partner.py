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