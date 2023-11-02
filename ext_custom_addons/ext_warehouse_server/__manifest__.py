{
    'name': 'Warehouse',
    'version': 'odoo16-wh01',
    'category': 'management',
    'summary': 'Sumary and management part in warehouse',
    'description': """
                Sumary and management part in warehouse
    """,
    'depends': [
        'sale',
        'mail',
        'base',
        'report_xlsx',
        'product',
    ],

    'data': [
        'security/ir.model.access.csv',
        'views/menu_view.xml',
        'views/warehouse_server_view.xml',
        'views/server_info_view.xml',
        'views/product_view.xml',

    ],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
