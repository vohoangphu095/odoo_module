# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Quản Lý Thuê Xe',
    'version': '1.1',
    'category': 'Sales/Sales',
    'summary': 'Quan ly Thue Xe',
    'description': """
This module contains all the common features of Sales Management and eCommerce.

****************
Create by IT VX
****************

    """,
    'depends': ['base', 'stock', 'account'],
    'data': [
        'data/ir_sequence_data.xml',
        'security/ir.model.access.csv',
        'views/bike_rental_view.xml',
        'views/bike_vehicle_view.xml',
        'views/res_partner_view.xml',
        'views/invoice_view.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
