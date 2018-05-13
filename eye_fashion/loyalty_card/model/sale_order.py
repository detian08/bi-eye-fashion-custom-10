# -*- coding: utf-8 -*-
##############################################################################
#
# OdooBro - odoobro.contact@gmail.com
#
##############################################################################

from openerp import api, fields, models
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    state = fields.Selection(inverse="_update_loyalty_point")
    upgrade_message = fields.Char(
        string="Message Box",
        compute="_get_needed_amount_msg",
        store=True)
    card_id = fields.Many2one(
        string='Loyalty Card',
        comodel_name='card.card',
        inverse='_dump_func',
        search='_search_by_card',
        compute='_dump_func')

    @api.multi
    def _dump_func(self):
        pass

    @api.multi
    def _search_by_card(self, operator, value):
        partner_ids = []
        if value:
            args = [('partner_id', '!=', False)]
            cards = self.env['card.card'].name_search(value, args)
            if cards:
                card_ids = [x[0] for x in cards]
                cards = self.env['card.card'].browse(card_ids)
                partner_ids = [x.partner_id.id for x in cards]
        return [('partner_id', 'in', partner_ids)]

    @api.onchange('card_id')
    def _set_customer(self):
        for order in self:
            if not self.card_id or not self.card_id.partner_id:
                continue
            order.partner_id = self.card_id.partner_id
    
    @api.multi
    def _update_loyalty_point(self):
        for order in self:
            if order.state != 'done':
                continue
            card = self.env['card.card']._get_card(order.partner_id.id)
            if not card:
                continue
            points = card.convert_amount_to_point(order.amount_total)
            card.total_point += points
            card.point_in_period += points

    @api.multi
    @api.depends('order_line', 'state')
    def _get_needed_amount_msg(self):
        for order in self:
            msg = u''
            if order.state != 'draft':
                order.upgrade_message = msg
                continue
            card = self.env['card.card']._get_valid_card(order.partner_id.id)
            if not card:
                order.upgrade_message = msg
                continue
            remind_rate = order.company_id.lc_remind_point_rate
            if not remind_rate:
                order.upgrade_message = msg
                continue
            type = card.type_id._get_next_type()
            if type:
                amount_in_period = \
                    card.convert_point_to_amount(card.point_in_period)
                amount_onhand = order.amount_total + amount_in_period
                basic_amount = card.convert_point_to_amount(type.basic_point)
                if basic_amount > amount_onhand:
                    prate = round(float(amount_onhand)/float(basic_amount),2)
                    if prate >= remind_rate:
                        needed_amount = basic_amount - amount_onhand
                        msg = _(u'''Need more {:,} to upgrade the customer card
                        with the new discount {}%
                        '''.format(needed_amount, type.discount))
                else:
                    msg = _(u'''After done this order, this customer is
                    eligible to upgrade his/her loyalty card {}
                    with the new discount {}%.
                    '''.format(card.name, type.discount))            
            order.upgrade_message = msg

    @api.multi
    @api.onchange('partner_id')
    def onchange_partner_id(self):
        super(SaleOrder, self).onchange_partner_id()
        card = self.env['card.card']._get_valid_card(self.partner_id.id)
        if card and card.pricelist_id:
            self.pricelist_id = card.pricelist_id.id
