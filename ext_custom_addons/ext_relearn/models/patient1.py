from odoo import fields, api, models, exceptions
from odoo.exceptions import ValidationError


class HospitalPatient(models.Model):
    _name = "hospital1.patient"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "hospital patient"

    name = fields.Char(string="Name", required=True, tracking=True)
    age = fields.Integer(string='Age', tracking=True)
    image_patient = fields.Binary(string='Image')
    appoint_ids = fields.One2many("hospital1.appointment", "patient_id")
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ], required=True, default='male', tracking=True)
    note = fields.Text(string='Description', tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'), ('confirm', 'Confirmed'), ('done', 'Done'), ('cancel', 'Cancelled')
    ], string='Status', default='draft')
    responsive_id = fields.Many2one('res.partner', string="Responsible")
    sequence_patient = fields.Char(string='patient sequence',
                                   default=lambda self: self.env['ir.sequence'].next_by_code("seq.hospital.patient"))
    company_id=fields.Many2one('res.company')
    @api.model
    def create(self, vals):
        if not vals.get('name') or not vals.get('age') or not vals.get('gender') or not vals.get('note'):
            raise exceptions.ValidationError("Vui long nhap day du thong tin!")
        res = super(HospitalPatient, self).create(vals)
        return res

    def action_confirm(self):
        self.state = 'confirm'

    def action_done(self):
        self.state = 'done'

    def action_draft(self):
        self.state = 'draft'

    def action_cancel(self):
        self.state = 'cancel'

    def unlink(self):
        if self.state == 'done':
            raise ValidationError('cant delete %s when in done state' % self.name)
        return super(HospitalPatient, self).unlink()

    @api.constrains('name')
    def check_name(self):
        for rec in self:
            patient = self.env['hospital1.patient'].search([('name', '=', rec.name), ('id', '!=', rec.id)])
            if patient:
                raise ValidationError("Name %s already  exists" % rec.name)

    def name_get(self):
        result=[]
        for rec in self:
            name=f'{rec.sequence_patient} {rec.name} {rec.gender}'
            result.append((rec.id,name))
        return  result