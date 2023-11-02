from odoo import fields, models, api


class ProductVariant(models.Model):
    _inherit = 'product.template'

    server_info_id = fields.Many2one('server.info', string='Server Info')
    server_gen = fields.Selection(related='server_info_id.server_gen', string='Server Generation')
    rma = fields.Char(string='RMA#')
    serial = fields.Char(string='Server serial')
    rev = fields.Char(string='Server REV')
    base_unit = fields.Char(string='Base Unit')
    base_rev = fields.Char(string='Base REV')

    # them product type selection
    # detailed_type = fields.Selection(
    #     selection=[
    #         ('server', 'Server'),
    #         ('cable', 'Cable'),
    #         ('card', 'Card'),
    #         ('memory', 'Memory'),
    #     ],
    # )
