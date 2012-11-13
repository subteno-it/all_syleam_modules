# -*- coding: utf-8 -*-
##############################################################################
#
#    wms_routing module for OpenERP, This module allows to assing rounds to orders to set default locations automatically on moves
#    Copyright (C) 2011 SYLEAM Info Services (<http://www.Syleam.fr/>)
#              Sylvain Garancher <sylvain.garancher@syleam.fr>
#              Sebastien LANGE <sebastien.lange@syleam.fr>
#
#    This file is a part of wms_routing
#
#    wms_routing is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    wms_routing is distributed in the hope that it will be useful,
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


class sale_order(osv.osv):
    _inherit = 'sale.order'

    _columns = {
        'round_id': fields.many2one('stock.round', 'Round', help='Round for this sale order', readonly=True, states={'draft': [('readonly', False)]}),
    }

    def onchange_partner_id(self, cr, uid, ids, partner_id, context=None):
        """
        Redefine this method to fill round_id when changing partner
        """
        res = super(sale_order, self).onchange_partner_id(cr, uid, ids, partner_id)

        new_val = self.onchange_shipping_address(cr, uid, ids, partner_id, res['value']['partner_shipping_id'], None, context=context)

        if new_val:
            res['value']['round_id'] = new_val['value']['round_id']

        return res

    def onchange_shipping_address(self, cr, uid, ids, partner_id, partner_shipping_id, round_id, context=None):
        """
        Returns the round_id to put on this sale order
        """
        res = {}

        # If there is a round_id defined, we don't change the value
        if not round_id:

            # We search the round_id value on the address, then, on the partner
            if partner_shipping_id:
                res_partner_address_obj = self.pool.get('res.partner.address')
                partner_address_data = res_partner_address_obj.read(cr, uid, partner_shipping_id, ['round_id'], context=context)
                if partner_address_data and partner_address_data['round_id']:
                    res = {'value': {'round_id': partner_address_data['round_id'][0]}}

            if not res and partner_id:
                res_partner_obj = self.pool.get('res.partner')
                partner_data = res_partner_obj.read(cr, uid, partner_id, ['round_id'], context=context)
                if partner_data and partner_data['round_id']:
                    res = {'value': {'round_id': partner_data['round_id'][0]}}

        # No value found, we return nothing
        return res

sale_order()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
