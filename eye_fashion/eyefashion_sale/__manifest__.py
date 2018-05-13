# -*- coding: utf-8 -*-
{
    'name': 'Eye-fashion Sales',
    'category': 'Sales',
    'author': "ACME TEAM",
    'website': 'http://www.acme-group.net',
    'depends': ['account','sale_stock', 'sales_team','res_partner_changes','sales_order_lines_image'
                ],
    'data': [
        'security/pos_sale.xml',
        'data/pos_sale_sequence.xml',
        'views/pos_config_settings_views.xml',
        'views/account_journal_view.xml',
        'views/account_invoice_view.xml',
        'views/account_payment.xml',
        'views/stock_picking.xml',
        'views/stock_scrap.xml',
        'views/product_product.xml',
        'views/product_brand_view.xml',
        'views/res_partner.xml',
        'views/crm_team.xml',
        'views/sale_view.xml',
        'views/report_payment.xml',
        'views/pos_menuitem.xml',
        'security/ir.model.access.csv',
             ],
    'installable': True,
}
