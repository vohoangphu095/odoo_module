from odoo import fields, models


class HospitalPatient(models.Model):
    _name = "hospital.patient"

    name = fields.Char(string="Name", tracking=1)
    age = fields.Integer(string="Age", tracking=1)
    gender = fields.Selection([
        ('other', 'Other'),
        ('male', 'Male'),
        ('female', 'Female')
    ], string="Gender", default="male", tracking=1)
    note=fields.Text(string='dessss')
