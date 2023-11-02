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


class ResPartner(models.Model):
    _inherit = 'res.partner'

    cmnd = fields.Char('CMND/CCCD/PassPost')
    inter_company = fields.Boolean('Internal Company')

