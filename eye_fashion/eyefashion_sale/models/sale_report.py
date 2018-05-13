import logging
from openerp import models, fields, api, _
from openerp import workflow

_logger = logging.getLogger(__name__)

class SaleReport(models.Model):
    _inherit = "sale.report"

    sale_type = fields.Char('Type')

    # @api.model_cr
    # def init(self):
    #     print 'sale report view reloading'
    #     super(SaleReport,self).init()

    def _select(self):
        select_str = super(SaleReport, self)._select()
        return select_str + ',s.sale_type as sale_type'


    def _group_by(self):
        group_by_str = super(SaleReport, self)._group_by()
        return group_by_str + ',s.sale_type'
