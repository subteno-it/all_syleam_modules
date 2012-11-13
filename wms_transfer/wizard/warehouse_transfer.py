# -*- coding: utf-8 -*-
##############################################################################
#
#    wms_transfer module for OpenERP, Wizard for transfer product in stock in other warehouse
#    Copyright (C) 2012 SYLEAM Info Services (<http://www.syleam.fr/>)
#              Sebastien LANGE <sebastien.lange@syleam.fr>
#
#    This file is a part of wms_transfer
#
#    wms_transfer is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    wms_transfer is distributed in the hope that it will be useful,
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
import decimal_precision as dp
from tools.translate import _
import time
import netsvc


class stock_warehouse_transfer(osv.osv_memory):
    _name = 'wizard.stock.warehouse.transfer'
    _description = 'Transfer stock from one warehouse to an other one'
    _rec_name = 'product_id'

    _columns = {
        'warehouse_src_id': fields.many2one('stock.warehouse', 'Warehouse Source', required=True, change_default=True, readonly=True, help='The warehouse where find the product available'),
        'warehouse_dest_id': fields.many2one('stock.warehouse', 'Warehouse Destination', change_default=True, required=True, help='The product selected will be transfer in this warehouse'),
        'location_src_id': fields.many2one('stock.location', 'Location Source', required=True, readonly=True, help='Location source where find the product available'),
        'location_dest_id': fields.many2one('stock.location', 'Location Destination', required=True, help='The product selected will be transfer in this location'),
        'product_id': fields.many2one('product.product', 'Product', readonly=True, help='Product will be tranfer in new warehouse'),
        'product_uom_qty': fields.float('Product Quantity', digits_compute=dp.get_precision('Product UoM'), help='Quantity to transfer'),
        'uom_id': fields.many2one('product.uom', 'Product UoM', required=True, help='Unit for this transfer'),
        'tracking_id': fields.many2one('stock.tracking', 'Tracking', readonly=True),
        'prodlot_id': fields.many2one('stock.production.lot', 'Production lot', readonly=True),
        'date_expected': fields.datetime('Date Expected', help='Date of receive product.'),
        'product_packaging_id': fields.many2one('product.packaging', 'Packaging', help='Packaging of product'),
        'company_id': fields.many2one('res.company', 'Company', required=False),
        'last_transfer': fields.boolean('Last Product to Transfer', help='Indicate it last product to transfer.'),
    }

    _defaults = {
        'company_id': lambda s, cr, uid, c: s.pool.get('res.company')._company_default_get(cr, uid, 'wizard.stock.warehouse.transfer', context=c),
        'date_expected': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'last_transfer': False,
    }

    def default_get(self, cr, uid, fields_list, context=None):
        """
        Automatically populate fields when opening the wizard from the selected report stock
        """
        if context is None:
            context = {}
        report_obj = self.pool.get('wms.report.stock.available')

        # Call to super for standard behaviour
        values = super(stock_warehouse_transfer, self).default_get(cr, uid, fields_list, context=context)

        # Retrieve current stock move from context
        if 'active_id' in context and context.get('active_id', False):
            report_id = context['active_id']
            report = report_obj.browse(cr, uid, report_id, context=context)

            # Initialize values
            values.update({
                'warehouse_src_id': report.warehouse_id.id,
                'location_src_id': report.location_id.id,
                'product_id': report.product_id.id,
                'uom_id': report.uom_id.id,
                'product_uom_qty': report.product_qty,
                'prodlot_id': report.prodlot_id.id,
                'tracking_id': report.tracking_id.id,
                'product_packaging_id': report.product_id.packaging \
                    and len(report.product_id.packaging) == 1 \
                    and report.product_id.packaging[0].id or False,
            })

        return values

    def _prepare_picking(self, cr, uid, wizard, address_id, context=None):
        """
        @param wizard : browse of wizard
        @param address_id : id of partner address
        """
        return {
            'name': _('Warehouse Transfer'),
            'type': 'internal',
            'state': 'draft',
            'move_type': 'one',
            'address_id': address_id,
            'invoice_state': 'none',
            'company_id': wizard.warehouse_src_id.company_id.id,
        }

    def _prepare_move(self, cr, uid, wizard, address_id, picking_id, context=None):
        """
        @param wizard : browse of wizard
        @param address_id : id of partner address
        @param picking_id : id of picking
        """
        product_obj = self.pool.get('product.product')
        return {
            'name': product_obj.name_get(cr, uid, [wizard.product_id.id], context=context)[0][1],
            'picking_id': picking_id,
            'product_id': wizard.product_id.id,
            'date': wizard.date_expected,
            'date_expected': wizard.date_expected,
            'product_qty': wizard.product_uom_qty,
            'product_uom': wizard.uom_id.id,
            'product_uos_qty': wizard.product_uom_qty,
            'product_uos': wizard.uom_id.id,
            'product_packaging': wizard.product_packaging_id.id and wizard.product_packaging_id.id or False,
            'address_id': address_id,
            'location_id': wizard.location_src_id.id,
            'location_dest_id': wizard.location_dest_id.id,
            'tracking_id': wizard.tracking_id and wizard.tracking_id.id or False,
            'prodlot_id': wizard.prodlot_id and wizard.prodlot_id.id or False,
            'state': 'draft',
            'company_id': wizard.company_id.id,
        }

    def _prepare_procurement(self, cr, uid, wizard, move_id, context=None):
        """
        @param wizard : browse of wizard
        @param move_id : id of move
        """
        product_obj = self.pool.get('product.product')
        return {
            'name': product_obj.name_get(cr, uid, [wizard.product_id.id], context=context)[0][1],
            'origin': _('Warehouse Transfer'),
            'date_planned': wizard.date_expected,
            'product_id': wizard.product_id.id,
            'product_qty': wizard.product_uom_qty,
            'product_uom': wizard.uom_id.id,
            'product_uos_qty': wizard.product_uom_qty,
            'product_uos': wizard.uom_id.id,
            'location_id': wizard.location_src_id.id,
            'procure_method': 'make_to_order',
            'move_id': move_id,
            'company_id': wizard.company_id.id,
        }

    def validate(self, cr, uid, ids, context=None):
        """
        Modify moves quantities
        """
        move_obj = self.pool.get('stock.move')
        pick_obj = self.pool.get('stock.picking')
        product_obj = self.pool.get('product.product')
        proc_obj = self.pool.get('procurement.order')
        wf_service = netsvc.LocalService("workflow")
        for wizard in self.browse(cr, uid, ids, context=context):
            if wizard.warehouse_src_id == wizard.warehouse_dest_id:
                raise osv.except_osv(_('Error !'),
                        _("The warehouses source and destination must be different!"))
            if not wizard.product_uom_qty:
                raise osv.except_osv(_('Error !'),
                        _("Please fill the quantity to transfer!"))
            picking_ids = pick_obj.search(cr, uid, [
                ('state', '=', 'draft'),
                ('user_id', '=', uid)
            ], context=context)
            address_id = wizard.location_dest_id.address_id and wizard.location_dest_id.address_id.id \
                    or wizard.warehouse_dest_id.partner_address_id and wizard.warehouse_dest_id.partner_address_id.id \
                    or False
            if picking_ids:
                picking_id = picking_ids[0]
            else:
                picking_id = pick_obj.create(cr, uid, self._prepare_picking(cr, uid, wizard, address_id, context=context), context=context)
            move_id = move_obj.create(cr, uid, self._prepare_move(cr, uid, wizard, address_id, picking_id, context=context), context=context)
            proc_id = proc_obj.create(cr, uid, self._prepare_procurement(cr, uid, wizard, move_id, context=context), context=context)
            if wizard.last_transfer:
                wf_service.trg_validate(uid, 'stock.picking', picking_id, 'button_confirm', cr)
                wf_service.trg_validate(uid, 'procurement.order', proc_id, 'button_confirm', cr)
        return {}

stock_warehouse_transfer()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
