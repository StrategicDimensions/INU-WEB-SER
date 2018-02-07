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
        ], string='Status', required=True, default='candidate', track_visibility='onchange')
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
        ], string='Kit')
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
    is_active_mtd = fields.Boolean("Is Active (MTD)")
    is_new_mtd = fields.Boolean("Is New (MTD)")
    is_vr_earner_mtd = fields.Boolean("Is VR Earner (MTD)")
    is_new_senior_mtd = fields.Boolean("Is New & Senior Beyond (MTD)")
    is_new_junior_mtd = fields.Boolean("Is New & Junior Beyond (MTD)")
    is_new_ruby_mtd = fields.Boolean("Is New & Ruby & Beyond (MTD)")
    vr_earner = fields.Integer("# of VR Earners (MTD)")
    new_senior_recruits = fields.Integer("# of New Senior Recruits (MTD)")
    new_junior_recruits = fields.Integer("# of New Junior Recruits (MTD)")

    # QTD Performance Tab
    personal_pv_qtd = fields.Float("Personal PV (QTD)")
    pv_downline_1_qtd = fields.Float("PV Downline 1 (QTD)")
    pv_downline_2_qtd = fields.Float("PV Downline 2 (QTD)")
    pv_downline_3_qtd = fields.Float("PV Downline 3 (QTD)")
    pv_downline_4_qtd = fields.Float("PV Downline 4 (QTD)")
    pv_tot_group_qtd = fields.Float("Group PV (QTD)")
    personal_members_qtd = fields.Integer("# of Active Downline (QTD)")
    new_members_qtd = fields.Integer("# of New Members (QTD)")

    is_active_qtd = fields.Boolean("Is Active (QTD)")
    is_new_qtd = fields.Boolean("Is New (QTD)")
    is_vr_earner_qtd = fields.Boolean("Is VR Earner (QTD)")
    is_new_senior_qtd = fields.Boolean("Is New & Senior Beyond (QTD)")
    is_new_junior_qtd = fields.Boolean("Is New & Junior Beyond (QTD))")
    is_new_ruby_qtd = fields.Boolean("Is New & Ruby & Beyond (QTD)")
    vr_earner_qtd = fields.Integer("# of VR Earners (QTD)")
    new_senior_recruits_qtd = fields.Integer("# of New Senior Recruits (QTD)")
    new_junior_recruits_qtd = fields.Integer("# of New Junior Recruits (QTD)")

    # YTD Performance Tab
    personal_pv_ytd = fields.Float("Personal PV (YTD)")
    pv_downline_1_ytd = fields.Float("PV Downline 1 (YTD)")
    pv_downline_2_ytd = fields.Float("PV Downline 2 (YTD)")
    pv_downline_3_ytd = fields.Float("PV Downline 3 (YTD)")
    pv_downline_4_ytd = fields.Float("PV Downline 4 (YTD)")
    pv_tot_group_ytd = fields.Float("Group PV (YTD)")
    personal_members_ytd = fields.Integer("# of Active Downline (YTD)")
    new_members_ytd = fields.Integer("# of New Members (YTD)")

    is_active_ytd = fields.Boolean("Is Active (YTD)")
    is_new_ytd = fields.Boolean("Is New (YTD)")
    is_vr_earner_ytd = fields.Boolean("Is VR Earner (YTD)")
    is_new_senior_ytd = fields.Boolean("Is New & Senior Beyond (YTD)")
    is_new_junior_ytd = fields.Boolean("Is New & Junior Beyond (YTD))")
    is_new_ruby_ytd = fields.Boolean("Is New & Ruby & Beyond (YTD)")
    vr_earner_ytd = fields.Integer("# of VR Earners (YTD)")
    new_senior_recruits_ytd = fields.Integer("# of New Senior Recruits (YTD)")
    new_junior_recruits_ytd = fields.Integer("# of New Junior Recruits (YTD)")

    # MTD Odoo Tab
    o_personal_pv_mtd = fields.Float("O_Personal PV (MTD)")
    o_pv_downline_1_mtd = fields.Float("O_PV Downline 1 (MTD)")
    o_pv_downline_2_mtd = fields.Float("O_PV Downline 2 (MTD)")
    o_pv_downline_3_mtd = fields.Float("O_PV Downline 3 (MTD)")
    o_pv_downline_4_mtd = fields.Float("O_PV Downline 4 (MTD)")
    o_pv_tot_group_mtd = fields.Float("O_Group PV (MTD)")
    o_personal_members_mtd = fields.Integer("O_# of Active Downline (MTD)")
    o_new_members_mtd = fields.Integer("O_# of New Members (MTD)")

    o_is_active_mtd = fields.Boolean("O_Is Active (MTD)")
    o_is_new_mtd = fields.Boolean("O_Is New (MTD)")
    o_is_vr_earner_mtd = fields.Boolean("O_Is VR Earner (MTD)")
    o_is_new_senior_mtd = fields.Boolean("O_Is New & Senior Beyond (MTD)")
    o_is_new_junior_mtd = fields.Boolean("O_Is New & Junior Beyond (MTD))")
    o_is_new_ruby_mtd = fields.Boolean("O_Is New & Ruby & Beyond (MTD)")
    o_vr_earner_mtd = fields.Integer("O_# of VR Earners (MTD)")
    o_new_senior_recruits_mtd = fields.Integer("O_# of New Senior Recruits (MTD)")
    o_new_junior_recruits_mtd = fields.Integer("O_# of New Junior Recruits (MTD)")

    # QTD Odoo Tab
    o_personal_pv_qtd = fields.Float("O_Personal PV (QTD)")
    o_pv_downline_1_qtd = fields.Float("O_PV Downline 1 (QTD)")
    o_pv_downline_2_qtd = fields.Float("O_PV Downline 2 (QTD)")
    o_pv_downline_3_qtd = fields.Float("O_PV Downline 3 (QTD)")
    o_pv_downline_4_qtd = fields.Float("O_PV Downline 4 (QTD)")
    o_pv_tot_group_qtd = fields.Float("O_Group PV (QTD)")
    o_personal_members_qtd = fields.Integer("O_# of Active Downline (QTD)")
    o_new_members_qtd = fields.Integer("O_# of New Members (QTD)")

    o_is_active_qtd = fields.Boolean("O_Is Active (QTD)")
    o_is_new_qtd = fields.Boolean("O_Is New (QTD)")
    o_is_vr_earner_qtd = fields.Boolean("O_Is VR Earner (QTD)")
    o_is_new_senior_qtd = fields.Boolean("O_Is New & Senior Beyond (QTD)")
    o_is_new_junior_qtd = fields.Boolean("O_Is New & Junior Beyond (QTD))")
    o_is_new_ruby_qtd = fields.Boolean("O_Is New & Ruby & Beyond (QTD)")
    o_vr_earner_qtd = fields.Integer("O_# of VR Earners (QTD)")
    o_new_senior_recruits_qtd = fields.Integer("O_# of New Senior Recruits (QTD)")
    o_new_junior_recruits_qtd = fields.Integer("O_# of New Junior Recruits (QTD)")

    # YTD Odoo Tab
    o_personal_pv_ytd = fields.Float("O_Personal PV (YTD)")
    o_pv_downline_1_ytd = fields.Float("O_PV Downline 1 (YTD)")
    o_pv_downline_2_ytd = fields.Float("O_PV Downline 2 (YTD)")
    o_pv_downline_3_ytd = fields.Float("O_PV Downline 3 (YTD)")
    o_pv_downline_4_ytd = fields.Float("O_PV Downline 4 (YTD)")
    o_pv_tot_group_ytd = fields.Float("O_Group PV (YTD)")
    o_personal_members_ytd = fields.Integer("O_# of Active Downline (YTD)")
    o_new_members_ytd = fields.Integer("O_# of New Members (YTD)")

    o_is_active_ytd = fields.Boolean("O_Is Active (YTD)")
    o_is_new_ytd = fields.Boolean("O_Is New (YTD)")
    o_is_vr_earner_ytd = fields.Boolean("O_Is VR Earner (YTD)")
    o_is_new_senior_ytd = fields.Boolean("O_Is New & Senior Beyond (YTD)")
    o_is_new_junior_ytd = fields.Boolean("O_Is New & Junior Beyond (YTD))")
    o_is_new_ruby_ytd = fields.Boolean("O_Is New & Ruby & Beyond (YTD)")
    o_vr_earner_ytd = fields.Integer("O_# of VR Earners (YTD)")
    o_new_senior_recruits_ytd = fields.Integer("O_# of New Senior Recruits (YTD)")
    o_new_junior_recruits_ytd = fields.Integer("O_# of New Junior Recruits (YTD)")

    performance_history_count = fields.Integer(compute="_compute_performance_history_count", string="Performance History Count")
    rewards_count = fields.Integer(compute="_compute_rewards_count", string="Rewards Count")
    downline_count = fields.Integer(compute="_compute_downline_count", string="Downline Count")
    project_count = fields.Integer(compute="_compute_project_count", string="Project Count")
    sms_count = fields.Integer(compute="_compute_sms_count", string="SMS Count")
    property_product_pricelist = fields.Many2one(track_visibility='onchange')
    watchlist = fields.Boolean('Watchlist', default=False)

    device_id = fields.Char("Device ID", readonly=True)
    device_type = fields.Selection([
        ('android', 'Android'),
        ('iphone', 'iPhone'),
    ], string="Device Type", readonly=True)
    is_device_live = fields.Boolean("Is Device Live", readonly=True)
    portal_password = fields.Char("Portal Password")

    _sql_constraints = [
#         ('mobile_uniq', 'unique(mobile)', 'Mobile should be unique.'),
        ('email_uniq', 'unique(email)', 'Email should be unique.'),
        ('ref_uniq', 'unique(ref)', 'Internal Reference should be unique.'),
    ]

    @api.model
    def get_month_interval(self, current_date):
        first_date = current_date.replace(day = 7)
        next_first_date = current_date + relativedelta(day=1, months=1) # Getting 1st of next month
        last_date = next_first_date.replace(day = 6)
        return first_date, last_date

    @api.model
    def compute_mtd(self):
        Invoice = self.env['account.invoice']
        first_date, last_date = self.get_month_interval(date.today())
        partners = self.search([('customer', '=', True)], order='id desc')
        for partner in partners:
            invoices = Invoice.search([('partner_id', '=', partner.id), ('type', '=', 'out_invoice'), ('date_invoice', '>=', first_date), ('date_invoice', '<=', last_date), ('state', 'not in', ('draft', 'cancel'))])
            personal_pv_month =  sum(invoices.mapped('total_pv'))

            downline1_partner = partner.search([('upline', '=', partner.id), ('customer', '=', True)])
            downline1_invoices = Invoice.search([('partner_id', 'in', downline1_partner.ids), ('type', '=', 'out_invoice'), ('date_invoice', '>=', first_date), ('date_invoice', '<=', last_date), ('state', 'not in', ('draft', 'cancel'))])
            pv_downline_1_month = sum(downline1_invoices.mapped('total_pv'))

            downline2_partner = partner.search([('upline', 'in', downline1_partner.ids), ('customer', '=', True)])
            downline2_invoices = Invoice.search([('partner_id', 'in', downline2_partner.ids), ('type', '=', 'out_invoice'), ('date_invoice', '>=', first_date), ('date_invoice', '<=', last_date), ('state', 'not in', ('draft', 'cancel'))])
            pv_downline_2_month = sum(downline2_invoices.mapped('total_pv'))

            downline3_partner = partner.search([('upline', 'in', downline2_partner.ids), ('customer', '=', True)])
            downline3_invoices = Invoice.search([('partner_id', 'in', downline3_partner.ids), ('type', '=', 'out_invoice'), ('date_invoice', '>=', first_date), ('date_invoice', '<=', last_date), ('state', 'not in', ('draft', 'cancel'))])
            pv_downline_3_month = sum(downline3_invoices.mapped('total_pv'))

            downline4_partner = partner.search([('upline', 'in', downline3_partner.ids), ('customer', '=', True)])
            downline4_invoices = Invoice.search([('partner_id', 'in', downline4_partner.ids), ('type', '=', 'out_invoice'), ('date_invoice', '>=', first_date), ('date_invoice', '<=', last_date), ('state', 'not in', ('draft', 'cancel'))])
            pv_downline_4_month = sum(downline4_invoices.mapped('total_pv'))

            group_pv_month = personal_pv_month + pv_downline_1_month + pv_downline_2_month + pv_downline_3_month + pv_downline_4_month

            is_active_month = False
            if personal_pv_month >= 5:
                is_active_month = True

            is_new_month = False
            join_date = fields.Date.from_string(partner.join_date)
            if join_date and join_date >= first_date and join_date <= last_date:
                is_new_month = True

            is_vr_earner_month = False
            if personal_pv_month >= 20 and group_pv_month >= 45:
                is_vr_earner_month = True

            is_new_senior_month = False
            if is_new_month == True and partner.status in ('senior', 'pearl', 'ruby', 'emerald', 'sapphire', 'diamond', 'double_diamond', 'triple_diamond', 'exective_diamond', 'presidential'):
                is_new_senior_month = True

            is_new_junior_month = False
            if is_new_month == True and partner.status in ('junior', 'senior', 'pearl', 'ruby', 'emerald', 'sapphire', 'diamond', 'double_diamond', 'triple_diamond', 'exective_diamond', 'presidential'):
                is_new_junior_month = True

            is_new_ruby_month = False
            if is_new_month == True and partner.status in ('ruby', 'emerald', 'sapphire', 'diamond', 'double_diamond', 'triple_diamond', 'exective_diamond', 'presidential'):
                is_new_ruby_month = True

            personal_members_month = len(downline1_partner.filtered(lambda partner: partner.o_is_active_mtd)) # of Active Downline (MTD)
            new_members_month = len(downline1_partner.filtered(lambda partner: partner.o_is_new_mtd)) # of New Members (MTD)
            vr_earner_month = len(downline1_partner.filtered(lambda partner: partner.o_is_vr_earner_mtd)) # of VR Earners (MTD)
            new_senior_recruits_month = len(downline1_partner.filtered(lambda partner: partner.o_is_new_mtd and partner.status in ('senior', 'pearl', 'ruby', 'emerald', 'sapphire', 'diamond', 'double_diamond', 'triple_diamond','exective_diamond', 'presidential'))) # of New Senior Recruits (MTD)
            new_junior_recruits_month = len(downline1_partner.filtered(lambda partner: partner.o_is_new_mtd and partner.status in ('junior','senior', 'pearl', 'ruby', 'emerald', 'sapphire', 'diamond', 'double_diamond', 'triple_diamond','exective_diamond', 'presidential'))) # of New Junior Recruits (MTD)

            partner_dict = {
                'o_personal_pv_mtd': personal_pv_month,
                'o_pv_downline_1_mtd': pv_downline_1_month,
                'o_pv_downline_2_mtd': pv_downline_2_month,
                'o_pv_downline_3_mtd': pv_downline_3_month,
                'o_pv_downline_4_mtd': pv_downline_4_month,
                'o_pv_tot_group_mtd': group_pv_month,
                'o_personal_members_mtd': personal_members_month,
                'o_new_members_mtd': new_members_month,
                'o_is_active_mtd': is_active_month,
                'o_is_new_mtd': is_new_month,
                'o_is_vr_earner_mtd': is_vr_earner_month,
                'o_is_new_senior_mtd': is_new_senior_month,
                'o_is_new_junior_mtd': is_new_junior_month,
                'o_is_new_ruby_mtd': is_new_ruby_month,
                'o_vr_earner_mtd': vr_earner_month,
                'o_new_senior_recruits_mtd': new_senior_recruits_month,
                'o_new_junior_recruits_mtd': new_junior_recruits_month,
            }
            partner.write(partner_dict)

    @api.model
    def get_quarter_interval(self, current_date):
        if current_date.month < 6 or (current_date.month == 6 and current_date.day < 7):
            current_year = current_date.year - 1
        elif current_date.month > 6 or (current_date.month == 6 and current_date.day > 6):
            current_year = current_date.year

        q1_start_date = date(current_year, 6, 7)
        q1_end_date = date(current_year, 9, 6)
        if current_date >= q1_start_date and current_date <= q1_end_date:
            return q1_start_date, q1_end_date

        q2_start_date = date(current_year, 9, 7)
        q2_end_date = date(current_year, 12, 6)
        if current_date >= q2_start_date and current_date <= q2_end_date:
            return q2_start_date, q2_end_date

        q3_start_date = date(current_year, 12, 7)
        q3_end_date = date(current_year+1, 3, 6)
        if current_date >= q3_start_date and current_date <= q3_end_date:
            return q3_start_date, q3_end_date

        q4_start_date = date(current_year+1, 3, 7)
        q4_end_date = date(current_year+1, 6, 6)
        if current_date >= q4_start_date and current_date <= q4_end_date:
            return q4_start_date, q4_end_date

    @api.model
    def compute_qtd(self):
        Invoice = self.env['account.invoice']
        first_date, last_date = self.get_quarter_interval(date.today())
        partners = self.search([('customer', '=', True)], order='id desc')
        for partner in partners:
            invoices = Invoice.search([('partner_id', '=', partner.id), ('type', '=', 'out_invoice'), ('date_invoice', '>=', first_date), ('date_invoice', '<=', last_date), ('state', 'not in', ('draft', 'cancel'))])
            personal_pv_quarter =  sum(invoices.mapped('total_pv'))

            downline1_partner = partner.search([('upline', '=', partner.id), ('customer', '=', True)])
            downline1_invoices = Invoice.search([('partner_id', 'in', downline1_partner.ids), ('type', '=', 'out_invoice'), ('date_invoice', '>=', first_date), ('date_invoice', '<=', last_date), ('state', 'not in', ('draft', 'cancel'))])
            pv_downline_1_quarter = sum(downline1_invoices.mapped('total_pv'))

            downline2_partner = partner.search([('upline', 'in', downline1_partner.ids), ('customer', '=', True)])
            downline2_invoices = Invoice.search([('partner_id', 'in', downline2_partner.ids), ('type', '=', 'out_invoice'), ('date_invoice', '>=', first_date), ('date_invoice', '<=', last_date), ('state', 'not in', ('draft', 'cancel'))])
            pv_downline_2_quarter = sum(downline2_invoices.mapped('total_pv'))

            downline3_partner = partner.search([('upline', 'in', downline2_partner.ids), ('customer', '=', True)])
            downline3_invoices = Invoice.search([('partner_id', 'in', downline3_partner.ids), ('type', '=', 'out_invoice'), ('date_invoice', '>=', first_date), ('date_invoice', '<=', last_date), ('state', 'not in', ('draft', 'cancel'))])
            pv_downline_3_quarter = sum(downline3_invoices.mapped('total_pv'))

            downline4_partner = partner.search([('upline', 'in', downline3_partner.ids), ('customer', '=', True)])
            downline4_invoices = Invoice.search([('partner_id', 'in', downline4_partner.ids), ('type', '=', 'out_invoice'), ('date_invoice', '>=', first_date), ('date_invoice', '<=', last_date), ('state', 'not in', ('draft', 'cancel'))])
            pv_downline_4_quarter = sum(downline4_invoices.mapped('total_pv'))

            group_pv_quarter = personal_pv_quarter + pv_downline_1_quarter + pv_downline_2_quarter + pv_downline_3_quarter + pv_downline_4_quarter

            is_active_quarter = False
            if personal_pv_quarter >= 15:
                is_active_quarter = True

            is_new_quarter = False
            join_date = fields.Date.from_string(partner.join_date)
            if join_date and join_date >= first_date and join_date <= last_date:
                is_new_quarter = True

            is_vr_earner_quarter = False
            if personal_pv_quarter >= 60 and group_pv_quarter >= 135:
                is_vr_earner_quarter = True

            is_new_senior_quarter = False
            if is_new_quarter == True and partner.status in ('senior', 'pearl', 'ruby', 'emerald', 'sapphire', 'diamond', 'double_diamond', 'triple_diamond', 'exective_diamond', 'presidential'):
                is_new_senior_quarter = True

            is_new_junior_quarter = False
            if is_new_quarter == True and partner.status in ('junior', 'senior', 'pearl', 'ruby', 'emerald', 'sapphire', 'diamond', 'double_diamond', 'triple_diamond', 'exective_diamond', 'presidential'):
                is_new_junior_quarter = True

            is_new_ruby_quarter = False
            if is_new_quarter == True and partner.status in ('ruby', 'emerald', 'sapphire', 'diamond', 'double_diamond', 'triple_diamond', 'exective_diamond', 'presidential'):
                is_new_ruby_quarter = True

            personal_members_quarter = len(downline1_partner.filtered(lambda partner: partner.o_is_active_qtd)) # of Active Downline (QTD)
            new_members_quarter = len(downline1_partner.filtered(lambda partner: partner.o_is_new_qtd)) # of New Members (QTD)
            vr_earner_quarter = len(downline1_partner.filtered(lambda partner: partner.o_is_vr_earner_qtd)) # of VR Earners (QTD)
            new_senior_recruits_quarter = len(downline1_partner.filtered(lambda partner: partner.o_is_new_qtd and partner.status in ('senior', 'pearl', 'ruby', 'emerald', 'sapphire', 'diamond', 'double_diamond', 'triple_diamond','exective_diamond', 'presidential'))) # of New Senior Recruits (QTD)
            new_junior_recruits_quarter = len(downline1_partner.filtered(lambda partner: partner.o_is_new_qtd and partner.status in ('junior','senior', 'pearl', 'ruby', 'emerald', 'sapphire', 'diamond', 'double_diamond', 'triple_diamond','exective_diamond', 'presidential'))) # of New Junior Recruits (QTD)

            partner_dict = {
                'o_personal_pv_qtd': personal_pv_quarter,
                'o_pv_downline_1_qtd': pv_downline_1_quarter,
                'o_pv_downline_2_qtd': pv_downline_2_quarter,
                'o_pv_downline_3_qtd': pv_downline_3_quarter,
                'o_pv_downline_4_qtd': pv_downline_4_quarter,
                'o_pv_tot_group_qtd': group_pv_quarter,
                'o_personal_members_qtd': personal_members_quarter,
                'o_new_members_qtd': new_members_quarter,
                'o_is_active_qtd': is_active_quarter,
                'o_is_new_qtd': is_new_quarter,
                'o_is_vr_earner_qtd': is_vr_earner_quarter,
                'o_is_new_senior_qtd': is_new_senior_quarter,
                'o_is_new_junior_qtd': is_new_junior_quarter,
                'o_is_new_ruby_qtd': is_new_ruby_quarter,
                'o_vr_earner_qtd': vr_earner_quarter,
                'o_new_senior_recruits_qtd': new_senior_recruits_quarter,
                'o_new_junior_recruits_qtd': new_junior_recruits_quarter,
            }
            partner.write(partner_dict)

    @api.model
    def get_year_interval(self, current_date):
        if current_date.month < 6 or (current_date.month == 6 and current_date.day < 7):
            current_year = current_date.year - 1
        elif current_date.month > 6 or (current_date.month == 6 and current_date.day > 6):
            current_year = current_date.year

        start_date = date(current_year, 6, 7)
        end_date = date(current_year+1, 6, 6)
        return start_date, end_date

    @api.model
    def compute_ytd(self):
        Invoice = self.env['account.invoice']
        first_date, last_date = self.get_year_interval(date.today())
        partners = self.search([('customer', '=', True)], order='id desc')
        for partner in partners:
            invoices = Invoice.search([('partner_id', '=', partner.id), ('type', '=', 'out_invoice'), ('date_invoice', '>=', first_date), ('date_invoice', '<=', last_date), ('state', 'not in', ('draft', 'cancel'))])
            personal_pv_year =  sum(invoices.mapped('total_pv'))

            downline1_partner = partner.search([('upline', '=', partner.id), ('customer', '=', True)])
            downline1_invoices = Invoice.search([('partner_id', 'in', downline1_partner.ids), ('type', '=', 'out_invoice'), ('date_invoice', '>=', first_date), ('date_invoice', '<=', last_date), ('state', 'not in', ('draft', 'cancel'))])
            pv_downline_1_year = sum(downline1_invoices.mapped('total_pv'))

            downline2_partner = partner.search([('upline', 'in', downline1_partner.ids), ('customer', '=', True)])
            downline2_invoices = Invoice.search([('partner_id', 'in', downline2_partner.ids), ('type', '=', 'out_invoice'), ('date_invoice', '>=', first_date), ('date_invoice', '<=', last_date), ('state', 'not in', ('draft', 'cancel'))])
            pv_downline_2_year = sum(downline2_invoices.mapped('total_pv'))

            downline3_partner = partner.search([('upline', 'in', downline2_partner.ids), ('customer', '=', True)])
            downline3_invoices = Invoice.search([('partner_id', 'in', downline3_partner.ids), ('type', '=', 'out_invoice'), ('date_invoice', '>=', first_date), ('date_invoice', '<=', last_date), ('state', 'not in', ('draft', 'cancel'))])
            pv_downline_3_year = sum(downline3_invoices.mapped('total_pv'))

            downline4_partner = partner.search([('upline', 'in', downline3_partner.ids), ('customer', '=', True)])
            downline4_invoices = Invoice.search([('partner_id', 'in', downline4_partner.ids), ('type', '=', 'out_invoice'), ('date_invoice', '>=', first_date), ('date_invoice', '<=', last_date), ('state', 'not in', ('draft', 'cancel'))])
            pv_downline_4_year = sum(downline4_invoices.mapped('total_pv'))

            group_pv_year = personal_pv_year + pv_downline_1_year + pv_downline_2_year + pv_downline_3_year + pv_downline_4_year

            is_active_year = False
            if personal_pv_year >= 60:
                is_active_year = True

            is_new_year = False
            join_date = fields.Date.from_string(partner.join_date)
            if join_date and join_date >= first_date and join_date <= last_date:
                is_new_year = True

            is_vr_earner_year = False
            if personal_pv_year >= 160 and group_pv_year >= 540:
                is_vr_earner_year = True

            is_new_senior_year = False
            if is_new_year == True and partner.status in ('senior', 'pearl', 'ruby', 'emerald', 'sapphire', 'diamond', 'double_diamond', 'triple_diamond', 'exective_diamond', 'presidential'):
                is_new_senior_year = True

            is_new_junior_year = False
            if is_new_year == True and partner.status in ('junior', 'senior', 'pearl', 'ruby', 'emerald', 'sapphire', 'diamond', 'double_diamond', 'triple_diamond', 'exective_diamond', 'presidential'):
                is_new_junior_year = True

            is_new_ruby_year = False
            if is_new_year == True and partner.status in ('ruby', 'emerald', 'sapphire', 'diamond', 'double_diamond', 'triple_diamond', 'exective_diamond', 'presidential'):
                is_new_ruby_year = True

            personal_members_year = len(downline1_partner.filtered(lambda partner: partner.o_is_active_ytd)) # of Active Downline (YTD)
            new_members_year = len(downline1_partner.filtered(lambda partner: partner.o_is_new_ytd)) # of New Members (YTD)
            vr_earner_year = len(downline1_partner.filtered(lambda partner: partner.o_is_vr_earner_ytd)) # of VR Earners (YTD)
            new_senior_recruits_year = len(downline1_partner.filtered(lambda partner: partner.o_is_new_ytd and partner.status in ('senior', 'pearl', 'ruby', 'emerald', 'sapphire', 'diamond', 'double_diamond', 'triple_diamond','exective_diamond', 'presidential'))) # of New Senior Recruits (YTD)
            new_junior_recruits_year = len(downline1_partner.filtered(lambda partner: partner.o_is_new_ytd and partner.status in ('junior','senior', 'pearl', 'ruby', 'emerald', 'sapphire', 'diamond', 'double_diamond', 'triple_diamond','exective_diamond', 'presidential'))) # of New Junior Recruits (YTD)

            partner_dict = {
                'o_personal_pv_ytd': personal_pv_year,
                'o_pv_downline_1_ytd': pv_downline_1_year,
                'o_pv_downline_2_ytd': pv_downline_2_year,
                'o_pv_downline_3_ytd': pv_downline_3_year,
                'o_pv_downline_4_ytd': pv_downline_4_year,
                'o_pv_tot_group_ytd': group_pv_year,
                'o_personal_members_ytd': personal_members_year,
                'o_new_members_ytd': new_members_year,
                'o_is_active_ytd': is_active_year,
                'o_is_new_ytd': is_new_year,
                'o_is_vr_earner_ytd': is_vr_earner_year,
                'o_is_new_senior_ytd': is_new_senior_year,
                'o_is_new_junior_ytd': is_new_junior_year,
                'o_is_new_ruby_ytd': is_new_ruby_year,
                'o_vr_earner_ytd': vr_earner_year,
                'o_new_senior_recruits_ytd': new_senior_recruits_year,
                'o_new_junior_recruits_ytd': new_junior_recruits_year,
            }
            partner.write(partner_dict)

    def _compute_is_admin(self):
        for partner in self:
            if partner.env.user._is_superuser():
                partner.is_admin = True
            else:
                partner.is_admin = False

    @api.constrains('dob')
    def _check_dob(self):
        for partner in self:
            if partner.dob:
                dob = datetime.strptime(partner.dob, DF)
                today = date.today()
                age = relativedelta(today, dob)
                if age.years < 18:
                    raise ValidationError(_('Member should be 18 years and above.'))

    @api.constrains('mobile')
    def _check_mobile(self):
        for partner in self:
            if partner.mobile:
                if ' ' in partner.mobile:
                    raise ValidationError(_('Mobile Number should not have any space.'))
                mobile = partner.mobile.replace(' ', '')
                if len(mobile) < 11:
                    raise ValidationError(_('Mobile Number should not be less than 11 digits.'))
                if self.search_count([('mobile', '=', partner.mobile)]) > 1:
                    raise ValidationError(_('Mobile should be unique.'))

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
            order = self.env['sale.order'].with_context(kit_order=True).create(sale_order_vals)
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

    @api.model
    def check_birthday(self):
        customers = self.search([('customer', '=', True), ('status', 'in', ('new', 'junior', 'senior', 'pearl', 'ruby'))])
        today = datetime.today()
        for customer in customers:
            if customer.dob and customer.mobile:
                dob = datetime.strptime(customer.dob, DF)
                if dob.day == today.day and dob.month == today.month:
                    sms_template = self.env.ref('sms_frame.sms_template_inuka_international')
                    msg_compose = self.env['sms.compose'].create({
                        'record_id': customer.id,
                        'model': 'res.partner',
                        'sms_template_id': sms_template.id,
                        'from_mobile_id': self.env.ref('sms_frame.sms_number_inuka_international').id,
                        'to_number': customer.mobile,
                        'sms_content': """ INUKA Happy Birthday %s %s, sending you SMILES for every moment of your special day. Have a wonderful HAPPY BIRTHDAY. Your INUKA Team 27219499850""" %(customer.first_name, customer.last_name)
                    })
                    msg_compose.send_entity()

    @api.model
    def create_birthday_ticket(self):
        HelpDeskTicket = self.env['helpdesk.ticket']
        team = self.env['helpdesk.team'].search([('name', '=', 'Escalations')], limit=1)
        ticket_type = self.env['helpdesk.ticket.type'].search([('name', '=', 'Birthday')], limit=1)
        channel = self.env['mail.channel'].search([('name', '=', 'Escalations')], limit=1)
        customers = self.search([('customer', '=', True), ('status', 'in', ('emerald', 'sapphire', 'diamond', 'double_diamond', 'triple_diamond', 'exective_diamond', 'presidential'))])
        today = datetime.today() + relativedelta(days=1)
        for customer in customers:
            if customer.dob:
                dob = datetime.strptime(customer.dob, DF)
                if dob.day == today.day and dob.month == today.month:
                    ticket = HelpDeskTicket.create({
                        'name': """Birthday: %s %s - %s""" %(customer.first_name, customer.last_name, customer.dob),
                        'team_id': team.id,
                        'user_id': False,
                        'priority': '2',
                        'description': """Birthday: %s %s - %s""" %(customer.first_name, customer.last_name, customer.dob),
                        'partner_id': customer.id,
                        'mobile': customer.mobile,
                        'partner_email': customer.email,
                        'ticket_type_id': ticket_type.id,
                    })
                    if channel:
                        ticket.message_subscribe(channel_ids=[channel.id])

    @api.multi
    def create_helpdesk_ticket(self):
        HelpDeskTicket = self.env['helpdesk.ticket']
        team = self.env['helpdesk.team'].search([('name', '=', 'Escalations')], limit=1)
        ticket_type = self.env['helpdesk.ticket.type'].search([('name', '=', 'Other')], limit=1)
        channel = self.env['mail.channel'].search([('name', '=', 'Escalations')], limit=1)
        tag = self.env['helpdesk.tag'].search([('name', '=', 'Status Change')], limit=1)
        user = self.env['res.users'].search([('login', '=', 'alma@inuka.co.za')], limit=1)
        for customer in self:
            ticket = HelpDeskTicket.create({
                'name': """%s %s has achieved %s status""" %(customer.first_name, customer.last_name, customer.status),
                'team_id': team.id,
                'user_id': user.id,
                'priority': '2',
                'description': """%s %s has achieved %s status""" %(customer.first_name, customer.last_name, customer.status),
                'partner_id': customer.id,
                'mobile': customer.mobile,
                'partner_email': customer.email,
                'ticket_type_id': ticket_type.id,
                'tag_ids': [(6, 0, tag.ids)],
            })
            ticket.message_subscribe(channel_ids=[channel.id])

    def _compute_performance_history_count(self):
        PerformanceHistory = self.env['performance.history']
        for partner in self:
            partner.performance_history_count = PerformanceHistory.search_count([('partner_id', '=', partner.id)])

    def _compute_downline_count(self):
        for partner in self:
            partner.downline_count = partner.search_count([('upline', '=', partner.id), ('customer', '=', True)])

    def _compute_project_count(self):
        Project = self.env['project.project']
        for partner in self:
            partner.project_count = Project.search_count([('partner_id', '=', partner.id)])

    def _compute_sms_count(self):
        SmsMessage = self.env['sms.message']
        model_id = self.env['ir.model'].search([('model', '=', 'res.partner')], limit=1).id
        for partner in self:
            partner.sms_count = SmsMessage.search_count([('model_id', '=', model_id), ('record_id', '=', partner.id)])

    @api.multi
    def view_performance_history(self):
        self.ensure_one()
        performances = self.env['performance.history'].search([('partner_id', '=', self.id)])
        action = self.env.ref('inuka.action_performance_history_form').read()[0]
        action['domain'] = [('id', 'in', performances.ids)]
        return action

    def _compute_rewards_count(self):
        Rewards = self.env['inuka.reward']
        for partner in self:
            partner.rewards_count = Rewards.search_count([('partner_id', '=', partner.id)])

    @api.multi
    def view_rewards(self):
        self.ensure_one()
        rewards = self.env['inuka.reward'].search([('partner_id', '=', self.id)])
        action = self.env.ref('inuka.action_inuka_rewards_form').read()[0]
        action['domain'] = [('id', 'in', rewards.ids)]
        return action

    @api.multi
    def view_downline_member(self):
        self.ensure_one()
        partners = self.search([('upline', '=', self.id), ('customer', '=', True)])
        view_id = self.env.ref('inuka.view_res_partner_downline_tree').id

        return {
            'name': _('Downline'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'res.partner',
            'view_id': view_id,
            'context': self.env.context,
            'domain': [('id', 'in', partners.ids)],
        }

    @api.multi
    def view_project(self):
        self.ensure_one()
        projects = self.env['project.project'].search([('partner_id', '=', self.id)])
        action = self.env.ref('project.open_view_project_all').read()[0]
        action['domain'] = [('id', 'in', projects.ids)]
        return action

    @api.multi
    def view_sms_message(self):
        self.ensure_one()
        model_id = self.env['ir.model'].search([('model', '=', 'res.partner')], limit=1).id
        messages = self.env['sms.message'].search([('model_id', '=', model_id), ('record_id', '=', self.id)])

        return {
            'name': _('Messages'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'sms.message',
            'context': self.env.context,
            'domain': [('id', 'in', messages.ids)],
        }

    @api.multi
    def action_watchlist_add(self):
        self.ensure_one()
        watchlist_comment_id = self.env.ref('inuka.view_partner_watchlist_comment_form').id
        return {
            'name': _('Watchlist Comment'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'res.partner.watchlist',
            'views': [(watchlist_comment_id, 'form')],
            'view_id': watchlist_comment_id,
            'target': 'new',
            'context': {'watchlist': False},
        }

    @api.multi
    def action_watchlist_remove(self):
        self.ensure_one()
        watchlist_comment_id = self.env.ref('inuka.view_partner_watchlist_comment_form').id
        return {
            'name': _('Watchlist Comment'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'res.partner.watchlist',
            'views': [(watchlist_comment_id, 'form')],
            'view_id': watchlist_comment_id,
            'target': 'new',
            'context': {'watchlist': True},
        }


class PerformanceHistory(models.Model):
    _name = 'performance.history'
    _description = 'Performance History'
    _rec_name = 'partner_id'

    partner_id = fields.Many2one("res.partner", string="Customer")
    performance_type = fields.Selection([
        ('month', 'Month Performance'),
        ('quarter', 'Quarter Performance'),
        ('year', 'Year Performance'),
        ], string='Type')
    date = fields.Date("Date", default=fields.Date.today())
    months = fields.Selection([
        ('jan', 'January'),
        ('feb', 'February'),
        ('mar', 'March'),
        ('apr', 'April'),
        ('may', 'May'),
        ('jun', 'June'),
        ('jul', 'July'),
        ('aug', 'August'),
        ('sep', 'September'),
        ('oct', 'October'),
        ('nov', 'November'),
        ('dec', 'December')
        ], string='Month')
    quarters = fields.Selection([
        ('q1', 'Q1'),
        ('q2', 'Q2'),
        ('q3', 'Q3'),
        ('q4', 'Q4'),
        ], string='Quarter')
    years = fields.Selection([
        ('2016', '2016'),
        ('2017', '2017'),
        ('2018', '2018'),
        ('2019', '2019'),
        ('2020', '2020'),
        ('2021', '2021'),
        ('2022', '2022')
        ], string='Year')

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
        ], string='Status', default='candidate')

    personal_pv = fields.Float("Personal PV")
    pv_downline_1 = fields.Float("PV Downline 1")
    pv_downline_2 = fields.Float("PV Downline 2")
    pv_downline_3 = fields.Float("PV Downline 3")
    pv_downline_4 = fields.Float("PV Downline 4")
    pv_tot_group = fields.Float("Group PV")
    personal_members = fields.Integer("# of Active Downline")
    new_members = fields.Integer("# of New Members")

    is_active = fields.Boolean("Is Active")
    is_new = fields.Boolean("Is New")
    is_vr_earner = fields.Boolean("Is VR Earner")
    is_new_senior = fields.Boolean("Is New & Senior Beyond")
    is_new_junior = fields.Boolean("Is New & Junior Beyond")
    is_new_ruby = fields.Boolean("Is New & Ruby & Beyond")
    vr_earner = fields.Integer("# of VR Earners")
    new_senior_recruits = fields.Integer("# of New Senior Recruits")
    new_junior_recruits = fields.Integer("# of New Junior Recruits")
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)
