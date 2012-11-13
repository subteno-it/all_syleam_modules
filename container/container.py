# -*- coding: utf-8 -*-
##############################################################################
#
#    container module for OpenERP, Manages containers receipt
#    Copyright (C) 2011 SYLEAM Info Services (<http://www.Syleam.fr/>)
#              Sylvain Garancher <sylvain.garancher@syleam.fr>
#
#    This file is a part of container
#
#    container is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    container is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


from osv import osv
from osv import fields
from datetime import datetime, timedelta
from tools.translate import _
import netsvc


class stock_container(osv.osv):
    _name = 'stock.container'
    _description = 'Container'

    def _compute_values(self, cr, uid, ids, field_name, arg, context=None):
        """
        Computes weight, volume and remaining volume values
        """
        res = {}

        for container in self.browse(cr, uid, ids, context=context):
            weight = volume = 0.

            # Add values from each move
            for move in container.incoming_move_list_ids:
                weight += move.product_qty * move.product_id.weight_net
                volume += move.product_qty * move.product_id.volume

            res[container.id] = {
                'weight': weight,
                'volume': volume,
                'remaining_volume': container.product_id.volume - volume,
            }

        return res

    _columns = {
        'name': fields.char('Name', size=64, required=True, help='Name of the container'),
        'partner_id': fields.many2one('res.partner', 'Freight Broker', readonly=True,
                                      states={'draft': [('readonly', False)], 'booking': [('readonly', False), ('required', True)]},
                                      help='Partner whom shipping container'),
        'address_id': fields.many2one('res.partner.address', 'Address to retrieve the container', readonly=True,
                                      states={'draft': [('readonly', False)], 'booking': [('readonly', False), ('required', True)]},
                                      help='Address whom the container is located, used to retrieve it'),
        'sscc': fields.char('SSCC', size=18, readonly=True,
                            states={'draft': [('readonly', False)], 'booking': [('readonly', False), ('required', True)]},
                            help='Serial Shipping Container Code : unique worldwide identifier for shipping units (given by the shipping company at booking). This field should be formatted to 18 numeric character.'),
        'etd_date': fields.date('Date of departure', readonly=True,
                                states={'draft': [('readonly', False)], 'booking': [('readonly', False), ('required', True)]},
                                help='Date of departure'),
        'eta_date': fields.date('Estimated date of arrival', readonly=True,
                                states={'booking': [('readonly', False), ('required', True)], 'freight': [('readonly', False), ('required', True)]},
                                help='Estimated date of arrival'),
        'etm_date': fields.date('Estimated time to market',
                                states={'draft': [('readonly', True)], 'unpacking': [('readonly', True)], 'cancel': [('readonly', True)], 'delivered': [('readonly', True)]},
                                help='Estimated date products available for delivery to customer'),
        'rdv_date': fields.datetime('RDV', readonly=True,
                                    states={'approaching': [('required', True), ('readonly', False)]},
                                    help='Date and time at which the transporter will show up at final destination to deliver the container'),
        'weight': fields.function(_compute_values, method=True, string='Weight', type='float', store=False, multi='values', help='The total weight of all products listed in incoming move lists of the container'),
        'volume': fields.function(_compute_values, method=True, string='Volume', type='float', store=False, multi='values', help='The total GROSS volume of all products listed in incoming move lists of the container'),
        'remaining_volume': fields.function(_compute_values, method=True, string='Remaining Volume', type='float', store=False, multi='values', help='The substraction of the container product gross volume minus the total GROSS volume of all products listed in incoming move lists of the container'),
        'product_id': fields.many2one('product.product', 'Product', required=True,
                                      states={'draft': [('readonly', False)]},
                                      help='The container product'),
        'incoterm_id': fields.many2one('stock.incoterms', 'Incoterm', required=True, help='Incoterm'),
        'container_stock_location_id': fields.many2one('stock.location', 'Container Stock Location', required=True, readonly=True,
                                                       states={'draft': [('readonly', False)]},
                                                       help='Stck location of the container\'s contents'),
        'destination_warehouse_id': fields.many2one('stock.warehouse', 'Destination Warehouse', required=True,
                                                    states={'cancel': [('readonly', True)], 'delivered': [('readonly', True)]},
                                                    help='Warehouse destination of the container\'s contents'),
        'incoming_move_list_ids': fields.many2many('stock.move', 'stock_container_move_rel', 'container_id', 'move_id', 'Incoming Shipments',
                                                   domain="[ ('picking_id.type', '=', 'in'), ('state', '=', 'assigned'), '|', ('location_id.categ_id.id', '=', container_stock_location_id), ('location_id.categ_id', '=', False)]",
                                                   readonly=True,
                                                   states={'draft': [('readonly', False)]},
                                                  ),
        'move_line_ids': fields.one2many('stock.move', 'container_id', 'Outgoing Move List', readonly=True, help='Stock Moves'),
        'state': fields.selection([('draft', 'Draft'),
                                   ('booking', 'Booking'),
                                   ('freight', 'Freight'),
                                   ('clearance', 'Clearance'),
                                   ('approaching', 'Approaching'),
                                   ('unpacking', 'Unpacking'),
                                   ('delivered', 'Delivered'),
                                   ('cancel', 'Cancel')],
                                  'Status', readonly=True,
                                  help="""Status of the container:
  - Booking : The shipping company is preparing to ship
  - Freight : The container is on the sea
  - Clearance : The container is undergoing custom clearance
  - Approaching : The container is being transported locally to its final destination and a meeting is organized with the logistic guy at destination location
  - Unpacking : The container is being unpacked at its final destination
  - Delivered : the container is archived with all fields locked"""),
        'prod_serial': fields.related('product_id', 'code', type='char', string='Product serial no.', help='Serial number of the product'),
    }

    _defaults = {
        'state': 'draft',
    }

    def get_dates_from_moves(self, cr, uid, container_id, context=None):
        """
        Modify container's dates from moves dates
        """
        container = self.browse(cr, uid, container_id, context=context)

        # Get the highest date of the moves
        moves_list = [datetime.strptime(move.date, '%Y-%m-%d %H:%M:%S') for move in container.move_line_ids]
        if not moves_list:
            return {}

        # Compute dates values
        date_etm = max(moves_list)
        eta_date = date_etm - timedelta(container.product_id.produce_delay or 0)
        etd_date = date_etm - timedelta(container.product_id.sale_delay or 0)
        # Set container's default dates
        values = {
            'etd_date': etd_date.strftime('%Y-%m-%d'),
            'eta_date': eta_date.strftime('%Y-%m-%d'),
            'etm_date': date_etm.strftime('%Y-%m-%d'),
            'rdv_date': date_etm.strftime('%Y-%m-%d'),
        }

        return values

    def write(self, cr, uid, ids, values, context=None):
        """
        Write method
        """
        res_users_obj = self.pool.get('res.users')

        company = res_users_obj.browse(cr, uid, uid, context=context).company_id

        for container in self.browse(cr, uid, ids, context=context):
            # Write new dates on container
            new_dates = self.get_dates_from_moves(cr, uid, container.id, context=context)

            etd_date = values.get('etd_date', False) or container.etd_date or new_dates.get('etd_date', False)
            if etd_date:
                values['etd_date'] = etd_date,

            eta_date = values.get('eta_date', False) or container.eta_date or new_dates.get('eta_date', False)
            if eta_date:
                values['eta_date'] = eta_date,

            etm_date = values.get('etm_date', False) or container.etm_date or new_dates.get('etm_date', False)
            if etm_date:
                values['etm_date'] = etm_date,

            rdv_date = values.get('rdv_date', False) or container.rdv_date or new_dates.get('rdv_date', False)
            if rdv_date:
                values['rdv_date'] = rdv_date,

            res = super(stock_container, self).write(cr, uid, ids, values, context=context)

            if company.container_updates_dates:
                # Adjusts dates on moves
                if values.get('state', container.state) not in ('draft', 'booking'):
                    stock_move_obj = self.pool.get('stock.move')
                    stock_picking_obj = self.pool.get('stock.picking')

                    move_ids = [move.id for move in container.move_line_ids]
                    stock_move_obj.write(cr, uid, move_ids, {'date': values.get('etm_date', container.etm_date)}, context=context)

                    # Search pickings to update their planned date
                    stock_move_data = stock_move_obj.read(cr, uid, move_ids, ['picking_id'], context=context)
                    picking_ids = [data['picking_id'][0] for data in stock_move_data if data.get('picking_id', False)]
                    for picking in stock_picking_obj.browse(cr, uid, picking_ids, context=context):
                        new_date = max([datetime.strptime(move.date, '%Y-%m-%d %H:%M:%S') for move in picking.move_lines])
                        picking.write({'min_date': new_date.strftime('%Y-%m-%d')})

        return res

    def unlink(self, cr, uid, ids, context=None):
        """
        Disable Container deletion when not in draft
        """
        if [container.id for container in self.browse(cr, uid, ids, context=context) if container.state == 'draft']:
            raise osv.except_osv(_('Error'), _('A container must be in state draft to be deleted !'))

        res = super(stock_container, self).unlink(cr, uid, ids, context=context)
        return res

    def action_draft(self, cr, uid, ids, context=None):
        """
        Action lanched when the user want to revert in draft
        """

        for container in self.browse(cr, uid, ids, context=context):
            # Chek if the user filled picking in in this container before booking
            if container.move_line_ids:
                # Read incoming move list
                move_ids = [move.id for move in container.move_line_ids]
                self.pool.get('stock.move').unlink(cr, uid, move_ids, context=context)

        return True

    def action_booking(self, cr, uid, ids, context=None):
        """
        Action lanched when arriving on booking state
        """
        if context is None:
            # There is no context in workflow, so get it on user
            context = self.pool.get('res.users').context_get(cr, uid, context=context)

        stock_move_obj = self.pool.get('stock.move')

        for container in self.browse(cr, uid, ids, context=context):
            # Check container's location
            #if container.incoterm_id.code in ['EXW', 'FCA', 'FAS', 'FOB', 'CFR', 'CIF', 'CPT', 'CIP'] and container.container_stock_location_id.usage != 'internal':
            #    raise osv.except_osv(_('Warning !'), _('You must define container stock location as company location !'))
            #elif container.incoterm_id.code in ['DAF', 'DES', 'DES', 'DDU', 'DDP'] and container.container_stock_location_id.usage != 'supplier':
            #    raise osv.except_osv(_('Warning !'), _('You must define container stock location as supplier location !'))
            #FIXME : In version 6, we must have the stock location in internal else impossible to create invoice supplier
            if container.container_stock_location_id.usage != 'supplier':
                raise osv.except_osv(_('Warning !'), _('You must define container stock location as supplier location !'))

            # Check remaining volume
            if container.remaining_volume < 0:
                raise osv.except_osv(_('Warning !'), _('Remaining volume must be positive !'))

            # Chek if the user filled picking in in this container before booking
            if not container.incoming_move_list_ids:
                raise osv.except_osv(_('Warning !'), _('You must select incoming shipmets before booking !'))

            # Create outgoing moves from incoming moves
            default = {
                'state': 'draft',
                'picking_id': False,
                'container_id': container.id,
                'location_dest_id': container.container_stock_location_id.id,
            }
            for move in container.incoming_move_list_ids:
                default['move_dest_id'] = move.id
                # Create the new move
                new_move_id = stock_move_obj.copy(cr, uid, move.id, default, context=context)

            # Read incoming move list
            move_ids = [move.id for move in container.incoming_move_list_ids]

            # Changes incoming moves' location to container's location
            stock_move_obj.write(cr, uid, move_ids, {'location_id': container.container_stock_location_id.id}, context=context)

        return True

    def action_freight(self, cr, uid, ids, context=None):
        """
        Action lanched when arriving on freight state
        """
        if context is None:
            context = {}

        partial_id = self.pool.get("stock.partial.container").create(
            cr, uid, {}, context=dict(context, active_ids=ids))
        return {
            'name':_("Products to Process"),
            'view_mode': 'form',
            'view_id': False,
            'view_type': 'form',
            'res_model': 'stock.partial.container',
            'res_id': partial_id,
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': dict(context, active_ids=ids)
        }

    def action_clearance(self, cr, uid, ids, context=None):
        """
        Action lanched when arriving on clearance state
        """
        return True

    def action_unpacking(self, cr, uid, ids, context=None):
        """
        Action lanched when arriving on unpacking state
        """
        return True

    def action_cancel(self, cr, uid, ids, context=None):
        """
        Action lanched when arriving on cancel state
        """
        if context is None:
            # There is no context in workflow, so get it on user
            context = self.pool.get('res.users').context_get(cr, uid, context=context)

        for container in self.browse(cr, uid, ids, context=context):
            # Error if one of the incoming pickings is in cancel state
            if [move.picking_id.id for move in container.incoming_move_list_ids if move.picking_id.state != 'cancel']:
                raise osv.except_osv(_('Warning !'), _('Incoming or outgoing packing list not in cancel state !'))

        return True

    def action_deliver(self, cr, uid, ids, context=None):
        """
        Action lanched when arriving on delivered state
        """
        if context is None:
            context = {}
        wf_service = netsvc.LocalService("workflow")

        for container in self.browse(cr, uid, ids, context=context):
            picking_ids = [move.picking_id.id for move in container.incoming_move_list_ids]
            wf_service.trg_validate(uid, 'stock.container', container.id, 'button_deliver', cr)

        partial_id = self.pool.get("stock.partial.picking").create(
            cr, uid, {}, context=dict(context, active_ids=picking_ids, container_ids=ids))
        return {
            'name':_("Products to Process"),
            'view_mode': 'form',
            'view_id': False,
            'view_type': 'form',
            'res_model': 'stock.partial.picking',
            'res_id': partial_id,
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': dict(context, active_ids=picking_ids, container_ids=ids)
        }

    def copy(self, cr, uid, id, default=None, context=None):
        """
        Removes some values to avoid creating duplicate pickings
        """

        default = {
            'incoming_move_list_ids': [],
            'move_line_ids': [],
        }

        return super(stock_container, self).copy(cr, uid, id, default, context=context)

    def onchange_etd_date(self, cr, uid, ids, new_date, context=None):
        """
        Change date of container
        """
        date_etd = datetime.strptime(new_date, '%Y-%m-%d')
        for container in self.browse(cr, uid, ids, context=context):
            etm_date = date_etd + timedelta(container.product_id.sale_delay or 0)
            eta_date = etm_date - timedelta(container.product_id.produce_delay or 0)
        return {'value': {
            'eta_date': eta_date.strftime('%Y-%m-%d'),
            'etm_date': etm_date.strftime('%Y-%m-%d'),
            'rdv_date': etm_date.strftime('%Y-%m-%d'),
        }}

    def onchange_eta_date(self, cr, uid, ids, new_date, context=None):
        """
        Change date of container
        """
        date_eta = datetime.strptime(new_date, '%Y-%m-%d')
        for container in self.browse(cr, uid, ids, context=context):
            etm_date = date_eta + timedelta(container.product_id.produce_delay or 0)
            if container.state in ('draft', 'booking'):
                etd_date = etm_date - timedelta(container.product_id.sale_delay or 0)
                return {'value': {
                    'etd_date': etd_date.strftime('%Y-%m-%d'),
                    'etm_date': etm_date.strftime('%Y-%m-%d'),
                    'rdv_date': etm_date.strftime('%Y-%m-%d'),
                }}
            return {'value': {
                'etm_date': etm_date.strftime('%Y-%m-%d'),
                'rdv_date': etm_date.strftime('%Y-%m-%d'),
            }}

    def onchange_etm_date(self, cr, uid, ids, new_date, context=None):
        """
        Change date of container
        """
        date_etm = datetime.strptime(new_date, '%Y-%m-%d')
        for container in self.browse(cr, uid, ids, context=context):
            if container.state in ('draft', 'booking'):
                eta_date = date_etm - timedelta(container.product_id.produce_delay or 0)
                etd_date = date_etm - timedelta(container.product_id.sale_delay or 0)
                return {'value': {
                    'eta_date': eta_date.strftime('%Y-%m-%d'),
                    'etd_date': etd_date.strftime('%Y-%m-%d'),
                    'rdv_date': date_etm.strftime('%Y-%m-%d'),
                }}
            elif container.state == 'freight':
                etd_date = date_etm - timedelta(container.product_id.sale_delay or 0)
                return {'value': {
                    'etd_date': etd_date.strftime('%Y-%m-%d'),
                    'rdv_date': date_etm.strftime('%Y-%m-%d'),
                }}
            else:
                return {'value': {
                    'rdv_date': date_etm.strftime('%Y-%m-%d'),
                }}

stock_container()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
