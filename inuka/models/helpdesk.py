# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import base64
import zipfile
import os
from io import BytesIO
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools.osutil import tempdir


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    product_ids = fields.Many2many('product.product', 'helpdesk_ticket_product_rel', 'ticket_id', 'product_id', string="Products")
    mobile = fields.Char("Customer Mobile")
    sale_order_count = fields.Integer(compute="_compute_sale_order_count", string="Sale Orders")
    is_close = fields.Boolean(related="stage_id.is_close")

    def _compute_sale_order_count(self):
        SaleOrder = self.env['sale.order']
        for ticket in self:
            ticket.sale_order_count = SaleOrder.search_count([('ticket_id', '=', ticket.id)])

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        super(HelpdeskTicket, self)._onchange_partner_id()
        if self.partner_id:
            self.mobile = self.partner_id.mobile

    @api.multi
    def create_sale_order(self):
        self.ensure_one()
        saleorder = self.env['sale.order'].create({
            'partner_id': self.partner_id.id,
            'ticket_id': self.id,
        })
        view_id = self.env.ref('sale.view_order_form').id
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sale.order',
            'views': [(view_id, 'form')],
            'view_id': view_id,
            'res_id': saleorder.id,
        }

    @api.multi
    def import_bank_statement(self):
        ResPartnerBank = self.env['res.partner.bank']
        stage = self.env['helpdesk.stage'].search([('name', '=', 'Solved')], limit=1)
        for ticket in self:
            attachments = self.env['ir.attachment'].search([('res_id', '=', ticket.id), ('res_model', '=', 'helpdesk.ticket')])

            acc_number = ticket.name.split("[")[1][:-1]
            bank_account_id = ResPartnerBank.search([('acc_number', '=', acc_number)], limit=1).id
            journal_id = self.env['account.journal'].search([('bank_account_id', '=', bank_account_id)], limit=1).id
            for attachment in attachments:
                fp = BytesIO()
                fp.write(base64.b64decode(attachment.datas))
                if not zipfile.is_zipfile(fp):
                    raise UserError(_('File is not a zip file!'))
                if zipfile.is_zipfile(fp):
                    with zipfile.ZipFile(fp, "r") as z:
                        with tempdir() as module_dir:
                            import odoo.modules.module as module
                            try:
                                module.ad_paths.append(module_dir)
                                z.extractall(module_dir)
                                for d in os.listdir(module_dir):
                                    extract_file = z.open(d)
                                    new_rec = self.env['account.bank.statement.import'].with_context(journal_id=journal_id).create({'data_file': base64.b64encode(extract_file.read()), 'filename': 'test'})
                                    new_rec.import_file()
                                    ticket.write({'stage_id': stage.id})
                            finally:
                                module.ad_paths.remove(module_dir)

    @api.multi
    def import_master_bank_statement(self):
        ResPartnerBank = self.env['res.partner.bank']
        stage = self.env['helpdesk.stage'].search([('name', '=', 'Solved')], limit=1)
        for ticket in self:
            attachments = self.env['ir.attachment'].search([('res_id', '=', ticket.id), ('res_model', '=', 'helpdesk.ticket')])

            acc_number = ticket.name.split("[")[1][:-1]
            bank_account_id = ResPartnerBank.search([('acc_number', '=', acc_number)], limit=1).id
            journal_id = self.env['account.journal'].search([('bank_account_id', '=', bank_account_id)], limit=1).id
            for attachment in attachments:
                fp = BytesIO()
                fp.write(base64.b64decode(attachment.datas))
                if not zipfile.is_zipfile(fp):
                    raise UserError(_('File is not a zip file!'))
                if zipfile.is_zipfile(fp):
                    with zipfile.ZipFile(fp, "r") as z:
                        with tempdir() as module_dir:
                            import odoo.modules.module as module
                            try:
                                module.ad_paths.append(module_dir)
                                z.extractall(module_dir)
                                for d in os.listdir(module_dir):
                                    extract_file = z.open(d)
                                    new_rec = self.env['master.account.bank.statement.import'].with_context(journal_id=journal_id).create({'data_file': base64.b64encode(extract_file.read()), 'filename': 'test'})
                                    new_rec.import_file()
                                    ticket.write({'stage_id': stage.id})
                            finally:
                                module.ad_paths.remove(module_dir)

    @api.multi
    def view_sale_orders(self):
        self.ensure_one()
        orders = self.env['sale.order'].search([('ticket_id', '=', self.id)])
        action = self.env.ref('sale.action_orders').read()[0]
        action['domain'] = [('id', 'in', orders.ids)]
        return action

    def sms_action(self):
        self.ensure_one()
        default_mobile = self.env.ref('sms_frame.sms_number_inuka_international')
        return {
            'name': 'SMS Compose',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sms.compose',
            'target': 'new',
            'type': 'ir.actions.act_window',
            'context': {'default_from_mobile_id': default_mobile.id, 'default_to_number': self.mobile, 'default_record_id': self.id, 'default_model': 'helpdesk.ticket'}
         }


class SaleOrder(models.Model):
    _inherit = "sale.order"

    ticket_id = fields.Many2one("helpdesk.ticket", string="Tickets")


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    @api.model
    def create(self, vals):
        res = super(IrAttachment, self).create(vals)
        if res.res_model == 'helpdesk.ticket' and 'FNB RSA OFX' in res.res_name and 'Hourly' in res.res_name:
            self.env['helpdesk.ticket'].browse(res.res_id).import_bank_statement()
        elif res.res_model == 'helpdesk.ticket' and 'FNB RSA OFX' in res.res_name and 'Hourly' not in res.res_name:
            self.env['helpdesk.ticket'].browse(res.res_id).import_master_bank_statement()
        return res
