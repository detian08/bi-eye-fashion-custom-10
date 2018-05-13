from openerp import fields, models, api, exceptions
from openerp.exceptions import UserError, Warning


class sale_order_inherit(models.Model):
    _inherit = 'sale.order'

    ean13 = fields.Char(string="Scan")

    @api.multi
    @api.onchange('ean13')
    def get_line_by_barcode(self):
        if self.ean13 != '':
            list = []
            lot_obj = self.env['stock.production.lot'].search([('name', '=', self.ean13)])
            olines = self.order_line
            exist = False
            for val in olines:
                list.append([0, 0, {
                    'product_id': val.product_id.id,
                    'name': val.product_id.name,
                    'product_uom': val.product_id.uom_id.id,
                    'product_uom_qty': val.product_uom_qty,
                    'price_unit': val.product_id.lst_price,
                    'tax_id': val.product_id.taxes_id
                }])

            for line in list:
                if line[2]['product_id'] == lot_obj.product_id.id:
                    line[2]['product_uom_qty'] = line[2]['product_uom_qty'] + 1
                    exist = True

            if not exist:
                if lot_obj:
                    list.append([0, 0,
                                 {
                                     'product_id': lot_obj.product_id.id,
                                     'name': lot_obj.product_id.name,
                                     'product_uom_qty': 1,
                                     'product_uom': lot_obj.product_id.uom_id.id,
                                     'price_unit': lot_obj.product_id.lst_price,
                                     'tax_id': lot_obj.product_id.taxes_id
                                 }])

            self.ean13 = ''
            self.order_line = list
