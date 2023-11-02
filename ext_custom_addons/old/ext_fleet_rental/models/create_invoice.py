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


class AccountInvoice(models.Model):
    _inherit = "account.move"

    rental_id = fields.Many2one('bike.rental', string='Rental Order Ref')


class AccountInvoiceLine(models.Model):
    _inherit = "account.move.line"

    rental_id = fields.Many2one('bike.rental', string='Rental Order Ref')

    @api.model
    def create(self, val):
        res = super(AccountInvoiceLine, self).create(val)
        return res
