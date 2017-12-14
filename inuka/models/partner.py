# -*- coding: utf-8 -*-

import random
import string
import re
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from random import randint

from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from odoo.exceptions import ValidationError


class Users(models.Model):
    _inherit = "res.users"

    @api.model
    def create(self, vals):
        return super(Users, self.with_context(from_user=True)).create(vals)

class ResPartner(models.Model):
    _inherit = 'res.partner'

    first_name = fields.Char("First Name")
    last_name = fields.Char("Last Name")
    passport_no = fields.Char("ID/Passport No")
    home_phone = fields.Char("Home Phone")
    join_date = fields.Date("Join Date")
    dob = fields.Date("DOB")
    status = fields.Selection([
        ('candidate', 'Candidate'),
        ('new', 'New'),
        ('junior', 'Junior'),
        ('senior', 'Senior'),
        ('pearl', 'Pearl'),
        ('ruby', 'Ruby'),
        ('emerald', 'Emerald'),
        ('sapphire', 'Sapphire'),
        ('diamond', 'Diamond'),
        ('double_diamond', 'Double Diamond'),
        ('triple_diamond', 'Triple Diamond'),
        ('exective_diamond', 'Exective Diamond'),
        ('presidential', 'Presidential')
        ], string='Status', required=True, default='candidate')
    upline = fields.Many2one("res.partner", string="Upline")
    upline_id = fields.Char(related="upline.ref", string="Upline ID")
    candidate_registrar = fields.Boolean("Candidate Registrar")
    bulk_custodian = fields.Boolean("Bulk Custodian")
    up_front_kits = fields.Boolean("Up-front Kits")
    personal_pv = fields.Float("Personal PV")
    pv_downline_1 = fields.Float("PV Downline 1")
    pv_downline_2 = fields.Float("PV Downline 2")
    pv_downline_3 = fields.Float("PV Downline 3")
    pv_downline_4 = fields.Float("PV Downline 4")
    pv_tot_group = fields.Float("PV Tot Group")
    personal_members = fields.Integer("Active Personal Members")
    new_members = fields.Integer("New Members")
    kit = fields.Selection([
        ('small', 'Small Kit'),
        ('medium', 'Medium Kit'),
        ('large', 'Large Kit'),
        ('junior', 'Junior kit'),
        ('senior', 'Senior kit'),
        ('not_indicated', 'Kit Not Indicated')
        ], string='Kit', required=True, default='small')
    source = fields.Selection([
        ('email', 'Email'),
        ('facebook', 'Facebook'),
        ('fax', 'Fax'),
        ('inuka', 'Inuka'),
        ('phone', 'Phone'),
        ('sms', 'SMS'),
        ('whatsapp', 'Whatsapp'),
        ('portal', 'Portal')
        ], string='Source', required=True, default='email')
    is_admin = fields.Boolean(compute="_compute_is_admin", string="Admin")

#     _sql_constraints = [
#         ('mobile_uniq', 'unique(mobile)', 'Mobile should be unique.'),
#         ('email_uniq', 'unique(email)', 'Email should be unique.'),
#         ('ref_uniq', 'unique(ref)', 'Internal Reference should be unique.'),
#     ]

    def _compute_is_admin(self):
        for partner in self:
            if partner.env.user._is_superuser():
                partner.is_admin = True
            else:
                partner.is_admin = False

#     @api.constrains('dob')
#     def _check_dob(self):
#         for partner in self:
#             if partner.dob:
#                 dob = datetime.strptime(partner.dob, DF)
#                 today = date.today()
#                 age = relativedelta(today, dob)
#                 if age.years < 18:
#                     raise ValidationError(_('Member should be 18 years and above.'))
# 
#     @api.constrains('mobile')
#     def _check_mobile(self):
#         for partner in self:
#             if partner.mobile:
#                 if ' ' in partner.mobile:
#                     raise ValidationError(_('Mobile Number should not have any space.'))
#                 mobile = partner.mobile.replace(' ', '')
#                 if len(mobile) < 11:
#                     raise ValidationError(_('Mobile Number should not be less than 11 digits.'))

    @api.onchange('first_name', 'last_name')
    def _onchange_first_name(self):
        if self.customer:
            name = ''
            if self.first_name:
                name += (self.first_name)
            if self.last_name:
                name += ' ' + (self.last_name)
            if self.ref:
                name += ' (' + (self.ref) +')'
            self.name = name

    def _prepare_sale_order(self):
        self.ensure_one()

        kit = self.kit
        vals = {
            'small': 600.00,
            'medium': 1300.00,
            'large': 1800.00,
            'junior': 3000.00,
            'senior': 6000.00,
            'not_indicated': 0.00,
        }
        order_total = vals.get(kit, 0.00)

        product_vals = {
            'small': 'KITSM',
            'medium': 'KITMD',
            'large': 'KITLG',
            'junior': 'KITJR',
            'senior': 'KITSR'
        }
        default_code = product_vals.get(kit)
        product = self.env['product.product']
        if default_code:
            product = product.search([('default_code', '=', default_code)], limit=1)

        return {
            'partner_id': self.id,
            'kit_order': True,
            'order_sent_by': self.source,
            'sale_date': self.join_date,
            'order_type': 'single',
            'pricelist_id': self.property_product_pricelist.id,
            'carrier_id': False,
            'payment_term_id': self.env.ref('account.account_payment_term_immediate').id,
            'pv': product.categ_id.category_pv,
            'order_total': order_total,
            'product_cost': order_total,
            'picking_policy': 'one',
            'user_id': self.create_uid.id,
            'team_id': False,
            'client_order_ref': kit,
            'company_id': self.company_id.id,
        }

    def _prepare_sale_order_line(self, order):
        self.ensure_one()

        vals = {
            'small': 'KITSM',
            'medium': 'KITMD',
            'large': 'KITLG',
            'junior': 'KITJR',
            'senior': 'KITSR'
        }
        default_code = vals.get(self.kit)
        product = self.env['product.product']
        if default_code:
            product = product.search([('default_code', '=', default_code)], limit=1)

        if not product:
            return {}
        return {
            'product_id': product.id,
            'product_uom_qty': 1.0,
            'order_id': order.id,
            'pv': product.categ_id.category_pv,
        }

    @api.model
    def create(self, vals):
        context = dict(self.env.context or {})
        if vals.get('customer') and not context.get('from_user', False):
            first_name = vals.get('first_name', '')
            last_name = vals.get('last_name', '')
            vals['ref'] = ''.join(random.choice(string.ascii_letters).upper() for x in range(3)) + (str(randint(100,999)))
            vals['name'] = ''
            if first_name:
                vals['name'] += (first_name)
            if last_name:
                vals['name'] += ' ' + (last_name)
            if vals['ref']:
                 vals['name'] += ' (' + (vals['ref']) +')'
        res = super(ResPartner, self).create(vals)
        if res.customer and not context.get('from_user', False):
            sale_order_vals = res._prepare_sale_order()
            order = self.env['sale.order'].create(sale_order_vals)
            sale_order_line_vals = res._prepare_sale_order_line(order)
            if sale_order_line_vals:
                self.env['sale.order.line'].create(sale_order_line_vals)

            if res.mobile:
                sms_template = self.env.ref('sms_frame.sms_template_inuka_international')
                msg_compose = self.env['sms.compose'].create({
                    'record_id': res.id,
                    'model': 'res.partner',
                    'sms_template_id': sms_template.id,
                    'from_mobile_id': self.env.ref('sms_frame.sms_number_inuka_international').id,
                    'to_number': res.mobile,
                    'sms_content': """ INUKA Welcomes YOU^Thank you for your Registration^ %s %s,your MemberID %s will be active once Kit payment is receipted^More info 27219499850""" %(res.first_name, res.last_name, res.ref)
                })
                msg_compose.send_entity()

            if res.upline.mobile:
                sms_template = self.env.ref('sms_frame.sms_template_inuka_international_referrer')
                msg_compose = self.env['sms.compose'].create({
                    'record_id': res.upline.id,
                    'model': 'res.partner',
                    'sms_template_id': sms_template.id,
                    'from_mobile_id': self.env.ref('sms_frame.sms_number_inuka_international').id,
                    'to_number': res.upline.mobile,
                    'sms_content': """ INUKA New Registration received^WELL DONE, %s^New MemberID %s for %s %s activated once kit is receipted^Info 27219499850""" %(res.upline.name, res.ref, res.first_name, res.last_name)
                })
                msg_compose.send_entity()

        return res

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []
        recs = self.search(['|', '|', '|', '|', ('ref', operator, name), ('name', operator, name), ('mobile', operator, name), ('passport_no', operator, name), ('email', operator, name)] + args, limit=limit)
        return recs.name_get()
