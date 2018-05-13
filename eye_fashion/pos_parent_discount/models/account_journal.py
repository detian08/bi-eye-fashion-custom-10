# -*- coding: utf-8 -*-

from odoo import models, fields

class AccountJournal(models.Model):
    _inherit = 'account.journal'

    is_corporate = fields.Boolean('Corporate',default=False)
    discount_account = fields.Many2one('account.account','Discount Account')