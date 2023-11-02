from odoo import fields, api, models, exceptions
from odoo.exceptions import ValidationError


class HospitalAppointment(models.Model):
    _name = "hospital1.appointment"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "hospital appointment"

    name = fields.Char(string="Name", required=True, tracking=True)
    patient_id = fields.Many2one("hospital1.patient", string="Patient", required=True)
    doctor_id=fields.Many2one("hospital.doctor")
    age = fields.Integer(string='Age')
    note1 = fields.Text(string='Noteghi chu')
    state1 = fields.Selection([
        ('draft', 'Draft'), ('confirm', 'Confirmed'), ('done', 'Done'), ('cancel', 'Cancelled')
    ], string='Status', default='draft')
    medicine = fields.Char(string='medicine')
    date_appointment = fields.Date(string='Date')
    date_checkup = fields.Datetime(string='checkuptime')
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ], required=True, default='male', tracking=True)
    appoiment_count = fields.Integer(string='appointment count', compute='compute_appointment_count')
    description = fields.Char(string='des')
    other_info = fields.Char(string='other info')
    prescription_line_ids = fields.One2many('appointment.prescription.lines', "appointment_id",
                                            string="Prescription lines")

    @api.depends('patient_id')
    def compute_appointment_count(self):
        for record in self:
            if record.patient_id:
                appointment_count = self.env['hospital1.appointment'].search_count([
                    ('patient_id', '=', record.patient_id.id),
                    ('state1', 'in', ['draft', 'confirm', 'done']),  # Include the states you want to count
                ])
                record.appoiment_count = appointment_count
            else:
                record.appoiment_count = 0

    @api.model
    def action_confirm1(self):
        self.state = 'confirm'

    @api.model
    def action_done1(self):
        self.state = 'done'

    @api.model
    def action_draft1(self):
        self.state = 'draft'

    @api.model
    def action_cancel1(self):
        self.state = 'cancel'

    @api.onchange('patient_id')  # neu thay doi patient id thi may cai duoi thay doi theo tuy chon cua minh
    def onchange_patient_id(self):
        if self.patient_id:
            if self.patient_id.gender:
                self.gender = self.patient_id.gender
            if self.patient_id.note:
                self.note1 = self.patient_id.note
            if self.patient_id.age:
                self.age = self.patient_id.age

        else:
            self.gender = ''
            self.note1 = ''
            self.age = ''


class AppointmentPrescriptionLines(models.Model):
    _name = "appointment.prescription.lines"
    _description = "Appointment Prescription Lines"

    name = fields.Char(string="medicine")
    qty = fields.Integer(string="quantity")
    appointment_id = fields.Many2one('hospital1.appointment', string='appointment')
