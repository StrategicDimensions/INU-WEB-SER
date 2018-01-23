# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Inuka',
    'category': 'Purchases',
    'sequence': 60,
    'summary': 'Inuka',
    'description': "",
    'website': 'https://www.odoo.com/',
    'depends': ['crm', 'purchase', 'delivery', 'base_automation', 'sms_frame', 'payment_mygate', 'account_bank_statement_import_ofx', 'inuka_pos', 'helpdesk', 'project'],
    'data': [
        'security/ir.model.access.csv',
        'security/inuka_security.xml',
        'data/account_financial_report_data.xml',
        'views/purchase_views.xml',
        'views/account_invoice_views.xml',
        'views/res_partner_views.xml',
        'views/sale_views.xml',
        'views/stock_views.xml',
        'views/account.xml',
        'data/mail_template_data.xml',
        'data/base_automation_data.xml',
        'data/sequence_data.xml',
        'views/report_invoice_document_inherited_for_pv.xml',
        'views/report_saleorder_document_inherited_for_pv.xml',
        'views/bulk_master_views.xml',
        'views/rewards_views.xml',
        'wizard/account_invoice_validate_view.xml',
        'wizard/master_account_bank_statement_import_view.xml',
        'views/report_bulk_view.xml',
        'views/helpdesk_ticket_views.xml',
        'wizard/partner_watchlist_comment_view.xml',
    ],
    'qweb': [
        "static/src/xml/account_reconciliation.xml",
    ],
    'test': [
    ],
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
}
