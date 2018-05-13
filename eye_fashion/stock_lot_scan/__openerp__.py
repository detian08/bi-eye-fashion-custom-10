{
    'name': 'Stock Lot Scan',
    'version': '1.1',
    'author': 'Mohammed Ali<moh_ali2523@yahoo.com>',
    'category': 'Sales',
    'website': '',
    'depends': ['stock','sale', 'product'],
    'data': [

        # 'views/sale_order_changes_view.xml',
        'views/stock_picking_changes_view.xml',
        # 'wizard/get_temp_lines_view.xml',
        'security/ir.model.access.csv',

    ],

}
