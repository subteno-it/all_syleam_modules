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


class product_product(osv.osv):
    _inherit = 'product.product'

    _columns = {
        'location_type': fields.property(None, method=True, string='Location type', view_load=True, type='selection', selection=[
            ('compute', 'Compute'),
            ('fixed', 'Fixed'),
            ('crossdock', 'Crossdock')
        ], help='Type of location for this product'),
    }

product_product()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
