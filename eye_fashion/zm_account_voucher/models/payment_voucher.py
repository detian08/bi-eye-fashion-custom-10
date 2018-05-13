# -*- encoding: utf-8 -*-
import re
import time

from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.tools.translate import _


class PaymentVoucher(models.Model):
    _name = 'zm.payment.voucher'
    _inherit = 'mail.thread'
    _description = 'Payments'
    _order = 'name asc'
    _rec_name = 'name'

    name = fields.Char(string='Number', default='/', track_visibility='onchange', readonly=True)
    payment_journal_id = fields.Many2one(comodel_name='account.journal', domain="[('type', 'in', ['bank', 'cash'])]",
                                         string='Payment Journal', required=True,
                                         states={'done': [('readonly', True)]}, track_visibility='onchange')
    date = fields.Date(string='Payment Date', default=time.strftime('%Y-%m-%d'), required=True,
                       states={'done': [('readonly', True)]})
    journal_bank = fields.Boolean(default=False, compute='_get_journal_type')
    bank_id = fields.Char(string='Bank Name', states={'done': [('readonly', True)]})
    cheque_number = fields.Char(string='Cheque Number', states={'done': [('readonly', True)]})
    payment_amount = fields.Monetary(string='Payment Amount', default=0.0, currency_field='currency_id', required=True,
                                     states={'done': [('readonly', True)]})
    currency_id = fields.Many2one(comodel_name='res.currency', string='Currency', states={'done': [('readonly', True)]},
                                  default=lambda self: self.env.user.company_id.currency_id)
    ref = fields.Char(string='Reference', states={'done': [('readonly', True)]}, track_visibility='onchange')
    payment_type = fields.Selection(selection=[('customer', 'Customer'), ('supplier', 'Supplier')],
                                    string='Payment Type', states={'done': [('readonly', True)]})
    partner_id = fields.Many2one(comodel_name='res.partner', string='Partner')
    partner_name = fields.Char(string='Partner Name', track_visibility='onchange',
                               states={'done': [('readonly', True)]})
    account_id = fields.Many2one(comodel_name='account.account', string='Account', required=True,
                                 states={'done': [('readonly', True)]})
    analytic_account_id = fields.Many2one(comodel_name='account.analytic.account', string='Analytic Account',
                                          states={'done': [('readonly', True)]})
    desc = fields.Text(string='Description', states={'done': [('readonly', True)]})
    notes = fields.Text(string='Notes', states={'done': [('readonly', True)]})
    state = fields.Selection(selection=[('draft', 'Draft'), ('done', 'Done')], string='State', default='draft',
                             track_visibility='onchange')
    move_line_ids = fields.One2many('account.move.line', 'custom_payment_id', readonly=True, copy=False,
                                    ondelete='restrict')

    @api.multi
    @api.constrains('payment_amount')
    def constrains_payment_amount(self):
        if self.payment_amount <= 0:
            raise UserError(_('Amount Show be more than 0.'))

    @api.one
    @api.depends('payment_journal_id')
    def _get_journal_type(self):
        if self.payment_journal_id.type == 'bank':
            self.journal_bank = True
        else:
            self.journal_bank = False

    @api.multi
    @api.onchange('payment_journal_id')
    def onchange_payment_journal_id(self):
        if self.payment_journal_id:
            if self.payment_journal_id.type == 'bank':
                self.bank_id = self.payment_journal_id.bank_id.name

    @api.multi
    @api.onchange('partner_id', 'payment_type')
    def onchange_partner_id(self):
        if self.partner_id:
            self.partner_name = self.partner_id.name
            if self.payment_type == 'customer':
                self.account_id = self.partner_id.property_account_receivable_id.id
            elif self.payment_type == 'supplier':
                self.account_id = self.partner_id.property_account_payable_id.id
            else:
                self.account_id = False

    @api.multi
    def button_journal_entries(self):
        context = dict(self._context or {})
        context['journal_id'] = self.payment_journal_id.id
        return {
            'name': _('Journal Entries'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', self.mapped('move_line_ids').mapped('move_id').ids)],
            'context': context,
        }

    @api.multi
    def confirm_payment(self):
        move = {}
        account_id = False
        if self.partner_id and self.payment_type == 'customer':
            account_id = self.partner_id.property_account_receivable_id.id
        elif self.partner_id and self.payment_type != 'customer':
            account_id = self.partner_id.property_account_payable_id.id
        elif not self.partner_id and self.payment_type == 'customer':
            account_id = self.env.user.partner_id.property_account_receivable_id.id
        elif not self.partner_id and self.payment_type != 'customer':
            account_id = self.env.user.partner_id.property_account_payable_id.id
        move_line_1 = {
            'name': self.desc or ' ',
            'journal_id': self.payment_journal_id.id,
            'date': self.date,
            'custom_payment_id': self.id,
            'analytic_account_id': self.analytic_account_id.id,
            'partner_id': self.partner_id.id,
            'ref': self.ref,
            'account_id': self.payment_journal_id.default_debit_account_id.id,
            'debit': 0 if self.payment_type == 'supplier' else self.payment_amount,
            'credit': 0 if self.payment_type == 'customer' else self.payment_amount,
            'date_maturity': self.date,
        }
        move_line_2 = {
            'name': self.desc or ' ',
            'journal_id': self.payment_journal_id.id,
            'date': self.date,
            'analytic_account_id': self.analytic_account_id.id,
            'custom_payment_id': self.id,
            'partner_id': self.partner_id.id,
            'ref': self.ref,
            'account_id': self.account_id.id,
            'debit': 0 if self.payment_type == 'customer' else self.payment_amount,
            'credit': 0 if self.payment_type == 'supplier' else self.payment_amount,
            'date_maturity': self.date,
        }
        move.update({'journal_id': self.payment_journal_id.id,
                     'date': self.date,
                     'ref': self.ref,
                     'currency_id': self.currency_id.id,
                     'company_id': self.env.user.company_id.id,
                     'line_ids': [(0, 0, move_line_1), (0, 0, move_line_2)],
                     })
        move_created = self.env['account.move'].create(move)
        move_created.post()
        if self.payment_type == 'customer':
            self.write({'name': self.env['ir.sequence'].next_by_code('voucher.customer')})
        else:
            self.write({'name': self.env['ir.sequence'].next_by_code('voucher.supplier')})
        self.write({'state': 'done'})

    def convertNumber(self, numbers):
        number = int(numbers)
        mask = "{0:.2f}"
        snumber = mask.format(number)
        split = snumber.split('.')
        postFix = ""
        dnum = int(split[1])
        if dnum > 0:
            if len(split[1]) == 1:
                postFix = " من العشرة"
            else:
                postFix = " من المائة"

        if dnum > 0:
            postFix = " فاصل " + self.convertLong(dnum) + postFix

        result = self.convertLong(long(split[0])) + postFix

        # remove extra spaces!
        result = re.sub(r"^\\s+", "", result)
        result = re.sub(r"\\b\\s{2,}\\b", " ", result)
        return result.strip()
        return result

    def convertLong(self, number):
        # 0 to 999 999 999 999
        if (number == 0):
            return "صفر"

        snumber = str(number);

        # pad with "0"
        snumber = snumber.zfill(12)

        # XXXnnnnnnnnn
        billions = int(snumber[0:3])
        # nnnXXXnnnnnn
        millions = int(snumber[3:6])
        # nnnnnnXXXnnn
        hundredThousands = int(snumber[6:9])
        # nnnnnnnnnXXX
        thousands = int(snumber[9:12])

        tradBillions = ""
        if billions == 0:
            tradBillions = ""
        elif billions == 1:
            tradBillions = " مليار "
        elif billions == 2:
            tradBillions = " ملياران "
        elif billions >= 3 and billions <= 10:
            tradBillions = self.convertLessThanOneThousand(billions) + " مليارات "
        else:
            tradBillions = self.convertLessThanOneThousand(billions) + " مليار "

        result = tradBillions;

        tradMillions = ""
        if millions == 0:
            tradMillions = ""
        elif millions == 1:
            tradMillions = " مليون "
        elif millions == 2:
            tradMillions = " مليونان "
        elif millions >= 3 and millions <= 10:
            tradMillions = self.convertLessThanOneThousand(millions) + " ملايين "
        else:
            tradMillions = self.convertLessThanOneThousand(millions) + " مليون "

        if result.strip() and tradMillions.strip():
            result = result + " و "

        result = result + tradMillions

        tradHundredThousands = ""

        if hundredThousands == 0:
            tradHundredThousands = ""
        elif hundredThousands == 1:
            tradHundredThousands = "ألف "
        elif hundredThousands == 2:
            tradHundredThousands = "ألفان "
        elif hundredThousands >= 3 and hundredThousands <= 10:
            tradHundredThousands = self.convertLessThanOneThousand(hundredThousands) + " آلاف "
        else:
            tradHundredThousands = self.convertLessThanOneThousand(hundredThousands) + " ألف "

        if result.strip() and tradHundredThousands.strip():
            result = result + " و "
        result = result + tradHundredThousands

        tradThousand = self.convertLessThanOneThousand(thousands)
        if result.strip() and tradThousand.strip():
            result = result + " و "
        result = result + tradThousand

        # remove extra spaces!
        result = re.sub(r"^\\s+", "", result)
        result = re.sub(r"\\b\\s{2,}\\b", " ", result)
        return result.strip()

    def convertLessThanOneThousand(self, number):
        soFar = ""

        numNames = [
            "",
            " واحد",
            " اثنان",
            " ثلاثة",
            " اربعة",
            " خمسة",
            " ستة",
            " سبعة",
            " ثمانية",
            " تسعة",
            " عشرة",
            " إحدى عشر",
            " إثنى عشر",
            " ثلاثة عشر",
            " اربعة عشر",
            " خمسة عشر",
            " ستة عشر",
            " سبعة عشر",
            " ثمانية عشر",
            " تسعة عشر"
        ]

        tensNames = [
            "",
            " عشرة",
            " عشرون",
            " ثلاثون",
            " اربعون",
            " خمسون",
            " ستون",
            " سبعون",
            " ثمانون",
            " تسعون"
        ]

        if (number % 100 < 20):
            soFar = numNames[number % 100];
            number /= 100;
        else:
            soFar = numNames[number % 10];
            number /= 10;

            if soFar.strip() and tensNames[number % 10].strip():
                soFar = soFar + " و ";
            soFar = soFar + tensNames[number % 10]
            number /= 10;

        result = ""
        if soFar.strip():
            result = " و " + soFar
        else:
            result = soFar

        if number == 0:
            return soFar
        elif number == 1:
            return "مائة" + result
        elif number == 2:
            return "مائتان" + result
        elif number == 8:
            return numNames[number][:-4] + "مائة" + result
        else:
            return numNames[number][:-2] + "مائة" + result


PaymentVoucher()


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    custom_payment_id = fields.Many2one(comodel_name='zm.payment.voucher', string='Custom Payment')


AccountMoveLine()
