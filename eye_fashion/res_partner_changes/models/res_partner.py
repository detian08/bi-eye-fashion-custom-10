# -*- coding: utf-8 -*-

from odoo import api, fields, models
from datetime import date
from datetime import datetime
from dateutil.relativedelta import relativedelta

class ResDoctor(models.Model):
    _name = 'res.doctor'

    name = fields.Char('Name')
    area = fields.Char('Area')
    address = fields.Char('Address')

class ResHospital(models.Model):
    _name = 'res.hospital'

    name = fields.Char('Name')


class ResPartnerLab(models.Model):
    _name = 'res.partner.lab'
    _rec_name = 'date'

    partner_id = fields.Many2one('res.partner')
    doctor_id = fields.Many2one('res.doctor','Doctor',required=True)
    hospital_id = fields.Many2one('res.hospital','Hospital',required=True)
    date = fields.Date('Date', copy=False, default=fields.Datetime.now())
    family_name = fields.Char('Family')


    re_sph = fields.Selection(selection='_get_selection1', string='RE (SPH)',required=True)
    re_cyl =fields.Selection(selection='_get_selection2', string='RE (CYL)',required=True)
    re_ax =fields.Selection(selection='_get_selection6', string='RE (AX)',required=True)
    re_ipd =fields.Selection(selection='_get_selection5',  string='RE (IPD)',required=True)
    re_add =fields.Selection(selection='_get_selection3',  string='RE (ADD)',required=True)
    re_seg =fields.Selection(selection='_get_selection4', string='RE (SEG.HI)')

    le_sph =fields.Selection(selection='_get_selection1', string='LE (SPH)',required=True)
    le_cyl =fields.Selection(selection='_get_selection2', string='LE (CYL)',required=True)
    le_ax =fields.Selection(selection='_get_selection6', string='LE (AX)',required=True)
    le_ipd =fields.Selection(selection='_get_selection5', string='LE (IPD)',required=True)
    le_add =fields.Selection(selection='_get_selection3',  string='LE (ADD)',required=True)
    le_seg =fields.Selection(selection='_get_selection4', string='LE (SEG.HI)')

    def _get_selection1(self):
        choice = []
        counter = 20.00
        while counter >= -20.00:
            display_name = 'num' + str(counter)
            number = "%+06.2f" % (counter)
            choice.append((display_name, number))
            counter -= 00.25
        return choice

    def _get_selection2(self):
        choice = []
        counter = 6
        while counter >= -6:
            display_name = 'num' + str(counter)
            number = "%+06.2f" % (counter)
            choice.append((display_name, number))
            counter -= .25
        return choice

    def _get_selection3(self):
        choice = []
        counter = 3.75
        while counter >= 0.5:
            display_name = 'num' + str(counter)
            number = "%+06.2f" % (counter)
            choice.append((display_name, number))
            counter -= .25
        number = "%06.2f" % (00.00)
        choice.append(('num0', number))
        return choice

    def _get_selection4(self):
        choice = []
        counter = 35
        while counter >= 8:
            display_name = 'num' + str(counter)
            number = "%6.2f" % (counter)
            choice.append((display_name, number))
            counter -= .5
        return choice

    def _get_selection5(self):
        choice = []
        counter = 20
        while counter <= 38:
            display_name = 'num' + str(counter)
            number = "%6.2f" % (counter)
            choice.append((display_name, number))
            counter += .5
        return choice

    def _get_selection6(self):
        choice = []
        counter = 0
        while counter <= 180:
            display_name = 'num' + str(counter)
            number = counter
            choice.append((display_name, number))
            counter += 1
        return choice

class ResPartner(models.Model):
    _inherit = 'res.partner'

    lab_ids = fields.One2many('res.partner.lab','partner_id',string="EYE FASHION OPTICS - LAB FORM")
    insurance_company_ids = fields.Many2many('res.partner','partner_company_rel','partner_id','company_id','Company')