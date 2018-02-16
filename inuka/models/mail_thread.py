# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import base64
import datetime
import dateutil
import email
import hashlib
import hmac
import lxml
import logging
import pytz
import re
import socket
import time
try:
    from xmlrpc import client as xmlrpclib
except ImportError:
    import xmlrpclib

from collections import namedtuple
from email.message import Message
from email.utils import formataddr
from lxml import etree
from werkzeug import url_encode

from odoo import _, api, exceptions, fields, models, tools
from odoo.tools import pycompat
from odoo.tools.safe_eval import safe_eval


_logger = logging.getLogger(__name__)


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    def _message_post_process_attachments(self, attachments, attachment_ids, message_data):
        IrAttachment = self.env['ir.attachment']
        m2m_attachment_ids = []
        cid_mapping = {}
        fname_mapping = {}
        if attachment_ids:
            filtered_attachment_ids = self.env['ir.attachment'].sudo().search([
                ('res_model', '=', 'mail.compose.message'),
                ('create_uid', '=', self._uid),
                ('id', 'in', attachment_ids)])
            if filtered_attachment_ids:
                filtered_attachment_ids.write({'res_model': message_data['model'], 'res_id': message_data['res_id']})
            m2m_attachment_ids += [(4, id) for id in attachment_ids]
        # Handle attachments parameter, that is a dictionary of attachments
        for attachment in attachments:
            cid = False
            if attachment[0][-3:] == 'eml':
                continue
            if len(attachment) == 2:
                name, content = attachment
            elif len(attachment) == 3:
                name, content, info = attachment
                cid = info and info.get('cid')
            else:
                continue
            if isinstance(content, pycompat.text_type):
                content = content.encode('utf-8')
            data_attach = {
                'name': name,
                'datas': base64.b64encode(content),
                'type': 'binary',
                'datas_fname': name,
                'description': name,
                'res_model': message_data['model'],
                'res_id': message_data['res_id'],
            }
            new_attachment = IrAttachment.create(data_attach)
            m2m_attachment_ids.append((4, new_attachment.id))
            if cid:
                cid_mapping[cid] = new_attachment
            fname_mapping[name] = new_attachment

        if cid_mapping and message_data.get('body'):
            root = lxml.html.fromstring(tools.ustr(message_data['body']))
            postprocessed = False
            for node in root.iter('img'):
                if node.get('src', '').startswith('cid:'):
                    cid = node.get('src').split('cid:')[1]
                    attachment = cid_mapping.get(cid)
                    if not attachment:
                        attachment = fname_mapping.get(node.get('data-filename'), '')
                    if attachment:
                        node.set('src', '/web/image/%s' % attachment.id)
                        postprocessed = True
            if postprocessed:
                body = lxml.html.tostring(root, pretty_print=False, encoding='UTF-8')
                message_data['body'] = body

        return m2m_attachment_ids
