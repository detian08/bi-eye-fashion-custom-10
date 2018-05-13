# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
from odoo.tools import float_is_zero
from odoo.exceptions import UserError
from odoo.http import request
import odoo.addons.decimal_precision as dp

from datetime import datetime, date

class PosOrder(models.Model):
    _inherit = "pos.order"

    adj_account_move = fields.Many2one('account.move','Discount Entry')