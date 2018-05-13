# -*- coding: utf-8 -*-
{
    "name": """POS Discount Programs""",
    "summary": """Use predefined discount programs for products in POS""",
    "category": "Point of Sale",
    "application": False,

    "author": "IT-Projects LLC, Dinar Gabbasov",
    "support": "apps@it-projects.info",
    "website": "https://twitter.com/gabbasov_dinar",
    "license": "LGPL-3",

    "depends": [
        'point_of_sale',
        'pos_discount',
    ],
    "external_dependencies": {"python": [], "bin": []},
    "data": [
        'views/template.xml',
        'views/view.xml',
        'security/ir.model.access.csv',
    ],
    'qweb': [
        'static/src/xml/DiscountProgram.xml',
    ],
    "demo": [],

    "post_load": None,
    "pre_init_hook": None,
    "post_init_hook": None,

    "auto_install": False,
    "installable": True,
}
