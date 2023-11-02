{
    'name': 'HOSPITAL MANAGEMENTx',
    'version': 'ODOO16x',
    'category': 'MANAGEMENTx',
    'summary': 'APP APP APP xxx',
    'description': """xxx yyy zzz
    """,
    'depends': [
        'sale',
        'mail',
        'base',
        'report_xlsx',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/data_seq.xml',
        'wizard/view_create_appointment_wizard.xml',
        'views/view_patient1.xml',
        'views/sale.xml',
        'views/view_kid.xml',
        'views/view_gender.xml',
        'views/view_appointment.xml',
        'views/view_doctor.xml',
        'report/report_patient_card.xml',
        'report/report.xml',

    ],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
