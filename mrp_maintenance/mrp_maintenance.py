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


class mrp_maintenance_type(osv.osv):
    _name = 'mrp.maintenance.type'
    _description = 'Maintenance Type'

    _columns = {
        'name': fields.char('Name', size=64, required=True, help='Name of type'),
        'code': fields.char('Code', size=64, help='Code of type'),
        'is_invoice': fields.boolean('Invoice ?', help='If set, the maintenance can be invoice'),
        'type': fields.selection([('all', 'All'), ('mrp', 'Maintenance Order'), ('lot', 'Production Lot')], 'Type', help='Maintenance Order : Use for Production order\nProduction Lot: use for Production Lot\nAll: use for twice'),
    }

    _defaults = {
        'is_invoice': False,
    }

mrp_maintenance_type()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
