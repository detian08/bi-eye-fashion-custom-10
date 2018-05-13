# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools import float_compare
from odoo.exceptions import UserError

class CrmTeam(models.Model):
    _inherit = "crm.team"

    cash_journal_id = fields.Many2one('account.journal','Cash')
    bank_journal_id = fields.Many2one('account.journal','Ahly')
    bank_journal_id2 = fields.Many2one('account.journal','Alex')

    warehouse_id = fields.Many2one('stock.warehouse','Warehouse')
    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account', help="The analytic account related to a sales order.", copy=False)

    #branch sequence related fields
    code = fields.Char(string='Short Code', size=6, required=True, help="The sales orders of this team/branch will be named using this prefix.")
    sequence_id = fields.Many2one('ir.sequence', string='Entry Sequence',
                                  help="This field contains the information related to the numbering of the sales orders of this team/branch.",
                                  readonly=True, copy=False)

    _sql_constraints = [
        ('code_uniq', 'unique(code)', 'Code must be unique !'),
    ]

    @api.multi
    def write(self, vals):
        for team in self:
            if ('code' in vals and team.code != vals['code']):
                # if self.env['sale.order'].search([('team_id', 'in', self.ids)], limit=1):
                #     raise UserError(_('This Sequences already contains orders, therefore you cannot modify its short name.'))
                new_prefix = self._get_sequence_prefix(vals['code'])
                team.sequence_id.write({'prefix': new_prefix})
            if not team.sequence_id:
                vals.update({'sequence_id': self.sudo()._create_sequence(vals).id})
        return super(CrmTeam, self).write(vals)


    @api.model
    def _get_sequence_prefix(self, code):
        prefix = code.upper()
        return prefix + '/%(range_year)s/'


    @api.model
    def _create_sequence(self, vals):
        prefix = self._get_sequence_prefix(vals['code'])
        if 'name' in vals:
            name = vals['name']
        else:
            name = self.name
        if 'code' in vals:
            code = vals['code']
        else:
            code = self.code
        print self.id
        seq = {
            'name': name,
            'implementation': 'no_gap',
            'prefix': prefix,
            'code': code,
            'padding': 5,
            'number_increment': 1,
            'use_date_range': True,
        }
        if 'company_id' in vals:
            seq['company_id'] = vals['company_id']
        return self.env['ir.sequence'].create(seq)


    @api.model
    def create(self, vals):
        if not vals.get('sequence_id'):
            vals.update({'sequence_id': self.sudo()._create_sequence(vals).id})
        return super(CrmTeam, self).create(vals)