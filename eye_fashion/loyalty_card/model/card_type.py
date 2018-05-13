# -*- coding: utf-8 -*-
##############################################################################
#
# OdooBro - odoobro.contact@gmail.com
#
##############################################################################

from openerp import api, fields, models
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _


class CardType(models.Model):
    _name = 'card.type'
    _description = 'Loyalty Card Type'
    _order = 'name'

    name = fields.Char(
        string='Type Name',
        required=True)
    basic_point = fields.Float(
        string='Basic Points',
        digits=dp.get_precision('Discount'))
    point_per_period = fields.Float(
        string='Points per Period',
        digits=dp.get_precision('Discount'))
    period_id = fields.Many2one(
        string='Period',
        comodel_name='card.period',
        required=1)
    categ_id = fields.Many2one(
        string='Category',
        comodel_name='card.category',
        required=1)
    discount = fields.Float(
        string='Discount (%)',
        digits=dp.get_precision('Discount'),
        required=1,
        default=0.0)
    seq = fields.Integer(
        string='Sequence')
    note = fields.Text(
        string='Note')
    issue_hard_card = fields.Boolean(
        string='Is Issue Hard Card?',
        default=False)
    active = fields.Boolean(
        string='Active?',
        default=True)

    _sql_constraints = [
        ('uniq_name_period_categ', "unique(name,period_id,categ_id)",
         _('Name/Period/Category value has been existed!')),
        ('uniq_seq_categ', "unique(seq,categ_id)",
         _('Sequence/Category value has been existed!'))]

    @api.multi
    def name_get(self):
        result = []
        for r in self:
            name = u"{} - {}".format(r.name, r.period_id.name)
            result.append((r.id, name))
        return result

    @api.multi
    def _get_next_type(self):
        self.ensure_one()
        args = [('categ_id', '=', self.categ_id.id),
                ('seq', '>', self.seq)]
        type = self.search(args, limit=1, order='seq')
        return type
