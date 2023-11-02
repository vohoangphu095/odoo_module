from odoo import fields, api,models


class HospitalPatient(models.Model):

    _inherit = 'sale.order'
    sale_description=fields.Char(string='sale description')
