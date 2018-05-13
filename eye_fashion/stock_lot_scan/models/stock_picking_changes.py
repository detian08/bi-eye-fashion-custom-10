from openerp import fields, models, api, exceptions
from openerp.exceptions import UserError, Warning
import datetime


class stock_picking_inherit(models.Model):
    _inherit = 'stock.picking'

    ean13 = fields.Char(string="Scan")
    ean132 = fields.Char(string="Scan")
    supplier_ean13 = fields.Char(string="Scan")
    supplier_ean132 = fields.Char(string="Scan")
    scan_products_ids = fields.One2many('scan.product', 'stock_picking_id', string="Scanned Products")
    temp_products_ids = fields.One2many('temp.product','stock_picking_id',string="Temp. Products")
    pickin_Typ_code = fields.Selection(related='picking_type_id.code', string="Code")
    type_of_scaning = fields.Selection(
        [('first_group', 'First Group'), ('second_group', 'Second Group'), ('third_group', 'Third Group')])

    @api.multi
    def synchronize_scan(self):
        for rec in self:
            if rec.pickin_Typ_code != 'incoming':
                rec.action_confirm_out()
            elif rec.pickin_Typ_code == 'incoming':
                rec.action_confirm_in()
            for line in rec.pack_operation_product_ids:
                for li in rec.scan_products_ids:
                    if line.product_id.id == li.product_id.id:
                        lot_id = rec.env['stock.production.lot'].search([('name', '=', li.lot_no)])
                        vals = {
                            'qty': li.product_uom_qty,
                            'lot_id': lot_id.id,
                            'lot_name': lot_id.name,
                            'operation_id': line.id,
                        }
                        stk_pack_id = rec.env['stock.pack.operation.lot'].search(
                            [('lot_id', '=', lot_id.id), ('operation_id', '=', line.id)])
                        print(str(stk_pack_id))
                        if stk_pack_id:
                            if stk_pack_id.qty < li.product_uom_qty:
                                stk_pack_id.write({'qty': li.product_uom_qty})
                        elif not stk_pack_id:
                            rec.env['stock.pack.operation.lot'].create(vals)
                    line.write({'qty_done': line.product_qty})

    @api.multi
    def action_confirm_out(self):
        product_list = []
        temp_list = []
        list = []
        for rec in self:
            for product in rec.pack_operation_product_ids:
                if product.product_id.id not in product_list:
                    product_list.append(product.product_id.id)

            # synchronize temp lines with scanned lines
            for line in rec.scan_products_ids:
                for li in rec.temp_products_ids:
                    if line.product_id.id == li.product_id.id:
                        li.write({'product_uom_qty': 0})


            for line in rec.scan_products_ids:
                for li in rec.temp_products_ids:
                    if line.product_id.id == li.product_id.id:
                        li.write({'product_uom_qty': li.product_uom_qty + line.product_uom_qty})

            for line in rec.scan_products_ids:
                temp_list.append(line.product_id.id)
            for li in rec.temp_products_ids:
                if li.product_id.id not in temp_list:
                    li.write({'product_uom_qty': 0})


            #/////////////////////////////////////////////////


            for line in rec.temp_products_ids:
                if line.product_id.id not in product_list:
                    list.append([0, 0, {
                        'product_id': line.product_id.id,
                        'name': line.product_id.name,
                        'product_qty': line.product_uom_qty,
                        'product_uom_id': line.product_id.uom_id.id,
                        'location_dest_id': self.location_dest_id.id,
                        'location_id': rec.location_id.id,
                    }])


                elif line.product_id.id in product_list:
                    for li in rec.pack_operation_product_ids:
                        li.write({'product_qty': 0})

            for line in rec.temp_products_ids:
                if line.product_id.id in product_list:
                    for li in rec.pack_operation_product_ids:
                        if li.product_id.id == line.product_id.id:
                            li.write({'product_qty': li.product_qty + line.product_uom_qty})

            rec.pack_operation_product_ids = list

    @api.multi
    def action_confirm_in(self):
        product_list = []
        list = []
        temp_list = []
        for rec in self:
            for product in rec.pack_operation_product_ids:
                product_list.append(product.product_id.id)

            # synchronize temp lines with scanned lines
            for line in rec.scan_products_ids:
                for li in rec.temp_products_ids:
                    if line.product_id.id == li.product_id.id:
                        li.write({'product_uom_qty': 0})

            for line in rec.scan_products_ids:
                for li in rec.temp_products_ids:
                    if line.product_id.id == li.product_id.id:
                        li.write({'product_uom_qty': li.product_uom_qty + line.product_uom_qty})

            for line in rec.scan_products_ids:
                temp_list.append(line.product_id.id)

            for li in rec.temp_products_ids:
                if li.product_id.id not in temp_list:
                    print "dflmfdkmfkdmfdkmfd"
                    li.write({'product_uom_qty': 0})

                # /////////////////////////////////////////////////

            for line in rec.temp_products_ids:
                if line.product_id.id not in product_list:
                    list.append([0, 0, {
                        'product_id': line.product_id.id,
                        'name': line.product_id.name,
                        'product_qty': line.product_uom_qty,
                        'product_uom_id': line.product_id.uom_id.id,
                        'location_dest_id': self.location_dest_id.id,
                        'location_id': rec.location_id.id,
                    }])


                elif line.product_id.id in product_list:
                    for li in rec.pack_operation_product_ids:
                        li.write({'product_qty': 0})

            for line in rec.temp_products_ids:
                if line.product_id.id in product_list:
                    for li in rec.pack_operation_product_ids:
                        if li.product_id.id == line.product_id.id:
                            li.write({'product_qty': li.product_qty + line.product_uom_qty})

            rec.pack_operation_product_ids = list

    # here we fill the lines of one2many field of scanned products in case of picking type code is not equal supplier
    @api.multi
    @api.onchange('ean132')
    def get_scan_line_by_barcode(self):
        for rec in self:
            pkin_typ = rec.picking_type_id
            mv_typ = rec.move_type
            priority_id = rec.priority
            company_id = rec.company_id
            location_id = rec.location_id
            picking_type_code = rec.picking_type_code
            typ_of_scan = rec.type_of_scaning

            if rec.ean132 != '':
                scan_lot_obj = rec.env['stock.production.lot'].search([('name', '=', rec.ean132)])
                scan_lines = rec.scan_products_ids
                temp_lines = rec.temp_products_ids
                scan_list = []
                temp_list = []
                scan_exist = False
                temp_exist = False
                for val in scan_lines:
                    scan_list.append([0, 0, {
                        'product_id': val.product_id.id,
                        'product_uom_qty': val.product_uom_qty,
                        'lot_no': val.lot_no,
                        'lot_name': val.lot_name,
                        'expiration_date': val.expiration_date,
                    }])

                # temp list
                for val in temp_lines:

                    temp_list.append([0, 0, {
                        'product_id': val.product_id.id,
                        'product_uom_qty': val.product_uom_qty,
                        # 'lot_no': val.lot_no,
                        # 'lot_name': val.lot_name,
                        # 'expiration_date': val.expiration_date,
                    }])
                # ///////////////////////////////////////////////////////


                if rec.picking_type_id.code == 'incoming':
                    if scan_lot_obj:
                        for line in scan_list:
                            if line[2]['product_id'] == scan_lot_obj.product_id.id and line[2][
                                'lot_no'] == rec.ean132 and line[2][
                                'expiration_date'] == scan_lot_obj.expiration_date and line[2][
                                'lot_name'] == scan_lot_obj.lot_name:
                                line[2]['product_uom_qty'] = line[2]['product_uom_qty'] + 1
                                scan_exist = True

                        # temp list
                        for line in temp_list:
                            if line[2]['product_id'] == scan_lot_obj.product_id.id:
                                line[2]['product_uom_qty'] = line[2]['product_uom_qty'] + 1
                                temp_exist = True
                                # /////////////////////////////////////////////

                    if not scan_lot_obj:
                        scanned_lot = rec.ean132
                        extracted_lot = str(scanned_lot).split('/')[0][5:-1]
                        extracted_lot2 = extracted_lot.lstrip("0")
                        extracted_year = str(scanned_lot)[str(scanned_lot).find("/") + 1:].split()[0][:2]
                        if extracted_year == 'Fa':
                            extracted_year = str(11)
                        get_product = rec.env['product.product'].search(['|',('default_code', '=', extracted_lot),('default_code', '=', extracted_lot2)])
                        lot_obj_search = rec.env['stock.production.lot'].search([('name', '=', scanned_lot)])

                        # get month
                        month = 0
                        month2 = 0
                        if "A" in str(str(scanned_lot)):
                            month2 = 1
                        elif "B" in str(scanned_lot):
                            month = 1
                            month2 = 2
                        elif "C" in str(scanned_lot):
                            month = 2
                            month2 = 3
                        elif "D" in str(scanned_lot):
                            month = 3
                            month2 = 4
                        elif "E" in str(scanned_lot):
                            month = 4
                            month2 = 5
                        elif "F" in str(scanned_lot):
                            month = 5
                            month2 = 6
                        elif "G" in str(scanned_lot):
                            month = 6
                            month2 = 7
                        elif "H" in str(scanned_lot):
                            month = 7
                            month2 = 8
                        elif "I" in str(scanned_lot):
                            month = 8
                            month2 = 9
                        elif "J" in str(scanned_lot):
                            month = 9
                            month2 = 10
                        elif "K" in str(scanned_lot):
                            month = 10
                            month2 = 11
                        elif "L" in str(scanned_lot):
                            month = 11
                            month2 = 12
                        elif "M" in str(scanned_lot):
                            month = 12

                        exp_dat = str(20) + extracted_year + "-" + str(month) + "-" + str(1)
                        exp_dat2 = str(20) + extracted_year + "-" + str(month2) + "-" + str(1)
                        if get_product:
                            ex_date = datetime.datetime.strptime(exp_dat, '%Y-%m-%d')
                            ex_date2 = datetime.datetime.strptime(exp_dat2, '%Y-%m-%d')

                        # if rec.ean132:
                        #     if not get_product:
                        #         raise Warning(str("The lot number you entered not found !!"))

                        if rec.type_of_scaning == 'first_group':

                            for line in scan_list:
                                if line[2]['product_id'] == lot_obj_search.product_id.id and line[2][
                                    'lot_no'] == str(scanned_lot).split('/')[0][5:-1] and line[2][
                                    'expiration_date'] == lot_obj_search.expiration_date and line[2][
                                    'lot_name'] == lot_obj_search.lot_name:
                                    line[2]['product_uom_qty'] = line[2]['product_uom_qty'] + 1
                                    scan_exist = True

                            # temp list
                            for line in temp_list:
                                if line[2]['product_id'] == lot_obj_search.product_id.id:
                                    line[2]['product_uom_qty'] = line[2]['product_uom_qty'] + 1
                                    temp_exist = True
                            # ////////////////////////////////////////////////
                            if not scan_exist:
                                if get_product:
                                    scan_list.append([0, 0,
                                                      {
                                                          'product_id': get_product.id,
                                                          'product_uom_qty': 1,
                                                          'lot_no': scanned_lot,
                                                          'lot_name': str(scanned_lot).split('/')[1][5:-4],
                                                          'expiration_date': ex_date,

                                                      }])
                            #temp list
                            if not temp_exist:
                                if get_product:
                                    temp_list.append([0, 0,
                                                      {
                                                          'product_id': get_product.id,
                                                          'product_uom_qty': 1,
                                                          # 'lot_no': scanned_lot,
                                                          # 'lot_name': str(scanned_lot).split('/')[1][5:-4],
                                                          # 'expiration_date': ex_date,

                                                      }])

                            if get_product:
                                if not lot_obj_search:
                                    rec.env['stock.production.lot'].create({'product_id': get_product.id,
                                                                            'product_uom_qty': 1,
                                                                            'lot_no': get_product.name,
                                                                            'name': scanned_lot,
                                                                            'lot_name': str(scanned_lot).split('/')[1][
                                                                                        5:-4],
                                                                            'expiration_date': exp_dat,
                                                                            })

                        elif rec.type_of_scaning == 'second_group':
                            for line in scan_list:
                                if line[2]['product_id'] == lot_obj_search.product_id.id and line[2][
                                    'lot_no'] == str(scanned_lot).split('/')[0][5:-1] and line[2][
                                    'expiration_date'] == lot_obj_search.expiration_date and line[2][
                                    'lot_name'] == lot_obj_search.lot_name:
                                    line[2]['product_uom_qty'] = line[2]['product_uom_qty'] + 1
                                    scan_exist = True

                            # temp list
                            for line in temp_list:
                                if line[2]['product_id'] == lot_obj_search.product_id.id :
                                    line[2]['product_uom_qty'] = line[2]['product_uom_qty'] + 1
                                    temp_exist = True
                            # //////////////////////////////////////////

                            if not scan_exist:
                                if get_product:
                                    scan_list.append([0, 0,
                                                      {
                                                          'product_id': get_product.id,
                                                          'product_uom_qty': 1,
                                                          'lot_no': str(scanned_lot).split('/')[0][5:-1],
                                                          'lot_name': str(scanned_lot).split('/')[1][5:-4],
                                                          'expiration_date': ex_date2,

                                                      }])
                            # temp list
                            if not temp_exist:
                                if get_product:
                                    temp_list.append([0, 0,
                                                      {
                                                          'product_id': get_product.id,
                                                          'product_uom_qty': 1,
                                                          # 'lot_no': str(scanned_lot).split('/')[0][5:-1],
                                                          # 'lot_name': str(scanned_lot).split('/')[1][5:-4],
                                                          # 'expiration_date': ex_date2,

                                                      }])
                            # //////////////////////////////////////////////

                            if get_product:
                                if not lot_obj_search:
                                    rec.env['stock.production.lot'].create({'product_id': get_product.id,
                                                                            'product_uom_qty': 1,
                                                                            'lot_no': get_product.name,
                                                                            'name': get_product.default_code,
                                                                            'lot_name': str(scanned_lot).split('/')[1][
                                                                                        5:-4],
                                                                            'expiration_date': exp_dat2,

                                                                            })


                elif rec.picking_type_id.code != 'incoming':
                    for line in scan_list:
                        if line[2]['product_id'] == scan_lot_obj.product_id.id and line[2]['lot_no'] == rec.ean132:
                            line[2]['product_uom_qty'] = line[2]['product_uom_qty'] + 1
                            scan_exist = True

                    #temp list
                    for line in temp_list:
                        if line[2]['product_id'] == scan_lot_obj.product_id.id:
                            line[2]['product_uom_qty'] = line[2]['product_uom_qty'] + 1
                            temp_exist = True

                if not scan_exist:
                    if scan_lot_obj:
                        scan_list.append([0, 0,
                                          {
                                              'product_id': scan_lot_obj.product_id.id,
                                              'product_uom_qty': 1,
                                              'lot_no': scan_lot_obj.name,
                                              'lot_name': scan_lot_obj.lot_name,
                                              'expiration_date': scan_lot_obj.expiration_date,
                                          }])

                # temp list
                if not temp_exist:
                    if scan_lot_obj:
                        temp_list.append([0, 0,
                                          {
                                              'product_id': scan_lot_obj.product_id.id,
                                              'product_uom_qty': 1,
                                              # 'lot_no': scan_lot_obj.name,
                                              # 'lot_name': scan_lot_obj.lot_name,
                                              # 'expiration_date': scan_lot_obj.expiration_date,
                                          }])
                        # /////////////////////////////////////////

                if rec.ean132:
                    if not scan_lot_obj:
                        pass#raise Warning(str("The lot number you entered not found !!"))

                rec.ean132 = ''
                rec.scan_products_ids = scan_list
                rec.temp_products_ids = temp_list
                rec.picking_type_id = pkin_typ
                rec.state = 'draft'
                rec.move_type = mv_typ
                rec.priority = priority_id
                rec.location_id = location_id
                rec.company_id = company_id
                rec.picking_type_code = picking_type_code
                rec.type_of_scaning == typ_of_scan



    # @api.multi
    # def clear_scanned_lines(self):
    #     list = []
    #     for rec in self:
    #         for line in rec.scan_products_ids:
    #             list.append(
    #                 [0, 0,
    #                  {
    #                      'product_id': line.product_id.id,
    #                      'product_uom_qty': 1,
    #                      'lot_no': line.product_id.name,
    #                      'lot_name': line.lot_name,
    #                      'expiration_date': line.expiration_date,
    #                  }])
    #         del list[:]
    #
    #         rec.scan_products_ids = list


                # +H844142806231/261512863105F16S
                # +H844142806241/261512863105F16S
                #      00598004702
                #         14280624

                # +H844142806251/261512863105F16S
                # +H844142806261/261512863105F16S

# +H124005980047021/2624363445303H16
# +H124009999999981/2624363445303H16598004702
# /////////////////////////////////////
