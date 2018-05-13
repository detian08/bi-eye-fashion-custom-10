# -*- coding: utf-8 -*-
##############################################################################
#
# OdooBro - odoobro.contact@gmail.com
#
##############################################################################

import logging

from openerp import api, models
_logger = logging.getLogger('openerp')


class UpdateFunctionData(models.TransientModel):
    _name = "update.function.data"

    @api.model
    def update_sale_config_settings(self):
        _logger.info("===== START: UPDATE SALE CONFIG SETTINGS =====")
        # For group
        config_data = {
            'sale_pricelist_setting': 'formula',
            'group_pricelist_item': True,
            'group_sale_pricelist': True,
            'group_product_pricelist': False
        }
        SaleConfig = self.env['sale.config.settings']
        fs = dict(SaleConfig._fields)
        vals = SaleConfig.default_get(fs)
        vals.update(config_data)
        sale_config = SaleConfig.create(vals)
        sale_config.execute()
        _logger.info("===== END: UPDATE SALE CONFIG SETTINGS =====")
        return True
