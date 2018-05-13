# -*- coding: utf-8 -*-
##############################################################################
#
# OdooBro - odoobro.contact@gmail.com
#
##############################################################################

from openerp import api, fields, models
from openerp.tools.translate import _


USAGE = [('all', 'All'),
         ('soft', 'Soft Card Only'),
         ('hard', 'Hard Card Only')]


class CardStage(models.Model):
    _name = 'card.stage'
    _description = 'Loyalty Card History'
    _rec_name = 'name'
    _order = 'sequence'

    name = fields.Char(
        string='Name')
    code = fields.Char(
        string='Code')
    sequence = fields.Integer(
        string='Sequence')
    usage = fields.Selection(USAGE,
        string='Usage')
    is_fold = fields.Boolean(
        string='Fold?',
        default=False)
    active = fields.Boolean(
        string='Active?',
        default=True)
    noupdate = fields.Boolean(
        string='No Manually Update?')
    noupdate_card = fields.Boolean(
        string='No Update on Card?')

    _sql_constraints = [
        ('uniq_sequence', "unique(sequence)",
         _('sequence value has been existed. Please choose another !'))]

    @api.multi
    def get_prev_state(self):
        self.ensure_one()
        args = [('sequence', '<', self.sequence)]
