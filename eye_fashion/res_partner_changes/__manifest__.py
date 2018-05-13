{
    'name': "Partner Changes",
    'author': "ACME Team",
    'category': "Sale",
    'data': [
        'views/res_partner.xml',
        'views/res_doctor.xml',
        'views/res_hospital.xml',
        'views/medical.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [],
    'depends': ['base','sale','sales_team'],
    'installable': True,
}