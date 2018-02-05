# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    purchase_type = fields.Selection([
        ('it', 'IT'),
        ('​stationery', '​Stationery'),
        ('warehouse​', 'Warehouse​ supplies (stock)'),
        ('furniture', 'Furniture'),
        ('repairs', 'Repairs'),
        ('services​', 'Services​ (Training​ etc)'),
        ('rental​', 'Rental​ (Car​ park​ etc)'),
        ('stock', 'Stock'),
        ('marketing​', 'Marketing​ ​ Material')
        ], string='Purchase Type', default='it', readonly=True, states={'draft': [('readonly', False)]})
    total_pv = fields.Float(compute='_compute_tot_pv', store=True)
    payment_reference = fields.Char("Payment Reference", states={'draft': [('readonly', False)]})
    approved_for_payment = fields.Boolean("Approved for Payment", readonly=True, copy=False)
    sale_date = fields.Date('Sale Date', track_visibility='onchange')
    channel = fields.Selection([
        ('front', 'Front Office'),
        ('admin', 'Admin'),
        ('portal', 'Online Portal'),
        ('mobile', 'Mobile Application'),
    ], string="Channel")

    @api.depends('invoice_line_ids','invoice_line_ids.pv')
    def _compute_tot_pv(self):
        for invoice in self:
            tot_pvs = 0.0
            for line in invoice.invoice_line_ids:
                tot_pvs += line.pv
            invoice.total_pv = tot_pvs

    @api.onchange('purchase_id')
    def purchase_order_change(self):
        self.purchase_type = self.purchase_id.purchase_type
        self.payment_reference = self.purchase_id.payment_reference
        super(AccountInvoice, self).purchase_order_change()

    @api.multi
    def action_invoice_open(self):
        SaleOrder = self.env['sale.order']
        context = dict(self.env.context or {})
        for invoice in self:
            purchase_ids = invoice.invoice_line_ids.mapped('purchase_id')
            total = sum(purchase_ids.mapped('amount_total'))
            if purchase_ids and invoice.amount_total != total:
                context['active_id'] = invoice.id
                return {
                    'name': _('Warning'),
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'account.invoice.validate',
                    'type': 'ir.actions.act_window',
                    'context': context,
                    'target': 'new'
                }
#             if invoice.type == 'in_invoice' and not invoice.approved_for_payment:
#                 raise UserError(_('Vendor bill should be approved for payment before you Validate.'))
        return super(AccountInvoice, self).action_invoice_open()

    @api.multi
    def action_approve_bill(self):
        for invoice in self:
            if invoice.type == 'in_invoice':
                if not (self.user_has_groups('purchase.group_purchase_manager') or invoice.user_id.id == invoice.env._uid):
                    raise UserError(_('Only the PO Requestor or Purchase Managers can Approve for Payment.'))
                invoice.approved_for_payment = True
                invoice.action_invoice_open()
        return True


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    unit_pv = fields.Float("Unit PV")
    pv = fields.Float("PV's")

    @api.onchange('product_id')
    def _onchange_product_id(self):
        super(AccountInvoiceLine, self)._onchange_product_id()
        self.pv = self.product_id.pv * self.quantity
        self.unit_pv = self.product_id.pv

    @api.onchange('quantity')
    def _onchange_quantity(self):
        self.pv = self.product_id.pv * self.quantity

    def _set_additional_fields(self, invoice):
        self.pv = self.product_id.pv * self.quantity
        self.unit_pv = self.product_id.pv
        super(AccountInvoiceLine, self)._set_additional_fields(invoice)
