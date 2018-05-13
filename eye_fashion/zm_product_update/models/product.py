from odoo import models, api
from odoo.exceptions import UserError
from odoo.tools.translate import _


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.model
    def create(self, vals):
        name_there = self.search([('name', '=', vals.get('name'))])
        if name_there:
            raise UserError(_("A name can only be assigned to one product !"))
        res = super(ProductTemplate, self).create(vals)
        return res

    @api.multi
    def write(self, vals):
        if vals.get('name'):
            name_there = self.search([('name', '=', vals.get('name'))])
            if name_there:
                raise UserError(_("A name can only be assigned to one product !"))
        res = super(ProductTemplate, self).write(vals)
        return res


class Product(models.Model):
    _inherit = 'product.product'

    @api.model
    def create(self, vals):
        new_barcode = ''
        max_barcode = self.search([('barcode', '!=', '')], order='barcode desc')
        try:
            max_code = max([int(x.barcode) for x in max_barcode])
            if max_code and not vals.get('barcode'):
                new_barcode = max_code + 1
        except:
            pass
        res = super(Product, self).create(vals)
        if new_barcode:
            res.write({'barcode': new_barcode})
        return res

    @api.multi
    def write(self, vals):
        if vals.get('name'):
            name_there = self.search([('name', '=', vals.get('name'))])
            if name_there:
                raise UserError(_("A name can only be assigned to one product !"))
        res = super(Product, self).write(vals)
        return res


Product()
