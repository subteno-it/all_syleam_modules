# -*- coding: utf-8 -*-
##############################################################################
#
#    mrp_maintenance module for OpenERP, Manage maintenance in production order
#    Copyright (C) 2012 SYLEAM Info Services (<http://www.syleam.fr/>)
#              Sebastien LANGE <sebastien.lange@syleam.fr>
#
#    This file is a part of mrp_maintenance
#
#    mrp_maintenance is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    mrp_maintenance is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import osv
from osv import fields
from tools.translate import _
import time
from tools import DEFAULT_SERVER_DATE_FORMAT


class mrp_maintenance_invoice(osv.osv_memory):
    _name = 'mrp.maintenance.invoice'
    _description = 'MRP Maintenance Invoice'

    def _get_journal(self, cr, uid, context=None):
        res = self._get_journal_id(cr, uid, context=context)
        if res:
            return res[0][0]
        return False

    def _get_journal_id(self, cr, uid, context=None):

        journal_obj = self.pool.get('account.journal')
        vals = []

        value = journal_obj.search(cr, uid, [('type', '=', 'sale')])
        for jr_type in journal_obj.browse(cr, uid, value, context=context):
            t1 = jr_type.id, jr_type.name
            if t1 not in vals:
                vals.append(t1)
        return vals

    _columns = {
        'journal_id': fields.selection(_get_journal_id, 'Destination Journal', required=True),
        'invoice_date': fields.date('Invoiced date'),
    }

    _defaults = {
        'journal_id': _get_journal,
    }

    def view_init(self, cr, uid, fields_list, context=None):
        """
        Check if authorized to use this wizard
        """
        if context is None:
            context = {}
        res = super(mrp_maintenance_invoice, self).view_init(cr, uid, fields_list, context=context)
        mrp_obj = self.pool.get('mrp.production')
        count = 0
        active_ids = context.get('active_ids', [])
        for mrp in mrp_obj.browse(cr, uid, active_ids, context=context):
            if mrp.state == 'done' and mrp.invoice_state == '2binvoiced' and mrp.sale_id and mrp.sale_id.is_maintenance:
                count += 1
        if len(active_ids) != count:
            raise osv.except_osv(_('Warning !'), _('None of these production lists not invoiced.'))
        return res

    def open_invoice(self, cr, uid, ids, context=None):
        """
        After create invoice, open it in new tab
        """
        if context is None:
            context = {}
        data_pool = self.pool.get('ir.model.data')
        invoice_ids = self.create_invoice(cr, uid, ids, context=context).values()
        inv_type = context.get('inv_type', False)
        action_model = False
        action = {}
        if not invoice_ids:
            raise osv.except_osv(_('Error'), _('No Invoices were created'))
        if inv_type == "out_invoice":
            action_model, action_id = data_pool.get_object_reference(cr, uid, 'account', "action_invoice_tree1")
        elif inv_type == "in_invoice":
            action_model, action_id = data_pool.get_object_reference(cr, uid, 'account', "action_invoice_tree2")
        elif inv_type == "out_refund":
            action_model, action_id = data_pool.get_object_reference(cr, uid, 'account', "action_invoice_tree3")
        elif inv_type == "in_refund":
            action_model, action_id = data_pool.get_object_reference(cr, uid, 'account', "action_invoice_tree4")
        if action_model:
            action_pool = self.pool.get(action_model)
            action = action_pool.read(cr, uid, action_id, context=context)
            action['domain'] = "[('id', 'in', [" + ','.join(map(str, invoice_ids)) + "])]"
        return action

    def create_invoice(self, cr, uid, ids, context=None):
        """
        Create invoice from production order with all product and workcenter
        """
        if context is None:
            context = {}
        picking_obj = self.pool.get('stock.picking')
        sale_obj = self.pool.get('sale.order')
        sale_line_obj = self.pool.get('sale.order.line')
        mrp_obj = self.pool.get('mrp.production')
        account_invoice_obj = self.pool.get('account.invoice')
        account_invoice_line_obj = self.pool.get('account.invoice.line')
        data_obj = self.read(cr, uid, ids, ['journal_id', 'invoice_date'])
        context['date_inv'] = data_obj[0]['invoice_date']
        active_ids = context.get('active_ids', [])
        res = {}
        for production in mrp_obj.browse(cr, uid, active_ids, context=context):
            picking_ids = []
            sale_ids = sale_obj.search(cr, uid, [('production_id', '=', production.id)], context=context)
            for sale in sale_obj.browse(cr, uid, sale_ids, context=context):
                for picking in sale.picking_ids:
                    if picking.state == 'done' and picking.invoice_state == '2binvoiced':
                        picking_ids.append(picking.id)
            inv_type = 'out_invoice'
            context['inv_type'] = inv_type
            if isinstance(data_obj[0]['journal_id'], tuple):
                data_obj[0]['journal_id'] = data_obj[0]['journal_id'][0]

            invoice_ids = []
            if picking_ids:
                invoice_ids = picking_obj.action_invoice_create(
                    cr, uid, picking_ids,
                    journal_id=data_obj[0]['journal_id'],
                    group=True,
                    type=inv_type,
                    context=context)

            if invoice_ids:
                invoice_id = invoice_ids.values()[0]
                # Get invoice lines created for link in maintenance order
                invoice_line_ids = [line.id for line in account_invoice_obj.browse(cr, uid, invoice_id, context=context).invoice_line]
                res[production.id] = invoice_id
                workcenter_lines = {}
                # Group by workcenter_id
                for line in production.workcenter_lines:
                    if line.workcenter_id.id in workcenter_lines:
                        workcenter_lines[line.workcenter_id.id].append(line)
                        continue
                    workcenter_lines[line.workcenter_id.id] = [line]
                pricelist_id = production.sale_id.pricelist_id.id
                partner_id = production.sale_id.partner_id.id
                for workcenter_id, lines in workcenter_lines.items():
                    product = lines[0].workcenter_id.product_id
                    nb_hour = 0.
                    # Get nb hour of workcenter
                    for line in lines:
                        nb_hour += line.hour
                    # Get price unit
                    price_unit = self.pool.get('product.pricelist').price_get(
                        cr, uid, [pricelist_id],
                        lines[0].workcenter_id.product_id.id, nb_hour or 1.0,
                        partner_id,
                        {
                            'uom': lines[0].workcenter_id.product_id.uom_id.id,
                            'date': time.strftime(DEFAULT_SERVER_DATE_FORMAT),
                        }
                    )[pricelist_id]

                    # Get taxes
                    taxes = product.taxes_id
                    taxe_ids = map(lambda x: x.id, taxes)
                    if production.sale_id.fiscal_position or production.sale_id.partner_id.property_account_position:
                        taxe_ids = self.pool.get('account.fiscal.position').map_tax(
                            cr,
                            uid,
                            production.sale_id.fiscal_position or production.sale_id.partner_id.property_account_position,
                            taxes
                        )

                    # Create a new invoice line for workcenter
                    invoice_line_ids.append(account_invoice_line_obj.create(cr, uid, {
                        'name': lines[0].workcenter_id.name,
                        'origin': production.sale_id and production.sale_id.name or production.name,
                        'invoice_id': invoice_id,
                        'uos_id': product.uom_id.id,
                        'product_id': product.id,
                        'account_id': product.product_tmpl_id.property_account_income or product.categ_id.property_account_income_categ.id,
                        'price_unit': price_unit,
                        'discount': 0.,
                        'quantity': nb_hour,
                        'invoice_line_tax_id': [(6, 0, taxe_ids)],
                        'account_analytic_id': production.sale_id.project_id and production.sale_id.project_id.id or False,
                    }, context=context))

                # Link all invoice lines in line of maintenance order
                sale_line_obj.write(cr, uid, [production.move_prod_id.sale_line_id.id], {
                    'invoiced': True,
                    'invoice_lines': [(6, 0, invoice_line_ids)],
                }, context=context)
                # Link invoice with maintenance order
                sale_obj.write(cr, uid, [production.sale_id.id], {
                    'invoice_ids': [(4, invoice_id)],
                }, context=context)
                # Compute invoice
                account_invoice_obj.button_compute(cr, uid, [invoice_id], context=context)
                # Set invoiced in picking's maintenance order
                picking_obj.write(cr, uid, [production.move_prod_id.picking_id.id], {
                    'invoice_state': 'invoiced',
                }, context=context)
                # Set invoiced in production order
                production.write({'invoice_state': 'invoiced'})
        return res

mrp_maintenance_invoice()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
