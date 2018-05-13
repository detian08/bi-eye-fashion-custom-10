from openerp import fields,models,api

class product_template_inherit(models.Model):
    _inherit = 'product.product'


    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        recs = self.browse()
        stock_production_lot = self.env['stock.production.lot']

        if name:
            product_ids = [p.product_id.id for p in stock_production_lot.search([('name', '=', name)])]
            recs = self.search((args + [('id', 'in', product_ids)]),
                               limit=limit)
            if not recs:
                recs = self.search((args + [('name', 'ilike', name)]),
                                   limit=limit)

        if not recs:
            recs = self.search([('name', operator, name)] + args, limit=limit)
        return recs.name_get()
