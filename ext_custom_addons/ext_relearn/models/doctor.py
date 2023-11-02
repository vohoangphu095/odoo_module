from odoo import fields, api, models

class HospitalDoctor(models.Model):
    _name = "hospital.doctor"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "hospital doctor"
    _rec_name = 'doctor_name'
    _order="age desc"
    is_deleted = fields.Boolean(string='Deleted', default=True)

    doctor_name = fields.Char(string="Name", required=True, tracking=True)
    age = fields.Integer(string='Age', tracking=True)
    image = fields.Binary(string='Image')
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ], required=True, default='male', tracking=True)
    note = fields.Text(string='Description', tracking=True)


    def copy(self, default=None):
        if default is None:
            default = {}
        if not default.get('doctor_name'):
            default['doctor_name'] = ("%s (Copy)" % self.doctor_name)
        return super(HospitalDoctor, self).copy(default)
