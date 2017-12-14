# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models

class AccountInvoiceReport(models.Model):
    _inherit = "account.invoice.report"

    pv = fields.Float("PV's", readonly=True)

    def _select(self):
        select_str = super(AccountInvoiceReport,self)._select()
        select_str += " ,sub.pv "
        return select_str

    def _sub_select(self):
        sub_select_str = super(AccountInvoiceReport,self)._sub_select()
        sub_select_str += " ,ail.pv as pv "
        return sub_select_str

    def _group_by(self):
        group_by_str = super(AccountInvoiceReport,self)._group_by()
        group_by_str += ",ail.pv "
        return group_by_str
