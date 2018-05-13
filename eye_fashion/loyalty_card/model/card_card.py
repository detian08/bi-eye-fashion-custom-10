# -*- coding: utf-8 -*-
##############################################################################
#
# OdooBro - odoobro.contact@gmail.com
#
##############################################################################

from datetime import datetime, timedelta
from openerp import api, fields, models
import openerp.addons.decimal_precision as dp
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from openerp.exceptions import Warning
from openerp.tools.translate import _


class CardCard(models.Model):
    _name = 'card.card'
    _description = 'Loyalty Card'
    _order = 'name'

    name = fields.Char(
        string='Card Number',
        default='/')
    type_id = fields.Many2one(
        string='Type',
        comodel_name='card.type',
        inverse='_update_pricelist_discount',
        required=1)
    partner_id = fields.Many2one(
        string='Customer',
        comodel_name='res.partner')
    creation_date = fields.Date(
        string='Creation Date')
    activate_date = fields.Date(
        string='Activated Date')
    expiry_date = fields.Date(
        string='Expiry Date')
    point_in_period = fields.Float(
        string='Points in Period',
        digits=dp.get_precision('Discount'))
    upgrade_type_id = fields.Many2one(
        string='Upgrade Card Type',
        comodel_name='card.type',
        compute="_check_upgrade",
        store=True)
    total_point = fields.Float(
        string='Total Points',
        digits=dp.get_precision('Discount'))
    last_period_total_point = fields.Float(
        string='Last Period Total Points',
        compute="_get_last_period_total_point",
        digits=dp.get_precision('Discount'))
    is_expired = fields.Boolean(
        string='Expired?',
        compute='_is_expired')
    state_id = fields.Many2one(
        string='Status',
        comodel_name='card.stage')
    noupdate_card = fields.Boolean(
        string='Noupdate Card?',
        related='state_id.noupdate_card',
        store=True)
    state = fields.Char(
        string='State',
        related='state_id.code',
        store=True)
    issue_hard_card = fields.Boolean(
        string='Is Issue Hard Card?',
        related='type_id.issue_hard_card',
        readonly=1)
    card_expected_date = fields.Date(
        string='Expected Date (for receiving Hard Card)')
    history_ids = fields.One2many(
        string='History',
        comodel_name='card.history',
        inverse_name='card_id')
    pricelist_id = fields.Many2one(
        comodel_name='product.pricelist',
        string='Pricelist',
        readonly=True, 
        help="Pricelist for the customer of this card.")

    barcode = fields.Char(
        string='Barcode')

    _sql_constraints = [
        ('barcode', 'unique(barcode)', _('Barcode must be unique.')),
    ]

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = list(args or [])
        if not (name == '' and operator == 'ilike'):
            args += ['|', ('barcode', operator, name)]
        return super(CardCard, self).name_search(name, args, operator, limit)

    @api.multi
    @api.depends('point_in_period')
    def _check_upgrade(self, points=None):
        CardType = self.env['card.type']
        for r in self:
            if not points:
                points = r.point_in_period
            args = [('categ_id', '=', r.type_id.categ_id.id),
                    ('basic_point', '<=', points),
                    ('seq', '>', r.type_id.seq)]
            type = CardType.search(args, limit=1, order='seq DESC')
            if type:
                r.upgrade_type_id = type.id

    @api.multi
    def _get_last_period_total_point(self):
        for record in self:
            if record.history_ids:
                record.last_period_total_point = \
                    record.history_ids[0].total_point
            else:
                record.last_period_total_point = 0.00

    @api.multi
    def _is_expired(self):
        tday = fields.Date.context_today(self)
        for record in self:
            is_expired = False
            if not record.expiry_date:
                continue
            if tday > record.expiry_date:
                is_expired = True
            record.is_expired = is_expired

    @api.multi
    def btn_confirm(self):
        state_id = self.env.ref('loyalty_card.stage_card2').id
        self.write({'state_id': state_id})

    @api.multi
    def btn_print_card(self):
        state_id = self.env.ref('loyalty_card.stage_card3').id
        self.write({'state_id': state_id})

    @api.multi
    def add_history(self):
        self.ensure_one()
        end_date = fields.Date.context_today(self)
        if end_date > self.expiry_date:
            end_date = self.expiry_date
        vals = {
            'card_id': self.id,
            'start_date': self.activate_date,
            'end_date': end_date,
            'point_in_period': self.point_in_period,
            'total_point': self.total_point,
            'user_id': self.env.uid,
            'type_id': self.type_id.id
        }
        return self.env['card.history'].create(vals)

    @api.multi
    def _update_pricelist_discount(self):
        for card in self:
            if not card.pricelist_id or not card.type_id:
                continue
            for item in card.pricelist_id.item_ids:
                item.price_discount = card.type_id.discount

    @api.multi
    def create_pricelist(self):
        self.ensure_one()
        Pricelist = self.env['product.pricelist']
        fs = dict(Pricelist._fields)
        vals = Pricelist.default_get(fs)
        vals.update({
            'name': u'Public Pricelist ({})'.format(self.partner_id.name)
        })
        pricelist = Pricelist.new(vals)
        for item in pricelist.item_ids:
            item.price_discount = self.type_id.discount
        vals = Pricelist._convert_to_write(pricelist._cache)
        pricelist = Pricelist.create(vals)
        return pricelist.id

    @api.multi
    def btn_upgrade_card(self):
        for r in self:
            if not r.upgrade_type_id:
                continue
            r.add_history()

            r.type_id = r.upgrade_type_id.id
            active_date = fields.Date.context_today(r)
            expiry_date = \
                r.upgrade_type_id.period_id.get_period_end_date(active_date)
            vals = {'activate_date': active_date,
                'expiry_date': expiry_date,
                'point_in_period': 0.00}
            r.write(vals)

    @api.multi
    def btn_renew(self, check_basic_points=True):
        for r in self:
            r.add_history()
        self.btn_active(check_basic_points)

    @api.multi
    def btn_force_renew(self):
        self.btn_renew(check_basic_points=False)

    @api.multi
    def btn_force_active(self):
        self.btn_active(check_basic_points=False)

    @api.multi
    def btn_active(self, check_basic_points=True):
        state_id = self.env.ref('loyalty_card.stage_card5').id
        for r in self:
            if not r.partner_id:
                raise Warning(_('''
                Error! Empty customer!
                '''))
            r.check_existed()
            if check_basic_points:
                r.check_basic_points()
            active_date = r.state_id.id != state_id and r.activate_date
            if not active_date:
                active_date = fields.Date.context_today(r)
            expiry_date = r.type_id.period_id.get_period_end_date(active_date)
            vals = {'state_id': state_id,
                    'activate_date': active_date,
                    'expiry_date': expiry_date,
                    'point_in_period': 0.00}
            # Add pricelist when activating card
            if not r.pricelist_id:
                pricelist_id = r.create_pricelist()
                if pricelist_id:
                    vals.update({'pricelist_id': pricelist_id})
            r.write(vals)

    @api.multi
    def btn_cancel(self):
        self.check_existed()
        state_id = self.env.ref('loyalty_card.stage_card6').id
        self.write({'state_id': state_id,
                    'activate_date': False,
                    'expiry_date': False})

    @api.multi
    def btn_reset(self):
        state_id = self.env.ref('loyalty_card.stage_card1').id
        self.write({'state_id': state_id})

    @api.multi
    def btn_lock(self):
        state_id = self.env.ref('loyalty_card.stage_card7').id
        self.write({'state_id': state_id})

    @api.multi
    def btn_unlock(self):
        state_id = self.env.ref('loyalty_card.stage_card5').id
        self.write({'state_id': state_id})

    @api.multi
    def check_existed(self):
        self.ensure_one()
        cancelled_state_id = self.env.ref('loyalty_card.stage_card6').id
        args = [('partner_id', '=', self.partner_id.id),
                ('state_id', '!=', cancelled_state_id),
                ('id', '!=', self.id)]
        existed = self.search(args, limit=1)
        if existed:
            raise Warning(_('''
            Error! Card {} has been issued to that customer!
            '''.format(existed.name)))

    @api.multi
    def check_basic_points(self):
        self.ensure_one()
        if not self.partner_id:
            return True
        points = 0.00
        basic_points = self.type_id.basic_point
        force_btn = _(u'Force Activate')
        if self.state == 'In Use':
            points = self.point_in_period or 0.00
            force_btn = _(u'Force Re-Activate')
            basic_points = self.type_id.point_per_period
        else:
            args = [('partner_id', '=', self.partner_id.id),
                    ('state', '=', 'done')]
            SaleOrder = self.env['sale.order']
            orders = SaleOrder.search(args)
            points = sum([r.amount_total for r in orders if r.amount_total])
            points = self.convert_amount_to_point(points)
        if basic_points and (not points or points < basic_points):
            raise Warning(_(u'''
            Error! The customer {} needs at least {:,} points,
            he/she has only {:,} points now.
            Click on the button `{}` if you want to do this action anyway.
            '''.format(self.partner_id.name, basic_points, points, force_btn)
            ))

    @api.model
    def convert_amount_to_point(self, amount):
        prate = self.env.user.company_id.lc_point_exchange_rate or 1
        if not amount or prate < 0:
            return 0.00
        res = float(amount)/float(prate)
        return int(res)

    @api.model
    def convert_point_to_amount(self, point):
        prate = self.env.user.company_id.lc_point_exchange_rate or 1
        if not point or prate < 0:
            return 0.00
        amount = round(float(point) * float(prate),2)
        return amount

    @api.model
    def default_get(self, fields_list):
        res = super(CardCard, self).default_get(fields_list)
        res.update({'creation_date': fields.Date.context_today(self)})
        stage = self.env['card.stage'].search([], limit=1)
        if stage:
            res.update({'state_id': stage.id})
        return res

    @api.model
    def create(self, vals):
        if vals.get('name', '') in ('', '/'):
            vals.update({'name': self._get_card_nb()})
        return super(CardCard, self).create(vals)

    @api.model
    def _get_card_nb(self):
        sequence = self.env['ir.sequence'].get('sequence_seq_card_nb')
        return sequence

    @api.model
    def _get_card(self, partner_id, state='In Use'):
        args = [('partner_id', '=', partner_id),
                ('state', '=', state)]
        card = self.search(args, limit=1)
        return card

    @api.model
    def _get_valid_card(self, partner_id):
        card = self._get_card(partner_id)
        if card.is_expired:
            return None
        return card
