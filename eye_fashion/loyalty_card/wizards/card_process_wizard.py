# -*- coding: utf-8 -*-
##############################################################################
#
# OdooBro - odoobro.contact@gmail.com
#
##############################################################################

from openerp import api, fields, models


class CardProcessWizard(models.TransientModel):
    _name = 'card.process.wizard'

    card_ids = fields.Many2many(
        string="Cards",
        comodel_name="card.card")
    state_id = fields.Many2one(
        string='Status',
        comodel_name='card.stage',
        required=1)
    is_force = fields.Boolean(
        string='Is Force?')

    @api.model
    def default_get(self, fields_list):
        res = super(CardProcessWizard, self).default_get(fields_list)
        card_ids = self._context.get('card_ids', [])
        res.update({'card_ids': [(6, 0, card_ids)]})
        return res

    @api.multi
    def button_proceed(self):
        self.ensure_one()
        cards = self.card_ids
        if not self.is_force:
            cards = self.card_ids.filtered(lambda r: not r.state_id.noupdate)
        if cards and self.state_id.usage == 'hard':
            cards = cards.filtered('issue_hard_card')
        cards.write({'state_id': self.state_id.id})
        return {
            'name': 'Cards',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'card.card',
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', cards.ids)]
        }
        return True

