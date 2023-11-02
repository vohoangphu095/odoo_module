from odoo import fields,  api,models

class ServerInfo(models.Model):
    _name='server.info'

    name=fields.Char(string='Server Part Number ')
    server_gen = fields.Selection([
        ('gen3', 'Gen 3'),
        ('gen4', 'Gen 4'),
        ('gen4.1', 'Gen 4.1'),
        ('gen4.2', 'Gen 4.2'),
        ('gen5', 'Gen 5'),
        ('other', 'Other')])
