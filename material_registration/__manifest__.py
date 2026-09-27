# -*- coding: utf-8 -*-
{
    'name': 'Material Registration',
    'version': '14.0.1.0.0',
    'category': 'Inventory',
    'summary': 'Registrasi material yang akan dijual',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'data/material_supplier_data.xml',
        'views/material_supplier_views.xml',
        'views/material_views.xml',
        'views/material_menus.xml',
    ],
    'installable': True,
    'application': True,
}
