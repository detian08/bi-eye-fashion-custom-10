from openerp import fields, models, api, exceptions


class stock_move_inherit(models.Model):
    _inherit = 'stock.move'

    check_is_scanned = fields.Boolean(string="Is Scanned Product")
    lot_name = fields.Char(string='Serial Number', help="Unique Serial Number")
    expiration_date = fields.Date(string="Expiration Date")
