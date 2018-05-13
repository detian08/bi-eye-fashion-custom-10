{
    'name': ' Stock Inventory Adjustments Scan',
    'version': '1.1',
    'author': 'Mohammed Ali<moh_ali2523@yahoo.com>',
    'category': 'Inventory',
    'website': 'zadsolutions.odoo.com',
    'depends': ['stock','sale', 'product'],
    'data': [

        'views/stock_inventory_changes_view.xml',
        # 'security/ir.model.access.csv',
    ],

}
