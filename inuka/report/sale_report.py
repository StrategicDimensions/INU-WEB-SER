# -*- coding:utf-8 -*-

from odoo import fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"

    pv = fields.Float("PV's", readonly=True)

    def _select(self):
        select_str = super(SaleReport, self)._select()
        select_str += " ,l.pv as pv "
        return select_str

    def _group_by(self):
        group_by_str = super(SaleReport,self)._group_by()
        group_by_str += ",l.pv "
        return group_by_str
