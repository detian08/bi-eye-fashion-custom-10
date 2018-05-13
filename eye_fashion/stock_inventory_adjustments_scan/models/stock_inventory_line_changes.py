from openerp import fields,api,models,exceptions


class stock_inventory_line_inherit(models.Model):
    _inherit = 'stock.inventory.line'

    scanned_quantity = fields.Float(string="Scanned Quantity")

