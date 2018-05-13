# -*- coding: utf-8 -*-
{
    'name': "POS Referal",

    'summary': """
        Pos Referal For Odoo Enterprise Edition.
        This Module creates a referal bonus for each customer referal and adds the points to POS Loyalty.
        """,

    'description': """
        - If an  existing customer brings a new customer to the shop, a new customer is created and refered by field is set to existing customer.

        - A customer can be assigned by a Tier which has the bonus percentage for calculating bonus points.

        - When the referral spends money in the shop, the referrer earns loyalty points based on the percentage in his tier.

        - The loyalty points can be used to redeem rewards (same as existing loyalty system).

        - A customer can have unlimited referrals linked to his account.

    """,

    'author': "Techspawn Solutions",
    'website': "http://www.techspawn.com",

    'category': 'Point of Sale',
    'version': '0.1',

    'depends': ['base', 'point_of_sale', 'pos_loyalty'],

    'data': [
        # 'security/ir.model.access.csv',
        'views/pos_views.xml',
        'views/res_partner.xml',
    ],
    'qweb': ['static/src/xml/pos.xml'],
    
}