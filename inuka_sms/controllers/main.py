# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.http import request


class SMSPushNotification(http.Controller):

    @http.route('/sms/push-notifications/', type="http", auth="public", csrf=False)
    def sms_push_notification(self, *args, **kwargs):
        print ('>>>', args, kwargs,request)
        if kwargs.get('apiMsgId') and kwargs.get('status'):
            request.env['sms.message'].sudo().search([('sms_gateway_message_id', '=', kwargs.get('apiMsgId'))]).write({'status_code': kwargs.get('status')})
        return 'Done'

    @http.route('/sms/reply/', type="http", auth="public", csrf=False)
    def sms_reply_notification(self, *args, **kwargs):
        print ('>>>', args, kwargs,request)
        if kwargs.get('replyMessageId'):
            model = False
            record_id = False
            record_name = False
            msg = "<b>SMS Received</b><ul>"
            msg += "<li>%s" % (kwargs.get('text'))
            msg += "</ul>"
            partner = request.env['res.partner'].sudo().search([('mobile', '=', kwargs.get('fromNumber'))], limit=1)
            helpdesk_ticket = request.env['helpdesk.ticket'].sudo().search([('partner_id', '=', partner.id)], order="create_date desc")
            if helpdesk_ticket:
                stage = request.env['helpdesk.stage'].sudo().search([('name', '=', 'In Progress')], limit=1)
                helpdesk_ticket = helpdesk_ticket and helpdesk_ticket[0]
                helpdesk_ticket.sudo().write({'stage_id': stage.id})
                model = 'helpdesk.ticket'
                record_id = helpdesk_ticket.id
                record_name = helpdesk_ticket.name
                helpdesk_ticket.message_post(body=msg)
            elif partner and not helpdesk_ticket:
                model = 'res.partner'
                record_id = partner.id
                record_name = partner.name
                partner.message_post(body=msg)
            model_id = False
            if model:
                model_id = request.env['ir.model'].sudo().search([('model', '=', model)], limit=1)
            inbound_sms = request.env['sms.message'].sudo().create({
                'sms_gateway_message_id': kwargs.get('replyMessageId'),
                'from_mobile': kwargs.get('fromNumber'),
                'to_mobile': kwargs.get('toNumber'),
                'message_date': kwargs.get('timestamp'),
                'sms_content': kwargs.get('text'),
                'keyword': kwargs.get('keyword'),
                'direction': 'I',
                'by_partner_id': request.env.user.partner_id.id,
                'model_id': model_id,
                'record_id': record_id,
                'record_name': record_name,
            })
        return 'Reply Received'
