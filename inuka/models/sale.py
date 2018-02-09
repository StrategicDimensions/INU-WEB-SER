# -*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import base64
import io
import csv
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _default_expiry_date(self):
        return date.today() + relativedelta(days=90)

    @api.depends('order_line','order_line.pv')
    def _compute_tot_pv(self):
        for order in self:
            tot_pvs = 0.0
            for line in order.order_line:
                tot_pvs += line.pv
            order.total_pv = tot_pvs

    order_sent_by = fields.Selection([
        ('email', 'Email'),
        ('facebook', 'Facebook'),
        ('fax',' Fax'),
        ('inuka', 'Inuka'),
        ('phone', 'Phone'),
        ('sms', 'SMS'),
        ('whatsapp', 'Whatsapp'),
        ('portal', 'Portal')],
        string="Order Sent By", default="email", readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})
    order_type = fields.Selection([
        ('collect', 'Collect / No Shipping'),
        ('bulk', 'Part of Bulk'),
        ('consolidated', 'Consolidated'),
        ('single', 'Single'),
        ('upfront', 'Upfront'),
        ('stock', 'Stock (for Up front)')],
        string='Order Type', default="collect", readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})
    sale_date = fields.Date('Sale Date', readonly=True, default=fields.Date.context_today, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})
    order_total = fields.Float('Order Total', readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})
    product_cost = fields.Float('Product Cost', readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})
    shipping_cost = fields.Float('Shipping Cost', readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})
    pv = fields.Float('PV', readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})
    total_pv = fields.Float(compute='_compute_tot_pv', store=True)
    reserve = fields.Monetary(string='Available Funds', compute="_compute_reserve")
    paid = fields.Boolean(readonly=True, copy=False)
    order_status = fields.Selection([
        ('new', 'New Order'),
        ('open', 'Open'),
        ('general', 'Snag General'),
        ('payment', 'Snag Payment Option'),
        ('unreadable', 'Snag Unreadable')
    ], string="Order Status", default="new", readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})
    delivery_status = fields.Selection([
        ('to_deliver', 'To Deliver'),
        ('partially', 'Partially Delivered'),
        ('fully', 'Fully Delivered'),
    ], compute="_compute_delivery_status", string="Delivery Status", store=True)
    bulk_master_id = fields.Many2one("bulk.master", string="Bulk", readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})
    kit_order = fields.Boolean("Kit Order", readonly=True)
    validity_date = fields.Date(string='Expiration Date', readonly=True, copy=False, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
        help="Manually set the expiration date of your quotation (offer), or it will set the date automatically based on the template if online quotation is installed.", default=_default_expiry_date)
    channel = fields.Selection([
        ('front', 'Front Office'),
        ('admin', 'Admin'),
        ('portal', 'Online Portal'),
        ('mobile', 'Mobile Application'),
    ], string="Channel")

    @api.depends('state', 'order_line', 'order_line.qty_delivered', 'order_line.product_uom_qty')
    def _compute_delivery_status(self):
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        for order in self:
            if order.state not in ('sale', 'done'):
                order.delivery_status = 'to_deliver'
                continue

            if all(float_compare(line.qty_delivered, 0.000, precision_digits=precision) == 0 for line in order.order_line if line.product_uom_qty):
                order.delivery_status = 'to_deliver'
            elif all(float_compare(line.qty_delivered, line.product_uom_qty, precision_digits=precision) == 0 for line in order.order_line):
                order.delivery_status = 'fully'
            else:
                order.delivery_status = 'partially'

    def _compute_reserve(self):
        ReservedFund = self.env['reserved.fund']
        for order in self:
            res_funds = self.env['reserved.fund'].search([('customer_id', '=', order.partner_id.id)])
            amount_reserve = sum([x.amount for x in res_funds])
            order.reserve = - (order.partner_id.credit - order.partner_id.debit) + order.partner_id.credit_limit - amount_reserve

#     @api.onchange('partner_id')
#     def onchange_partner_id(self):
#         super(SaleOrder, self).onchange_partner_id()
#         self.partner_shipping_id = False

    @api.model
    def create(self, vals):
        context = dict(self.env.context or {})
        partner_id = vals.get('partner_id')
        status = self.env['res.partner'].browse(partner_id).status
        if not context.get('kit_order') and status == 'candidate':
            raise UserError(_("You cannot create an order for a Candidate."))
        channel = self.env['mail.channel'].search([('name', 'like', 'Escalations')], limit=1)
        res = super(SaleOrder, self).create(vals)
        if res.partner_id.mobile:
            sms_template = self.env.ref('sms_frame.sms_template_inuka_international')
            msg_compose = self.env['sms.compose'].create({
                'record_id': res.id,
                'model': 'sale.order',
                'sms_template_id': sms_template.id,
                'from_mobile_id': self.env.ref('sms_frame.sms_number_inuka_international').id,
                'to_number': res.partner_id.mobile,
                'sms_content': """ INUKA thanks you for your order %s, an SMS with details will follow when your order (Ref: %s) is dispatched^More info on 27219499850""" %(res.partner_id.name, res.name)
            })
            msg_compose.send_entity()
        if res.partner_id.watchlist and channel:
            res.message_subscribe(channel_ids=[channel.id])
        return res

    @api.multi
    def dummy_redirect(self):
        return

    @api.multi
    def action_confirm(self):
        for order in self:
            res = order.carrier_id.rate_shipment(order)
            order.get_delivery_price()
            order.set_delivery_line()
            order.write({'shipping_cost': res['price'],'pv': order.total_pv, 'order_total': order.amount_total})
            order.picking_ids.write({'bulk_master_id': order.bulk_master_id.id})
        return super(SaleOrder, self).action_confirm()

    @api.multi
    def action_cancel(self):
        super(SaleOrder, self).action_cancel()
        self.action_unlink_reserved_fund()

    @api.multi
    def action_add_reserved_fund(self):
        ReservedFund = self.env['reserved.fund']
        for order in self:
            if order.reserve >= order.order_total:
                ReservedFund.create({
                    'date': fields.Datetime.now(),
                    'desctiption': 'Reservation for %s for Order %s for an amount of %d by %s' % (order.partner_id.name, order.name, order.order_total, order.user_id.name),
                    'amount': order.order_total,
                    'order_id': order.id,
                    'customer_id': order.partner_id.id,
                })
                order.paid = True
                msg = "<b>Fund Reserved</b><ul>"
                msg += "<li>Reservation for %s <br/> for Order %s for an amount of <br/> %s %d by %s" % (order.partner_id.name, order.name, order.company_id.currency_id.symbol, order.order_total, order.user_id.name)
                msg += "</ul>"
                order.message_post(body=msg)
            else:
                raise UserError(_('Insufficient Funds Available'))

    @api.multi
    def action_unlink_reserved_fund(self):
        ReservedFund = self.env['reserved.fund']
        for order in self:
            res_funds = ReservedFund.search([('order_id', '=', order.id)])
            # res_funds.unlink()
            res_funds.write({
                'active': False,
            })
            order.paid = False
            msg = "<b>Fund unreserved</b><ul>"
            msg += "<li>Reservation Reversed for %s <br/> for Order %s for an amount of <br/> %s %d by %s" % (order.partner_id.name, order.name, order.company_id.currency_id.symbol, order.order_total, order.user_id.name)
            msg += "</ul>"
            order.message_post(body=msg)

    @api.multi
    def _prepare_invoice(self):
        res = super(SaleOrder, self)._prepare_invoice()
        res['sale_date'] = self.sale_date
        res['channel'] = self.channel
        return res


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    pv = fields.Float("PV's")
    unit_pv = fields.Float("Unit PV")

    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        super(SaleOrderLine, self).product_id_change()
        self.pv = self.product_id.pv * self.product_uom_qty
        self.unit_pv = self.product_id.pv

    @api.onchange('product_uom_qty')
    def _onchange_product_uom_qty(self):
        self.pv = self.product_id.pv * self.product_uom_qty


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    advance_payment_method = fields.Selection(default='delivered')


class ReservedFund(models.Model):
    """Master should be added which will be used to reserve funds on a quotation"""
    _name = "reserved.fund"
    _description = "Reserved Fund"
    _rec_name = 'order_id'

    date = fields.Datetime(readonly=True, requied=True, default=lambda self: fields.Datetime.now())
    desctiption = fields.Char(readonly=True, requied=True)
    amount = fields.Float(readonly=True, requied=True)
    order_id = fields.Many2one('sale.order', readonly=True, requied=True)
    customer_id = fields.Many2one('res.partner', readonly=True, requied=True)
    active = fields.Boolean(default=True, readonly=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)


class SaleUpload(models.Model):
    _name = "sale.upload"
    _description = "Sale Upload"

    name = fields.Char("Name")
    state = fields.Selection([
        ('new', 'New'),
        ('inprogress', 'In Progress'),
        ('completed', 'Completed'),
        ('error', 'Error'),
        ('cancelled', 'Cancelled'),
        ], string='Status', default='new')
    start_time = fields.Datetime("Start Time")
    end_time = fields.Datetime("End Time")
    duration = fields.Integer(compute="_compute_duration", string="Duration")
    result = fields.Text()
    file = fields.Binary()
    end_point = fields.Integer("End Point")
    batch_size = fields.Integer("Batch Size")

    def _compute_duration(self):
        for record in self:
            start_time = fields.Datetime.from_string(record.start_time)
            end_time = fields.Datetime.from_string(record.end_time)
            duration = 0
            if start_time and end_time:
                duration = (end_time - start_time).total_seconds()
            record.duration = duration

    @api.multi
    def button_start(self):
        self.ensure_one()
        self.state = 'inprogress'
        self.start_time = fields.Datetime.now(self)
        self.import_data()
        return True

    @api.multi
    def button_cancel(self):
        self.ensure_one()
        self.state = 'cancelled'
        return True

    @api.multi
    def import_data(self):
        self.ensure_one()
        Partner = self.env['res.partner']
        Intermediate = self.env['sale.upload.intermediate']
        row_list = []

        try:
            data = base64.b64decode(self.file)
            file_input = io.StringIO(data.decode("utf-8"))
            file_input.seek(0)
            reader = csv.reader(file_input, delimiter=',', lineterminator='\r\n')
            reader_info = []
            reader_info.extend(reader)
            keys = reader_info[0]
        except Exception as e:
            raise UserError(_("Invalid file. \n Note: file must be csv" % tools.ustr(e)))

        if self.end_point == 0:
            start_point = 0
            end_point = start_point + batch_size
        else:
            start_point = self.end_point
            end_point = start_point + batch_size

        if end_point >= len(reader_info):
            end_point = len(reader_info)

        for row in range(start_point, end_point):
            field = reader_info[row]
            values = dict(zip(keys, field))
            row_list.append(values)

        status_dict = {
            'Candidate': 'candidate',
            'New': 'new',
            'Junior': 'junior',
            'Senior': 'senior',
            'Pearl': 'pearl',
            'Ruby': 'ruby',
            'Emerald': 'emerald',
            'Sapphire': 'sapphire',
            'Diamond': 'diamond',
            'double_diamond': 'double_diamond',
            'triple_diamond': 'triple_diamond',
            'Exective Diamond': 'exective_diamond',
            'Presidential': 'presidential',
        }

        record_count = status_count = 0
        for data in row_list:
            if data.get('MEMBERID'):
                part = Partner.search([('ref', '=', data['MEMBERID'])], limit=1)
                if part:
                    try:
                        sql_query ="""UPDATE res_partner SET personal_pv = %s,
                                    pv_downline_1 = %s, pv_downline_2 = %s,
                                    pv_downline_3 = %s, pv_downline_4 = %s,
                                    pv_tot_group = %s, personal_members = %s, new_members = %s WHERE ref = %s"""
                        params = (data.get('PVPERS') or 0.0, data.get('PVDOWNLINE1') or 0.0, data.get('PVDOWNLINE2') or 0.0, data.get('PVDOWNLINE3') or 0.0, data.get('PVDOWNLINE4') or 0.0,
                                data.get('PVTOTGROUP') or 0.0, data.get('ACTIVEPERSMEM') or 0, data.get('PERSNEWMEM') or 0, data.get('MEMBERID'))
                        self.env.cr.execute(sql_query, params)
                        record_count += 1
    
                        if part.status != status_dict.get(data.get('STATUS')):
                            sql_query = """INSERT INTO sale_upload_intermediate (partner_id, old_status, new_status, active)
                                    VALUES (%s, %s, %s, %s)"""
                            params = (part.id, part.status, status_dict.get(data.get('STATUS')), True)
                            self.env.cr.execute(sql_query, params)
                            self.env.cr.commit()
                            status_count += 1
                    except Exception as e:
                        result = """Error: %s""" %(str(e))
                        self.write({'result': result, 'end_time': fields.Datetime.now(self), 'state': 'error'})
                        return True

        result = """%s - %s: %s records updated, %s status change updated""" %(start_point, end_point, record_count, status_count)
        if self.result:
            result = self.result + '\n' + result
        if end_point == len(reader_info):
            self.write({'result': result, 'end_time': fields.Datetime.now(self), 'state': 'completed'})
        else:
            self.write({'end_point':end_point,'result': result, 'end_time': fields.Datetime.now(self), 'state': 'inprogress'})

        return True


class SaleUploadIntermediate(models.Model):
    _name = "sale.upload.intermediate"
    _description = "Sale Upload Intermediate"
    _rec_name = 'partner_id'

    partner_id = fields.Many2one("res.partner", string="Customer")
    old_status = fields.Selection([
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
        ], string='Old Status')
    new_status = fields.Selection([
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
        ], string='New Status')
    active = fields.Boolean(default=True)

    @api.model
    def update_status(self):
        records = self.search([], limit=20)
        for record in records:
            record.partner_id.write({'status': record.new_status})
            record.write({'active': False})
