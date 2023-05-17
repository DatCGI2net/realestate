# -*- coding: utf-8 -*-
{
    'name': "Real Estate Pilot",

    'summary': """
        An realestate advertisement""",

    'description': """
        Real Estate
    """,

    'author': "Hip Dev",
    'website': "http://www.cgito.net",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sales/CRM',
    'version': '16.0.0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'account',

    ],
    'data': [
        'security/ir.model.access.csv',
        'views/estate_property_views.xml',
        'views/estate_menus.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'application': True,
    'license': 'LGPL-3',

}
