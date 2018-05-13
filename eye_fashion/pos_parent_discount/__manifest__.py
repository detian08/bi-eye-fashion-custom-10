# -*- coding: utf-8 -*-

{
    'name': 'POS Parent Discount',
    'category': 'Point of Sale',
    'author': 'ACME TEAM',
    'website': 'http://www.acme-group.net',
    'depends': [ 'base','point_of_sale',],
    'data': [
        'views/res_partner.xml',
        'views/account_journal.xml',
        'views/pos_order.xml',
    ],
}
