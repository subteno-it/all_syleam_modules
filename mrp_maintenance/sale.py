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


class sale_order(osv.osv):
    _inherit = 'sale.order'

    _columns = {
        'is_maintenance': fields.boolean('Maintenance', help='If set, this sale order is maintenance order'),
        'workcenter_line_ids': fields.one2many('mrp.production.workcenter.line', 'sale_id', 'Workcenter lines', readonly=True, states={'draft': [('readonly', False)]}),
        'production_id': fields.many2one('mrp.production', 'Production', help='Production order has needed product'),
    }

    def action_wait(self, cr, uid, ids, context=None):
        """
        In maintenance:
            - the prodlot must be fill before confirm sale order
            - the product must be to produce and having bom
        """
        bom_obj = self.pool.get('mrp.bom')
        for order in self.browse(cr, uid, ids):
            if order.is_maintenance:
                for line in order.order_line:
                    if not line.product_id:
                        raise osv.except_osv(_('Product missing!'), _('Please fill product for : %s') % line.name)
                    if not line.prodlot_id:
                        raise osv.except_osv(_('Production Lot missing!'), _('Please fill production lot for product : %s') % line.product_id.name)
                    if not line.maintenance_type_id:
                        raise osv.except_osv(_('Maintenance Type missing!'), _('Please fill maintenance type for product : %s') % line.product_id.name)
                    bom_ids = bom_obj.search(cr, uid, [('product_id', '=', line.product_id.id)], limit=1, context=context)
                    if not bom_ids:
                        bom_obj.create(cr, uid, {
                            'name': line.product_id.name,
                            'product_id': line.product_id.id,
                            'product_qty': line.product_uom_qty,
                            'product_uom': line.product_uom.id,
                        }, context=context)
        return super(sale_order, self).action_wait(cr, uid, ids, context=context)

    def _create_pickings_and_procurements(self, cr, uid, order, order_lines, picking_id=False, context=None):
        """
        In Maintenance, the line must be in make_to_order for having link between mrp.production and sale.order
        """
        if order.is_maintenance:
            sale_line_obj = self.pool.get('sale.order.line')
            sale_line_obj.write(cr, uid, [line.id for line in order_lines], {'type': 'make_to_order'}, context=context)
        return super(sale_order, self)._create_pickings_and_procurements(cr, uid, order=order, order_lines=order_lines, picking_id=picking_id, context=context)

    def _prepare_order_picking(self, cr, uid, order, context=None):
        if order.production_id:
            pick_name = self.pool.get('ir.sequence').get(cr, uid, 'stock.picking.internal')
            return {
                'name': pick_name,
                'origin': order.name,
                'date': order.date_order,
                'type': 'internal',
                'state': 'auto',
                'move_type': order.picking_policy,
                'sale_id': order.id,
                'address_id': order.partner_shipping_id.id,
                'note': order.note,
                'invoice_state': (order.order_policy=='picking' and '2binvoiced') or 'none',
                'company_id': order.company_id.id,
            }
        return super(sale_order, self)._prepare_order_picking(cr, uid, order=order, context=context)

    def _prepare_order_line_move(self, cr, uid, order, line, picking_id, date_planned, context=None):
        """
        If sale order is for mrp production, replace default destination location by production location of product
        """
        results = super(sale_order, self)._prepare_order_line_move(cr, uid, order=order, line=line, picking_id=picking_id, date_planned=date_planned, context=context)
        if order.production_id \
           and line.product_id \
           and line.product_id.property_stock_production \
           and line.product_id.property_stock_production.id:
            results['location_dest_id'] = line.product_id.property_stock_production.id
        elif order.is_maintenance:
            if line.prodlot_id:
                results['prodlot_id'] = line.prodlot_id.id
        return results

    def ship_recreate(self, cr, uid, order, line, move_id, proc_id):
        """
        If sale order is for mrp production, link move_id in mrp_production
        """
        if order.production_id:
            order.production_id.write({'move_lines': [(4, move_id)]})
        return super(sale_order, self).ship_recreate(cr, uid, order=order, line=line, move_id=move_id, proc_id=proc_id)

sale_order()


class sale_order_line(osv.osv):
    _inherit = 'sale.order.line'

    _columns = {
        'prodlot_id': fields.many2one('stock.production.lot', 'Production Lot', readonly=True, states={'draft': [('readonly', False)]}, help='Production lot is used to put a serial number on the production'),
        'maintenance_type_id': fields.many2one('mrp.maintenance.type', 'Maintenance Type', domain=[('type', 'in', ['all', 'mrp'])], readonly=True, states={'draft': [('readonly', False)]}, help='Type of maintenance for know if this maintenance will be invoice or not'),
    }

sale_order_line()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
