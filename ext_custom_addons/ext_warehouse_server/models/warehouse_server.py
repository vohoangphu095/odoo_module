from odoo import fields,api,models

class WarehouseServer (models.Model):
    _name='warehouse.server'

    server_po=fields.Char(string='Server PO: ')


    date_received=fields.Date(string='Date received')
    server_correction=fields.Selection([
        ('repair','Repair'),
        ('rework','Rework'),# repair with all old compoment
        ('harvest','Harvest'),#get part to wh
    ])
    recieve_location=fields.Selection([
        ('fab-9vn','Fab-9 VN'),
        ('fab-9us','Fab-9 US'),
    ])
    partner_id=fields.Many2one('res.partner',string='partner')
    server_info_id = fields.Many2one('server.info', string='Server Info')
    server_gen = fields.Selection(related='server_info_id.server_gen', string='Server Generation')
