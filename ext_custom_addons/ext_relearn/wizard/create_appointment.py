from odoo import fields, api, models, exceptions



class CreateAppointmentWizard(models.TransientModel):
    _name = "create.appointment.wizard"
    _description = "cretae appointment wizard"

    name = fields.Char(string="Name", required=True)
    patient_id = fields.Many2one('hospital1.patient',string="patient", required=True)

    def action_create_appointment(self):
        print('button clicked')