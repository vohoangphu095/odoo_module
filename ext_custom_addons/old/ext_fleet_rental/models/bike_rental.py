# -*- coding: utf-8 -*-
from email.policy import default

from odoo import api, fields, models, _
from odoo.exceptions import Warning
from odoo.exceptions import ValidationError
from odoo import tools
import string
import logging
import base64
from psycopg2 import Error, OperationalError
from odoo.addons import decimal_precision as dp
from odoo.tools import float_is_zero, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
from datetime import date, datetime, time, timedelta
from odoo.exceptions import UserError
from odoo.modules.module import get_module_resource


class BikeRental(models.Model):
    _name = 'bike.rental'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Hợp Đồng Thuê Xe"

    name = fields.Char(string='Hợp Đồng Thuê Xe', required=True, copy=False, readonly=True,
                       index=True, default=lambda self: _('New'))
    partner_id = fields.Many2one('res.partner', string="Contact")
    partner_phone = fields.Char(related='partner_id.phone', reayonly=True, string='Phone', required=True,
                                track_visibility='onchange')
    partner_cmnd = fields.Char(related='partner_id.cmnd', readonly=True, string='CMND/CCCD/PassPost', required=True,
                               track_visibility='onchange')
    full_name = fields.Char(related='partner_id.name', readonly=True, string='Tên Người Thuê',
                            track_visibility='onchange')

    sequence = fields.Integer(string='Sequence', default=10)

    # @api.model
    # def _default_image(self):
    #     image_path = get_module_resource('hr', 'static/src/img', 'default_image.png')
    #     return tools.image_resize_image_big(base64.b64encode(open(image_path, 'rb').read()))
    #
    # image = fields.Binary(
    #     "Photo", default=_default_image, attachment=True,
    #     help="This field holds the image used as photo for the employee, limited to 1024x1024px.")
    # image_128 = fields.Image("Image", max_width=128, max_height=128)
    state = fields.Selection(
        [('create', 'Create'),
         ('running', 'Running'),
         ('confirm', 'Confirm'),
         ('invoice', 'Invoice'),
         ('cancel', 'Cancel'),
         ('done', 'Done')],
        string="State", default="create", copy=False, track_visibility='always')

    @api.model
    def _get_user_currency(self):
        currency_id = self.env['res.users'].browse(self._uid).company_id.currency_id
        return currency_id or self._get_euro()

    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self._get_user_currency())

    company_id = fields.Many2one('res.company', string='Company', required=True, index=True,
                                 default=lambda self: self.env.user.company_id,
                                 help="Company related to this journal")
    date_start = fields.Datetime(string='Ngày Cho Thuê Xe', required=True)
    date_end = fields.Datetime(string='Ngày Trả Xe')
    discount = fields.Selection([('giam15', 'Giảm 15%'), ('giam30', 'Giảm 30%')], string='Giảm giá cho khách',
                                track_visibility='onchange')
    date_order = fields.Datetime(string='Order Date', required=True, readonly=True, index=True,
                                 states={'create': [('readonly', False)]}, copy=False,
                                 default=fields.Datetime.now)

    team_id = fields.Many2one('crm.team', string='Rental Team Chanel', required=True, )

    # tao ddown tăng dần theo sale team
    # @api.model
    # def create(self, vals):
    #     if vals.get('name', '/') == '/' and vals.get('team_id'):
    #         asset_team = self.env['crm.team'].browse(vals['team_id'])
    #         if asset_team.sequence_id:
    #             vals['name'] = asset_team.sequence_id.next_by_id()
    #     return super(BtAsset, self).create(vals)

    payment_term_id = fields.Many2one('account.payment.term', string='Payment Terms', oldname='payment_term')

    note = fields.Text('Description')
    gop_y = fields.Text('Description')

    @api.model
    def _default_warehouse_id(self):
        company = self.env.user.company_id.id
        warehouse_ids = self.env['stock.warehouse'].search([('company_id', '=', company)], limit=1)
        return warehouse_ids

    warehouse_id = fields.Many2one('stock.warehouse', string="Cửa Hàng Cho Thuê", default=_default_warehouse_id)

    @api.onchange('warehouse_id')
    def _onchange_warehouse_id(self):
        self.warehouse_to_location = self.warehouse_id

    warehouse_to_location = fields.Many2one('stock.warehouse', string="Cửa Hàng Trả Xe", track_visibility='onchange')

    @api.model
    def create(self, vals):
        obj = super(BikeRental, self).create(vals)
        if obj.name == 'New':
            number = self.env['ir.sequence'].next_by_code('bike.rental.sequence.code')
            obj.write({'name': number})
        return obj

    bike_rental_line = fields.One2many('bike.rental.line', 'bike_rental_id', string="Xe Thuê", create=False)
    amount_time = fields.Float(string='Taxes', store=True, readonly=True, default=0)
    amount_untaxed = fields.Monetary(string='Chưa Giảm Giá', store=True, readonly=True, default=0)
    amount_tax = fields.Monetary(string='Giảm Giá', store=True, readonly=True, default=0)
    amount_total = fields.Monetary(string='Tổng Cộng', store=True, readonly=True, default=0)

    def action_running(self):
        lot_bike = []
        for line in self.bike_rental_line:
            bike_lot_find = line.bike_id.bike_lot
            for lot in lot_bike:
                if bike_lot_find == lot:
                    raise UserError(_('Trùng xe rồi!'))
            lot_bike.append(bike_lot_find)

        for line1 in self.bike_rental_line:
            line1.bike_id.update({
                'state': 'running',
            })
        return self.write({'state': 'running'})

    # def action_running(self):
    #     lot_bike = []
    #     for line in self.bike_rental_line:
    #         bike_lot_find = line.bike_id.bike_lot
    #         for lot in lot_bike:
    #             if bike_lot_find == lot:
    #                 raise UserError(_('Trùng xe rồi!'))
    #         lot_bike.append(bike_lot_find)
    #
    #     for line1 in self.bike_rental_line:
    #         line1.bike_id.update({
    #             'state': 'running',
    #         })
    #     return self.write({'state': 'running'})

    @api.onchange('date_end')
    def check_date_end(self):
        mes = ''
        if self.date_end:
            bike_star = self.date_start
            bike_end = self.date_end

            date_format = "%Y-%m-%d %H:%M:%S"
            bike_date_start = datetime.strptime(bike_star, date_format)
            bike_date_end = datetime.strptime(bike_end, date_format)
            if bike_date_start > bike_date_end:
                raise UserError('Ngày trả xe phải sau ngày mượn xe!')

    def action_cancel(self):
        if self.state == 'running' or self.state == 'create':
            return self.update({'state': 'cancel'})
        else:
            raise UserError('Không được bỏ đơn này!')

    def action_confirm(self):
        if not self.date_end:
            raise UserError(_('Chưa Nhập Ngày/Giờ Trả Xe!'))
        if self.date_end:
            bike_star = self.date_start
            bike_end = self.date_end

            date_format = "%Y-%m-%d %H:%M:%S"
            bike_date_start = datetime.strptime(bike_star, date_format)
            bike_date_end = datetime.strptime(bike_end, date_format)

            time_total = bike_date_end - bike_date_start
            time_date_hour = time_total.days * 24
            time_house = time_total.seconds // 3600
        amount_time = time_date_hour + time_house

        amount_money = 0
        if amount_time > 24:
            amount_money = 120000
            # while amount_time_count = 0:
            #     amount_time_count = amount_time/24
        if 9 <= amount_time and amount_time < 24:
            amount_money = 80000
        if 6 <= amount_time and amount_time < 9:
            amount_money = 70000
        if amount_time < 6:
            amount_money = 30000

        amout_bike_rental_line = 0
        for line in self.bike_rental_line:
            if line.bike_id.bike_lot:
                price_unit = amount_money
                discount = 0
                if self.discount == 'giam15':
                    discount = 15
                if self.discount == 'giam30':
                    discount = 30
                if not self.discount:
                    discount = 0
                line.update({
                    'price_unit': price_unit,
                    'discount': discount,
                })

                line_qty = line.bike_id.bike_qty + 1
                line_hour = line.bike_id.bike_hour + amount_time
                amout_bike_rental_line += 1
                line_bike_state = line.bike_state
                state = ''
                if line_bike_state == 'error':
                    state = 'error'
                if line_bike_state == 'ready':
                    state = 'ready'
                if state == '':
                    raise UserError(_('Chưa nhập trình trang xe khi nhận!'))
                line.bike_id.update({
                    'state': state,
                    'warehouse_id': self.warehouse_to_location,
                    'bike_qty': line_qty,
                    'bike_hour': line_hour,
                })

        amount_untaxed = amout_bike_rental_line * amount_money

        if self.discount == 'giam15':
            amount_tax = amount_untaxed * (15 / 100)
        if self.discount == 'giam30':
            amount_tax = amount_untaxed * (30 / 100)
        if not self.discount:
            amount_tax = 0

        self.update({
            'amount_time': amount_time,
            'amount_untaxed': self.currency_id.round(amount_untaxed),
            'amount_tax': self.currency_id.round(amount_tax),
            'amount_total': amount_untaxed - amount_tax,
        })
        for line1 in self.bike_rental_line:
            line.bike_id.update({
                'bike_hour': amount_time,
            })

        return self.write({'state': 'confirm'})

    def create_invoice(self):
        rental_id = self.id
        origin = self.name
        partner_id = self.partner_id.id
        company_id = self.company_id.id
        currency_id = self.currency_id.id
        account_id = self.partner_id.property_account_receivable_id.id,
        fiscal_position_id = self.partner_id.property_account_position_id.id
        team_id = self.team_id.id
        payment_term_id = self.payment_term_id.id
        # user_id: self.user_id.id
        comment: self.note
        amount_untaxed = self.amount_untaxed
        amount_tax = self.amount_tax
        amount_total = self.amount_total
        val = {
            'origin': origin,
            'type': 'out_invoice',
            'account_id': account_id,
            'partner_id': partner_id,
            'currency_id': currency_id,
            'journal_id': 62,
            'comment': 'Create by Bike Rental',
            'payment_term_id': payment_term_id,
            'fiscal_position_id': fiscal_position_id,
            'company_id': company_id,
            'user_id': False,
            'team_id': team_id,
            'global_channel_id': False,
            'rental_id': rental_id,
            'incoterms_id': False,

        }
        self.env['account.invoice'].create(val)
        search_rental_invoice = self.env["account.invoice"].search(
            [('rental_id', '=', self.id), ('origin', '=', self.name)])

        invoice_line_ids = []
        for line in self.bike_rental_line:
            default_code = line.bike_sku
            search_product = line.env['product.product'].search([('default_code', '=', default_code)])
            value = {
                'name': search_product.display_name,
                'sequence': 10,
                'invoice_id': search_rental_invoice.id,
                'origin': self.name,
                'account_id': account_id,
                'product_id': search_product.id,
                'quantity': 1,
                'discount': line.discount,
                'uom_id': search_product.uom_id.id,
                'account_analytic_id': 127,
                'analytic_tag_ids': [[6, False, []]],
                'invoice_line_tax_ids': [[6, False, []]],
                'price_unit': line.price_unit,
            }
            self.env['account.invoice.line'].create(value)

        return self.write({'state': 'invoice'})

    def update_state_done(self):
        search_rental_invoice = self.env["account.invoice"].search(
            [('rental_id', '=', self.id), ('origin', '=', self.name)])
        if search_rental_invoice.state == 'paid':
            return self.write({'state': 'done'})
        else:
            raise UserError('Invoice chưa được thanh Toán(paid)!')


class BikeRentalLine(models.Model):
    _name = "bike.rental.line"

    bike_rental_id = fields.Many2one('bike.rental', string='Hợp Đồng Thuê Xe')
    bike_id = fields.Many2one('bike.vehicle', string='Xe Cho Thuê', create=False, )
    name = fields.Text(related='bike_id.name', string='Tên Xe', readonly=True)
    bike_sku = fields.Char(related='bike_id.bike_sku', string='SKU', readonly=True)
    bike_lot = fields.Char(related='bike_id.bike_lot', string='Số Khung Xe', readonly=True)
    bike_state = fields.Selection([('error', 'Xe Hỏng'), ('ready', 'Xe Bình Thường')], string='Trạng Thái')
    state = fields.Selection(related='bike_id.state', string='Tình Trạng Xe Hiện Tại')
    status = fields.Selection([('create', 'Create'),
                               ('running', 'Running'),
                               ('confirm', 'Confirm'),
                               ('invoice', 'Invoice'),
                               ('cancel', 'Cancel'),
                               ('done', 'Done')], related='bike_rental_id.state', string='State Của Bike Rental')

    price_unit = fields.Float(string='Giá Từng Xe', readonly=True, default=0)
    discount = fields.Float(string='Discount', readonly=True, default=0)

    def action_show_details(self):
        self.ensure_one()
        if self.state == 'running':
            view = self.env.ref('ext_fleet_rental.view_bike_rental_line_operation_form')
        else:
            raise UserError(_('Xe đang chạy mới được bấm!'))

        return {
            'name': _('Detailed Operations'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'bike.rental.line',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': self.id,
            'context': dict(
                self.env.context,
            ),
        }

    @api.onchange('bike_id')
    def check_warehouse(self):
        if self.bike_id:
            if self.bike_id.warehouse_id.id != self.bike_rental_id.warehouse_id.id:
                raise UserError(_('Xe bạn chọn không có trong Cửa Hàng : %s !') % self.bike_rental_id.warehouse_id.name)
            if self.bike_id.state != 'ready':
                raise UserError(_('Xe bạn chọn không trong trạng thái sản sàng!'))
