# -*- coding: utf-8 -*-
##############################################################################
#
# OdooBro - odoobro.contact@gmail.com
#
##############################################################################

from openerp import api, fields, models
from openerp.tools.translate import _


class CardCategory(models.Model):
    _name = 'card.category'
    _description = 'Loyalty Card Category'
    _order = 'name'

    name = fields.Char(
        string='Name',
        required=True)
    type_ids = fields.One2many(
        string='Types',
        comodel_name='card.type',
        inverse_name='categ_id')

    _sql_constraints = [
        ('uniq_name', "unique(name)",
         _('Name value has been existed. Please choose another !'))]
