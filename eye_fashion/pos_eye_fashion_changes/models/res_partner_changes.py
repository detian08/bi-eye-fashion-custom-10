from openerp import fields, models, api

class res_partner_inherited(models.Model):
    _inherit = 'res.partner'

    sph_data = fields.Float('SPH')
    cyl_data = fields.Float('CYL')
    doctor_id = fields.Char('Doctor Name')
    hospital_id = fields.Char( 'Hospital')
    card_id = fields.Char('Card ID')
    expiry_date = fields.Char('Exp. Date')

    percentage_of_discount = fields.Float('% of Discount')
    discount_account = fields.Many2one('account.account', 'Account of Discount')

    related_percentage_of_discount = fields.Float(related='parent_id.percentage_of_discount', store=True )
    related_expiry_date = fields.Char()
    related_parent_name = fields.Char(related='parent_id.name', store=True)


    @api.model
    def create(self, vals):
        res = super(res_partner_inherited, self).create(vals)
        parent = res.parent_id.id
        if parent:
            res.write({'related_expiry_date':res.parent_id.expiry_date})
        return res

