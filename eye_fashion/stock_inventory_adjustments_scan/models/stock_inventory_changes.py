from openerp import fields,api,models,exceptions
from openerp.exceptions import UserError, Warning


class stock_inventory_inherit(models.Model):
    _inherit = 'stock.inventory'

    scanning_box = fields.Char(string="Scan")
    scanning_mode = fields.Selection([('internal_ref', 'By Internal reference'), ('lot_serial_no', 'By Lot/Serial Number')],string="Scanning Mode")

    @api.multi
    def synchronize_scanned_quantities(self):
        for rec in self:
            for val in rec.line_ids:
               val.product_qty =  val.scanned_quantity
        return True



    @api.multi
    @api.onchange('scanning_box')
    def get_scan_line_by_barcode(self):
        scan_list = []
        line_change_list = []
        scan_exist = False
        for rec in self:
            if rec.scanning_box :
                scan_lines = rec.line_ids
                scan_list = rec.line_ids
                if rec.scanning_mode == False:
                    raise Warning(str("You should select scanning mode first !!"))
                elif rec.scanning_mode == 'internal_ref':
                    get_product = rec.env['product.product'].search([('default_code', '=', rec.scanning_box)])
                    if get_product:
                        if get_product.tracking != 'none':
                            raise Warning(str("This product is tracked by Lot/Serial Number"))
                        elif get_product.tracking == 'none':
                            for line in scan_list:
                                if line.product_id.id == get_product.id:
                                    if type(line.id) == int:
                                        print"here1"
                                        scanned_quantity = line.scanned_quantity + 1
                                        line_change_list.append([1, line.id, {'scanned_quantity': scanned_quantity}])
                                    else:

                                        scanned_quantity = line.scanned_quantity + 1

                                        line_change_list.append([2, line.id])
                                        line_change_list.append([0, 0, {
                                            'product_id': get_product.id,
                                            'product_uom_id': get_product.uom_id.id,
                                            'location_id': rec.location_id.id,
                                            'package_id': rec.package_id.id,
                                            'partner_id': rec.partner_id.id,
                                            'theoretical_qty': 0,
                                            'product_qty': 0,
                                            'state': rec.state,
                                            'scanned_quantity': scanned_quantity,
                                        }])
                                    scan_exist = True

                                else:
                                    print"here3"

                                    line_change_list.append([4, line.id])
                            if scan_exist == False:
                                line_change_list.append([0, 0, {
                                                'product_id': get_product.id,
                                                'product_uom_id': get_product.uom_id.id,
                                                'location_id': rec.location_id.id,
                                                'package_id': rec.package_id.id,
                                                'partner_id': rec.partner_id.id,
                                                'theoretical_qty': 0,
                                                'product_qty': 0,
                                                'state': rec.state,
                                                'scanned_quantity': 1,
                                            }])
                    else:
                        raise Warning(str("No product with this internal reference found !!"))
                elif rec.scanning_mode == 'lot_serial_no':
                    get_product = rec.env['stock.production.lot'].search([('name', '=', rec.scanning_box)])
                    if get_product:
                        for line in scan_list:
                            if line.product_id.id == get_product.product_id.id and line.prod_lot_id.id == get_product.id:
                                if type(line.id) == int:
                                    scanned_quantity = line.scanned_quantity + 1
                                    line_change_list.append([1, line.id, {'scanned_quantity': scanned_quantity}])
                                else:
                                    scanned_quantity = line.scanned_quantity + 1
                                    line_change_list.append([2, line.id])
                                    line_change_list.append([0, 0, {
                                        'product_id': get_product.product_id.id,
                                        'product_uom_id': get_product.product_id.uom_id.id,
                                        'location_id': rec.location_id.id,
                                        'prod_lot_id': get_product.id,
                                        'package_id': rec.package_id.id,
                                        'partner_id': rec.partner_id.id,
                                        'theoretical_qty': 0,
                                        'product_qty': 0,
                                        'state': rec.state,
                                        'scanned_quantity': scanned_quantity,
                                    }])
                                scan_exist = True
                            else:
                                line_change_list.append([4, line.id])

                        if scan_exist == False:
                            line_change_list.append([0, 0, {
                                'product_id': get_product.product_id.id,
                                'product_uom_id': get_product.product_id.uom_id.id,
                                'location_id': rec.location_id.id,
                                'prod_lot_id': get_product.id,
                                'package_id': rec.package_id.id,
                                'partner_id': rec.partner_id.id,
                                'theoretical_qty': 0,
                                'product_qty': 0,
                                'state': rec.state,
                                'scanned_quantity': 1,
                            }])
                    else:
                        raise Warning(str("No product with this Lot/Serial Number found !!"))

                rec.scanning_box = ''
                rec.line_ids = line_change_list
