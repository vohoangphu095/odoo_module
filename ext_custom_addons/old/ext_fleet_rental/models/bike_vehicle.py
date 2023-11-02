# -*- coding: utf-8 -*-
from email.policy import default

from odoo import api, fields, models, _
from odoo.exceptions import Warning
from odoo.exceptions import ValidationError
from odoo import tools
import string
import logging
from psycopg2 import Error, OperationalError
from odoo.addons import decimal_precision as dp
from odoo.tools import float_is_zero, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
from datetime import date, datetime, time, timedelta
from odoo.exceptions import UserError


class BikeVehicle(models.Model):
    _name = 'bike.vehicle'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Xe Cho Thuê"

    bike_name = fields.Char(string='Tên Xe', required=True, track_visibility='onchange')
    bike_sku = fields.Char(string='Mã Xe', required=True, track_visibility='onchange')
    bike_lot = fields.Char(string='Số Khung Xe', required=True, track_visibility='onchange')
    bike_qty = fields.Integer(string='Số Lần Thuê')
    bike_hour = fields.Integer(string='Số Giờ Chạy')
    bike_size = fields.Selection([
        ('m', 'Size M'),
        ('l', 'Size L'),
        ('s', 'Size S'),
    ], required=True, track_visibility='onchange')
    state = fields.Selection([
        ('draft', 'Create'),
        ('running', 'Running'),
        ('error', 'Đang Lỗi'),
        ('ready', 'Sẳn Sàng')
    ], string='Status', readonly=True, copy=False, index=True, default="draft", track_visibility='always')
    company_id = fields.Many2one('res.company', string='Company', required=True, index=True,
                                 default=lambda self: self.env.user.company_id,
                                 help="Company related to this journal")
    warehouse_id = fields.Many2one('stock.warehouse', string="Cửa Hàng", track_visibility='onchange')
    bike_color = fields.Many2one('bike.color', string='Màu Xe', required=True, track_visibility='onchange')

    @api.depends('bike_sku', 'bike_lot', 'bike_name', 'bike_size', 'bike_color')
    def _compute_name(self):
        for item in self:
            val = '[' + item.bike_sku + ']' + '[' + item.bike_lot + ']' + item.bike_name
            item.update({
                'name': val
            })

    name = fields.Text(string="Tên Xe", compute=_compute_name)

    def action_ready(self):
        return self.write({'state': 'ready'})

    @api.onchange('bike_lot')
    def change_bike_lot(self):
        mes = ''
        if self.bike_lot:
            obj = self.env['bike.vehicle'].search([])
            for i in obj:
                a = self.bike_lot
                b = i.bike_lot
                if self.bike_lot.strip() == i.bike_lot.strip():
                    mes = _('%s có số khung %s đã tồn tại ở cửa hàng %s') % (
                        self.bike_name, self.bike_lot, i.warehouse_id.name)
            if mes != '':
                raise UserError(_(mes))

    # check tao moi xe
    # @api.model
    # def _check_bike(self, vals):
    #     mes = ''
    #     obj = self.env['bike.vehicle'].search([])
    #     for i in obj:
    #         line1 = vals.get('bike_lot')
    #         line2 = i.bike_lot
    #         if (vals.get('bike_lot')).strip() == (i.bike_lot).strip():
    #             mes = _('%s có số khung %s đã tồn tại ở cửa hàng %s') % (
    #                 vals.get('bike_name'), vals.get('bike_lot'), i.warehouse_id.name)
    #     if mes != '':
    #         raise UserError(_(mes))
    # @api.model
    # def create(self, vals):
    #     self._check_bike(vals)
    #     return super(BikeVehicle, self).create(vals)
    # *****************************


class Color(models.Model):
    _name = 'bike.color'

    name = fields.Char(string="Màu")
