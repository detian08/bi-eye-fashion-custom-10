# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import odoo.addons.decimal_precision as dp


class stockPackOperation(models.Model):
    _inherit = "stock.pack.operation"

    @api.multi
    @api.constrains('qty_done')
    def check_done_qty(self):
        for pack in self:
            if pack.picking_id.picking_type_id.code == 'outgoing':
                if pack.qty_done > pack.ordered_qty:
                    raise ValidationError(
                        _('Validation Error! Delivered Quantity cannot exceed Ordered Quantity'))