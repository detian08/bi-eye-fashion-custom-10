# -*- coding: utf-8 -*-
##############################################################################
#
# OdooBro - odoobro.contact@gmail.com
#
##############################################################################

from openerp import api, fields, models


class CreateCardsWizard(models.TransientModel):
    _name = 'create.card.wizard'

    quantity = fields.Integer(
          string="Quantity",
          required=True)
    type_id = fields.Many2one(
        string='Type',
        comodel_name='card.type',
        required=1)

    @api.multi
    def button_create(self):
        self.ensure_one()
        cards = Card = self.env['card.card']
        if self.quantity > 0:
            for _ in range(self.quantity):
                vals = {
                    'type_id': self.type_id.id
                }
                cards |= Card.create(vals)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'card.card',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'target': 'current',
            'context': {},
            'domain': [('id', 'in', cards.ids)],
        }
        return True
