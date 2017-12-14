# -*- coding: utf-8 -*-

from odoo import api, models


class AccountPayment(models.Model):
    _inherit = "account.payment"

    @api.multi
    def post(self):
        SaleOrder = self.env['sale.order']
        for payment in self:
            if payment.payment_type == 'inbound':
                sale_orders = SaleOrder.search([('partner_id', '=', payment.partner_id.id), ('order_status', '=', 'payment')])
                if sale_orders and sale_orders[0].reserve >= 0:
                    sale_orders.write({'order_status': 'open'})
        return super(AccountPayment, self).post()
