from odoo import fields, api, models


class HouseDetail(models.Model):
    _name = 'house.detail'

    name = fields.Char(stirng='Phong so ')
    status = fields.Selection([
        ('available', 'Trong'),
        ('Unavailable', 'Da thue'),
    ], string='Status')
