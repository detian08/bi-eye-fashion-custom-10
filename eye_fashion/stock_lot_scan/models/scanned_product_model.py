from openerp import fields, models, api, exceptions


class scanned_products_lines(models.Model):
    _name = 'scan.product'
    _rec_name = 'product_id'
    _description = 'Scanned Products'

    product_id = fields.Many2one('product.product', string="Product")
    lot_no = fields.Char(string="Serial No.")
    product_uom_qty = fields.Float(string="Qty")
    stock_picking_id = fields.Many2one('stock.picking', string="Stock Picking")
    lot_name = fields.Char(string='Lot Name', help="Unique Serial Number")
    expiration_date = fields.Date(string="Expiration Date")
    pick_Typ_code = fields.Selection(related='stock_picking_id.pickin_Typ_code', string="Code")



class temp_products_lines(models.Model):
    _name = 'temp.product'
    _rec_name = 'product_id'
    _description = 'Temp Scanned Products'

    product_id = fields.Many2one('product.product', string="Product")
    lot_no = fields.Char(string="Serial No.")
    product_uom_qty = fields.Float(string="Qty")
    stock_picking_id = fields.Many2one('stock.picking', string="Stock Picking")
    lot_name = fields.Char(string='Lot Name', help="Unique Serial Number")
    expiration_date = fields.Date(string="Expiration Date")
    pick_Typ_code = fields.Selection(related='stock_picking_id.pickin_Typ_code', string="Code")
