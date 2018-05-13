{
    'name': 'Point Of Sale Changes',
    'version': '1.1',
    'category': 'pos',
    'author': 'Mohammed Ali<mohamed.gomaa@acme-group.net>',
    'description': """
POS Changes
==========================
    """,
    'website': "http://www.yourcompany.com",
    'depends': ['point_of_sale'],
    'data': [

        'views/res_partner_changes_view.xml',
        # 'views/point_of_sale.xml',
    ],
    'qweb': ['static/src/xml/pos.xml'],

}