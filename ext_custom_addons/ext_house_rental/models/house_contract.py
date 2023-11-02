from odoo import fields, api, models


class HouseContract(models.Model):
    _name = 'house.contract'

    name = fields.Char(stirng='Phong so ')
    prices = fields.Integer(string='Gia phong')
