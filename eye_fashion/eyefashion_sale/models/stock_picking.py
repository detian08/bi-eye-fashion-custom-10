# -*- coding: utf-8 -*-

from odoo.osv import expression
from odoo import models, fields, api

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    status_list = [('received','Received'),
                                      ('factory_in','Factory in'),
                                      ('prepared_lance','Prepared Lance'),
                                      ('under_process','Under Process')]

    custom_status = fields.Selection(status_list,string='Status',copy=False, store=True, track_visibility='onchange')
    related_status = fields.Selection(status_list,compute='_get_related_status',string='Status',readonly=True)

    picking_type_status = fields.Char('Picking Type', compute='_get_picking_type')

    @api.multi
    def _get_picking_type(self):
        for picking in self:
            picking.picking_type_status = picking.picking_type_id.code

    @api.multi
    def _get_related_status(self):
        for picking in self:
            if picking.group_id:
                for pick in self.env['stock.picking'].search([('group_id', '=', picking.group_id.id)]):
                    if pick.picking_type_id.warehouse_id != picking.picking_type_id.warehouse_id and pick.custom_status:
                        picking.related_status = pick.custom_status