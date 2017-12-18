# -*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PickingType(models.Model):
    _inherit = "stock.picking.type"

    # Statistics for the kanban view
    count_bulk_waiting = fields.Integer(compute='_compute_bulk_count')
    count_bulk_ready = fields.Integer(compute='_compute_bulk_count')
    count_bulk_late = fields.Integer(compute='_compute_bulk_count')

    def _compute_bulk_count(self):
        today = fields.Datetime.now()
        Bulk = self.env['bulk.master']
        waiting = Bulk.search_count([('state', '=', 'confirmed')])
        ready = Bulk.search_count([('state', '=', 'ready')])
        late = Bulk.search_count([('state', 'not in', ['done', 'cancelled']), ('schedule_date', '<', today)])
        for record in self:
            record.count_bulk_waiting = waiting
            record.count_bulk_ready = ready
            record.count_bulk_late = late

    @api.multi
    def view_bulk_waiting(self):
        self.ensure_one()
        waiting_bulk = self.env['bulk.master'].search([('state', '=', 'confirmed')])
        action = self.env.ref('inuka.action_bulk_master_form').read()[0]
        action['domain'] = [('id', 'in', waiting_bulk.ids)]
        return action

    @api.multi
    def view_bulk_ready(self):
        self.ensure_one()
        bulk_ready = self.env['bulk.master'].search([('state', '=', 'ready')])
        action = self.env.ref('inuka.action_bulk_master_form').read()[0]
        action['domain'] = [('id', 'in', bulk_ready.ids)]
        return action

    @api.multi
    def view_bulk_late(self):
        self.ensure_one()
        today = fields.Datetime.now()
        bulk_late = self.env['bulk.master'].search([('state', 'not in', ['done', 'cancelled']), ('schedule_date', '<', today)])
        action = self.env.ref('inuka.action_bulk_master_form').read()[0]
        action['domain'] = [('id', 'in', bulk_late.ids)]
        return action


class Picking(models.Model):
    _inherit = 'stock.picking'

    bulk_master_id = fields.Many2one("bulk.master", string="Bulk")

    @api.multi
    def button_validate(self):
        context = dict(self.env.context or {})
        if not context.get('from_bulk') and any(picking.bulk_master_id.id != False for picking in self):
            raise UserError(_("You cannot validate if part of bulk."))
        return super(Picking, self).button_validate()
