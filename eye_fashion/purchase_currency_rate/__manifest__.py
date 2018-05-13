# -*- coding: utf-8 -*-

{
    'name': 'Purchase Rates',
    'version': '1.0',
    'category': 'sale',
    'description': """
    """,
    'author': 'Mostafa Mohamed',
    'website': '',
    'depends': ['purchase', 'account_accountant'],
    'data': [
        'views/invoice_view.xml',
        'views/payment_view.xml',
        'views/purchase_view.xml',
    ],
    'installable': True,
    'auto_install': False,
}
