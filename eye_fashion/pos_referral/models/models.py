# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    def get_orders(self):
    	for partner in self:
            refered = self.env['res.partner'].search([('refered_by','=',partner.id)])
            if refered:
	           partner.update({'pos_orders' : self.env['pos.order'].search([('partner_id','in',refered.ids)])})

    refered_by = fields.Many2one(comodel_name='res.partner', string="Refered By", required=False)
    tier = fields.Many2one(comodel_name='bonus.tier', string='Tier', required=False)
    pos_orders = fields.Many2many('pos.order', compute="get_orders", string='Order Lines', required=False,readonly=False)
    referral_points = fields.Float(string='Total Points Earned', required=False, readonly=False)


class CustomBonusTier(models.Model):
    _name = 'bonus.tier'

    name = fields.Char('Name', required=True)
    bonus_percent = fields.Float('Bonus Percentage', required=True)
    description = fields.Text('Description', requred=False)


class PosOrderCreate(models.Model):
    _inherit = "pos.order"

    points_earned = fields.Float(string='Points Earned', required=False, readonly=False)

    @api.model
    def _process_order(self, pos_order):

        order =  super(PosOrderCreate, self)._process_order(pos_order)      
        if order.partner_id.refered_by:         
            order_amount = order.amount_total
            order_bonus = order.partner_id.refered_by.tier.bonus_percent
            order_loyalty = order_amount * (order_bonus/100)
            order.partner_id.refered_by.loyalty_points += order_loyalty
            order.partner_id.refered_by.referral_points += order_loyalty
            order.points_earned = order_loyalty
        return order