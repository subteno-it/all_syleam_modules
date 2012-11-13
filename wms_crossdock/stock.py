# -*- coding: utf-8 -*-
##############################################################################
#
#    wms_crossdock module for OpenERP, Extension of WMS : Crossdocking management
#    Copyright (C) 2012 SYLEAM Info Services (<http://www.syleam.fr/>)
#              Sylvain Garancher <sylvain.garancher@syleam.fr>
#              Sebastien LANGE <sebastien.lange@syleam.fr>
#
#    This file is a part of wms_crossdock
#
#    wms_crossdock is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    wms_crossdock is distributed in the hope that it will be useful,
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


class stock_picking(osv.osv):
    _inherit = 'stock.picking'

    def get_crossdock_location(self, cr, uid, in_move_id, out_move_id, context=None):
        """
        Returns the crossdock location to use
        """
        stock_move_obj = self.pool.get('stock.move')
        in_move = stock_move_obj.browse(cr, uid, in_move_id, context=context)
        out_move = stock_move_obj.browse(cr, uid, out_move_id, context=context)

        # If some products are already reserved, we put the new products at the same location
        already_reserved = stock_move_obj.search(cr, uid, [('move_dest_id', '=', out_move.id)], context=context)
        if already_reserved:
            crossdock_location_id = stock_move_obj.read(cr, uid, already_reserved[0], ['location_dest_id'], context=context)['location_dest_id'][0]
        # Else we pick the crossdock location of the warehouse
        else:
            crossdock_location = in_move.location_dest_id.warehouse_id.crossdock_location_id
            partner = in_move.address_id.partner_id
            # Do not forget to check chained locations !
            crossdock_location_id = self.pool.get('stock.location').chained_location_get(cr, uid, crossdock_location, partner=partner, context=context)
            if not crossdock_location_id:
                crossdock_location_id = crossdock_location.id

        return crossdock_location_id

    def action_move(self, cr, uid, ids, context=None):
        """
        Redefine test_finished to add crossdocking management
        """
        in_ids = []
        other_ids = []
        for picking_id in self.browse(cr, uid, ids, context=context):
            if picking_id.type == 'in':
                in_ids.append(picking_id.id)
            else:
                other_ids.append(picking_id.id)

        if in_ids:
            stock_move_obj = self.pool.get('stock.move')

            # We take all moves, ordered by date (default in stock.move object)
            in_move_ids = stock_move_obj.search(cr, uid, [('picking_id', 'in', in_ids), ('state', 'not in', ('done', 'cancel'))], context=context)
            for in_move in stock_move_obj.browse(cr, uid, in_move_ids, context=context):
                # Verify the product is allowed for crossdock management
                if in_move.product_id and in_move.product_id.location_type == 'crossdock' \
                   and in_move.location_dest_id.warehouse_id \
                   and in_move.location_dest_id.warehouse_id.crossdock_location_id:
                    if not in_move.location_dest_id.warehouse_id:
                        raise osv.except_osv(_('Configuration error'), _('Warehouse missing on location %s' % in_move.location_dest_id.name))
                    # Verifiy if the move is already for a stock picking out
                    if in_move.move_dest_id and in_move.move_dest_id.picking_id and in_move.move_dest_id.picking_id.type == "out":
                        # Verify if location destination is already affected to crossdock
                        if in_move.move_dest_id.location_id.id != in_move.location_dest_id.warehouse_id.crossdock_location_id.id:
                            crossdock_location_id = in_move.location_dest_id.warehouse_id.crossdock_location_id.id
                            if in_move.product_qty == in_move.move_dest_id.product_qty:
                                stock_move_obj.write(cr, uid, [in_move.move_dest_id.id], {'location_id': crossdock_location_id}, context=context)
                                stock_move_obj.write(cr, uid, [in_move.id], {'location_dest_id': crossdock_location_id}, context=context)
                            elif in_move.product_qty < in_move.move_dest_id.product_qty:
                                out_move_quantity = in_move.move_dest_id.product_qty - in_move.product_qty
                                crossdock_quantity = in_move.move_dest_id.product_qty - out_move_quantity
                                data = {
                                    'product_qty': crossdock_quantity,
                                    'product_uos_qty': stock_move_obj.onchange_quantity(
                                        cr, uid, [],
                                        in_move.product_id.id,
                                        crossdock_quantity,
                                        in_move.product_id.uom_id.id,
                                        in_move.product_id.uos_id and in_move.product_id.uos_id.id or False
                                    )['value']['product_uos_qty'],
                                    'location_id': crossdock_location_id,
                                    'move_dest_id': False,
                                    'state': 'assigned',
                                }
                                new_move_id = stock_move_obj.copy(cr, uid, in_move.move_dest_id.id, data, context=context)
                                stock_move_obj.write(cr, uid, [in_move.move_dest_id.id], {
                                    'product_qty': out_move_quantity,
                                    'product_uos_qty': stock_move_obj.onchange_quantity(
                                        cr, uid, [],
                                        in_move.move_dest_id.product_id.id,
                                        out_move_quantity,
                                        in_move.move_dest_id.product_id.uom_id.id,
                                        in_move.move_dest_id.product_id.uos_id and in_move.move_dest_id.product_id.uos_id.id or False
                                    )['value']['product_uos_qty'],
                                }, context=context)
                                stock_move_obj.write(cr, uid, [in_move.id], {'location_dest_id': crossdock_location_id, 'move_dest_id': new_move_id}, context=context)
                            # in_move.product_qty > in_move.move_dest_id.product_qty:
                            else:
                                out_move_quantity = in_move.product_qty - in_move.move_dest_id.product_qty
                                crossdock_quantity = in_move.product_qty - out_move_quantity
                                data = {
                                    'product_qty': out_move_quantity,
                                    'product_uos_qty' : stock_move_obj.onchange_quantity(
                                        cr, uid, [],
                                        in_move.product_id.id,
                                        out_move_quantity,
                                        in_move.product_id.uom_id.id,
                                        in_move.product_id.uos_id and in_move.product_id.uos_id.id or False
                                    )['value']['product_uos_qty'],
                                    'move_dest_id': False,
                                    'state': 'assigned',
                                }
                                new_move_id = stock_move_obj.copy(cr, uid, in_move.id, data, context=context)
                                stock_move_obj.write(cr, uid, [in_move.move_dest_id.id], {'location_id': crossdock_location_id}, context=context)
                                stock_move_obj.write(cr, uid, [in_move.id], {
                                    'product_qty': crossdock_quantity,
                                    'product_uos_qty': stock_move_obj.onchange_quantity(
                                        cr, uid, [],
                                        in_move.product_id.id,
                                        crossdock_quantity,
                                        in_move.product_id.uom_id.id,
                                        in_move.product_id.uos_id and in_move.product_id.uos_id.id or False
                                    )['value']['product_uos_qty'],
                                    'location_dest_id': crossdock_location_id
                                }, context=context)
                    else:
                        # search if this picking is in backorder_id in other picking in
                        in_picking_backorder_ids = self.search(cr, uid, [('backorder_id', '=', in_move.picking_id.id), ('type', '=', 'in')], context=context)
                        ok = True
                        if in_picking_backorder_ids:
                            for in_picking_backorder_id in self.browse(cr, uid, in_picking_backorder_ids, context=context):
                                in_move_backorder_ids = stock_move_obj.search(cr, uid, [
                                    ('picking_id', '=', in_picking_backorder_id.id),
                                    ('product_id', '=', in_move.product_id.id),
                                    ('move_dest_id', '!=', False)
                                ], context=context)
                                if in_move_backorder_ids:
                                    # We must have only 1 result so take the first, if >1, we have an issue
                                    in_move_backorder = stock_move_obj.browse(cr, uid, in_move_backorder_ids[0], context=context)
                                    # Test in move_dest_id is a picking out not procurement
                                    if in_move_backorder.move_dest_id.picking_id and in_move_backorder.move_dest_id.picking_id.type == "out":
                                        ok = False
                                        crossdock_location_id = in_move.location_dest_id.warehouse_id.crossdock_location_id.id
                                        out_move_quantity = in_move_backorder.move_dest_id.product_qty - in_move.product_qty
                                        data = {
                                            'product_qty': in_move.product_qty,
                                                'product_uos_qty': stock_move_obj.onchange_quantity(
                                                    cr, uid, [],
                                                    in_move.product_id.id,
                                                    in_move.product_qty,
                                                    in_move.product_id.uom_id.id,
                                                    in_move.product_id.uos_id and in_move.product_id.uos_id.id or False
                                                )['value']['product_uos_qty'],
                                            'location_id': crossdock_location_id,
                                            'move_dest_id': False,
                                            'state': 'assigned',
                                        }
                                        new_move_id = stock_move_obj.copy(cr, uid, in_move_backorder.move_dest_id.id, data, context=context)
                                        stock_move_obj.write(cr, uid, [in_move_backorder.move_dest_id.id], {
                                            'product_qty': out_move_quantity,
                                            'product_uos_qty': stock_move_obj.onchange_quantity(
                                                cr, uid, [],
                                                in_move_backorder.move_dest_id.product_id.id,
                                                out_move_quantity,
                                                in_move_backorder.move_dest_id.product_id.uom_id.id,
                                                in_move_backorder.move_dest_id.product_id.uos_id and in_move_backorder.move_dest_id.product_id.uos_id.id or False
                                            )['value']['product_uos_qty'],
                                        }, context=context)
                                        stock_move_obj.write(cr, uid, [in_move.id], {'location_dest_id': crossdock_location_id, 'move_dest_id': new_move_id}, context=context)
                        elif ok:
                            # Search if we have to reserve for this product, ordered by date (default in stock.move object)
                            out_move_ids = stock_move_obj.search(cr, uid, [
                                ('picking_id.type', '=', 'out'),
                                ('picking_id.state', 'in', ('confirmed', 'assigned')),
                                ('state', '=', 'confirmed'),
                                ('product_id', '=', in_move.product_id.id)
                            ], context=context)

                            # Store the current in_move quantity in a separate variable
                            in_move_quantity = in_move.product_qty

                            for out_move in stock_move_obj.browse(cr, uid, out_move_ids, context=context):
                                # If stock_move have a sale_order_line in make_to_order then continue because already reserved an other picking
                                if not out_move.sale_line_id or (out_move.sale_line_id and out_move.sale_line_id.type == 'make_to_stock'):
                                    # Retrieve the total reserved quantity
                                    search_domain = [
                                        ('id', '!=', in_move.id),
                                        ('location_dest_id', 'child_of', [in_move.location_dest_id.warehouse_id.lot_stock_id.id]),
                                        ('move_dest_id', '=', out_move.id),
                                        ('product_id', '=', out_move.product_id.id),
                                        ('state', '=', 'assigned')
                                    ]
                                    reserved_stock_move_ids = stock_move_obj.search(cr, uid, search_domain, context=context)
                                    reserved_stock_move_data = stock_move_obj.read(cr, uid, reserved_stock_move_ids, ['product_qty'], context=context)
                                    reserved_quantity = sum([data['product_qty'] for data in reserved_stock_move_data if data['product_qty']])

                                    # If all quantity is already reserved, continue to the next
                                    if reserved_quantity >= out_move.product_qty:
                                        continue

                                    # Retrieve the total available quantity
                                    search_domain = [
                                        ('id', '!=', in_move.id),
                                        ('location_dest_id', 'child_of', [in_move.location_dest_id.warehouse_id.lot_stock_id.id]),
                                        ('move_dest_id', '=', False),
                                        ('product_id', '=', out_move.product_id.id),
                                        ('picking_id', '!=', False),
                                        ('state', '=', 'assigned')
                                    ]
                                    available_stock_move_ids = stock_move_obj.search(cr, uid, search_domain, context=context)
                                    available_stock_move_data = stock_move_obj.read(cr, uid, available_stock_move_ids, ['product_qty'], context=context)
                                    available_quantity = sum([data['product_qty'] for data in available_stock_move_data if data['product_qty']])

                                    # Sum the available and reserved quantity
                                    available_quantity = available_quantity + reserved_quantity

                                    # We have receipt enough product, reserve it
                                    crossdock_quantity = out_move.product_qty - available_quantity
                                    if crossdock_quantity > 0.0 and crossdock_quantity <= in_move_quantity:
                                        in_move_quantity = in_move_quantity - crossdock_quantity
                                        crossdock_location_id = self.get_crossdock_location(cr, uid, in_move.id, out_move.id, context=context)
                                        data = {
                                            'product_qty': crossdock_quantity,
                                            'product_uos_qty': stock_move_obj.onchange_quantity(
                                                cr, uid, [],
                                                in_move.product_id.id,
                                                crossdock_quantity,
                                                in_move.product_id.uom_id.id,
                                                in_move.product_id.uos_id and in_move.product_id.uos_id.id or False
                                            )['value']['product_uos_qty'],
                                            'location_dest_id': crossdock_location_id,
                                            'move_dest_id': out_move.id,
                                            'state': 'assigned',
                                        }
                                        stock_move_obj.write(cr, uid, [out_move.id], {'location_id': crossdock_location_id}, context=context)
                                        if in_move_quantity > 0:
                                            # Residual quantity, split the move
                                            new_move_id = stock_move_obj.copy(cr, uid, in_move.id, data, context=context)
                                            stock_move_obj.write(cr, uid, [in_move.id], {
                                                'product_qty': in_move_quantity,
                                                'product_uos_qty': stock_move_obj.onchange_quantity(
                                                    cr, uid, [],
                                                    in_move.product_id.id,
                                                    in_move_quantity,
                                                    in_move.product_id.uom_id.id,
                                                    in_move.product_id.uos_id and in_move.product_id.uos_id.id or False
                                                )['value']['product_uos_qty'],
                                            }, context=context)
                                        else:
                                            # All the products are reserved, just modify the move
                                            if in_move.move_dest_id:
                                                stock_move_obj.write(cr, uid, [in_move.move_dest_id.id], {
                                                    'move_dest_id': out_move.id,
                                                    'location_id': crossdock_location_id,
                                                    'location_dest_id': crossdock_location_id
                                                }, context=context)
                                                stock_move_obj.write(cr, uid, [in_move.id], {'location_dest_id': crossdock_location_id}, context=context)
                                            else:
                                                stock_move_obj.write(cr, uid, [in_move.id], data, context=context)
                                            # No more to reserve, we stop searching for this move
                                            break
                                    # Check the "force reserve" boolean on the warehouse
                                    elif in_move.location_dest_id.warehouse_id.force_reserve:
                                        #
                                        # FIXME : not work correctly so disable it
                                        #
                                        #crossdock_location_id = self.get_crossdock_location(cr, uid, in_move.id, out_move.id, context=context)
                                        #stock_move_obj.write(cr, uid, [out_move.id], {'location_id': crossdock_location_id}, context=context)
                                        #if in_move.move_dest_id:
                                        #    stock_move_obj.write(cr, uid, [in_move.move_dest_id.id], {'move_dest_id': out_move.id, 'location_id': crossdock_location_id, 'location_dest_id': crossdock_location_id}, context=context)
                                        #    stock_move_obj.write(cr, uid, [in_move.id], {'location_dest_id': crossdock_location_id}, context=context)
                                        #else:
                                        #    stock_move_obj.write(cr, uid, [in_move.id], {'move_dest_id': out_move.id, 'location_dest_id': crossdock_location_id}, context=context)
                                        ## No more to reserve, we stop searching for this move
                                        break
                                    # Not enough for the current move and no force reserve, stop here
                                    else:
                                        break

        return super(stock_picking, self).action_move(cr, uid, ids)

    def action_cancel(self, cr, uid, ids, context=None):
        """
        Unreserve all moves reserved for the canceled pickings
        """
        stock_move_obj = self.pool.get('stock.move')

        # Search canceled moves
        canceled_move_ids = stock_move_obj.search(cr, uid, [('picking_id', 'in', ids)], context=context)

        # Unreserve linked moves
        if canceled_move_ids:
            stock_move_ids = stock_move_obj.search(cr, uid, [('move_dest_id', 'in', canceled_move_ids)], context=context)
            if stock_move_ids:
                stock_move_obj.write(cr, uid, stock_move_ids, {'move_dest_id': False}, context=context)

        return super(stock_picking, self).action_cancel(cr, uid, ids, context=context)

stock_picking()


class stock_warehouse(osv.osv):
    _inherit = 'stock.warehouse'

    _columns = {
        'force_reserve': fields.boolean('Force reserve', help='If checked, the products will be reserved, even if we need more than the available quantity'),
        'crossdock_location_id': fields.many2one('stock.location', 'Crossdock location', help='Crossdock location for this product'),
    }

stock_warehouse()



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
