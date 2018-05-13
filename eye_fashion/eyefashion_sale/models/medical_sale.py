# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools import float_compare
from odoo.exceptions import UserError
from datetime import datetime, date

class SaleOrderMedical(models.Model):
    _inherit = "sale.order"

    doctor_id = fields.Many2one(related='medical_id.doctor_id',string='Doctor',readonly=True,store=True)
    hospital_id = fields.Many2one(related='medical_id.hospital_id',string='Hospital',readonly=True,store=True)
    date = fields.Date(related='medical_id.date',string='Date',readonly=True,store=True)
    family_name = fields.Char(related='medical_id.family_name',string='Family',readonly=True,store=True)

    re_sph = fields.Selection(related='medical_id.re_sph', string='RE (SPH)',readonly=True)
    re_cyl =fields.Selection(related='medical_id.re_cyl', string='RE (CYL)',readonly=True)
    re_ax =fields.Selection(related='medical_id.re_ax', string='RE (AX)',readonly=True)
    re_ipd =fields.Selection(related='medical_id.re_ipd',  string='RE (IPD)',readonly=True)
    re_add =fields.Selection(related='medical_id.re_add',  string='RE (ADD)',readonly=True)
    re_seg =fields.Selection(related='medical_id.re_seg', string='RE (SEG.HI)',readonly=True)

    le_sph =fields.Selection(related='medical_id.le_sph', string='LE (SPH)',readonly=True)
    le_cyl =fields.Selection(related='medical_id.le_cyl', string='LE (CYL)',readonly=True)
    le_ax =fields.Selection(related='medical_id.le_ax', string='LE (AX)',readonly=True)
    le_ipd =fields.Selection(related='medical_id.le_ipd', string='LE (IPD)',readonly=True)
    le_add =fields.Selection(related='medical_id.le_add',  string='LE (ADD)',readonly=True)
    le_seg =fields.Selection(related='medical_id.le_seg', string='LE (SEG.HI)',readonly=True)