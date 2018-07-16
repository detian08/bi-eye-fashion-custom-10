# -*- coding: utf-8 -*-

from odoo.osv import expression
from odoo import models, fields, api

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    status_list = [('new', 'New'),
                  ('in_way', 'In The Way'),
                  ('add_req', 'Additional Request'),
                  ('received','Received'),
                  ('factory_in','Factory in'),
                  ('prepared_lance','Prepared Lens'),
                  ('under_process','Under Process'),
                  ('done','Done'), 
                  ('reject','Reject')]

    custom_status = fields.Selection(status_list,string='Status', copy=False, track_visibility='onchange', store=True)
    related_status = fields.Selection(status_list,compute='_get_related_status',string='Status',readonly=True)

    picking_type_status = fields.Char('Picking Type', compute='_get_picking_type')
    sale_order_id = fields.Many2one('sale.order', 'Sale Order')
    purchase_order_id = fields.Many2one('purchase.order', 'Purchase Order')


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

    @api.depends('state')
    def _get_custom_state(self):
      for pick in self:
        if pick.state == 'draft':
          custom_status = 'new'
          pick.update({
                        'custom_status': custom_status,
                     })
        elif pick.state == 'cancel':
          custom_status =  'reject'
          pick.update({
                        'custom_status': custom_status,
                     })
        elif pick.state == 'done':
          custom_status =  'done'
          pick.update({
                        'custom_status': custom_status,
                     })
        else:
          pick.update({
                        'custom_status': pick.custom_status,
                     })