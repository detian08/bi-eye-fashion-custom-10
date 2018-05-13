from openerp import fields, models, api, exceptions


class stock_production_lot_inherit(models.Model):
    _inherit = 'stock.production.lot'

    @api.one
    @api.constrains('name')
    def _check_unique_name_constraint(self):
        if not self.name:
            return True
        elif len(self.search([('name', '=', self.name)])) > 1:
            raise ValueError("Lot Number already exists and violates unique field constraint")



    @api.multi
    @api.onchange('expiration_date')
    def get_exp_date(self):
        date = self.expiration_date
        self.life_date = date