# -*- coding: utf-8 -*-
##############################################################################
#
#    wms_crossdock module for OpenERP, Extension of WMS : Crossdocking management
#    Copyright (C) 2012 SYLEAM Info Services (<http://www.syleam.fr/>)
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

{
    'name': 'WMS Crossdock',
    'version': '1.0',
    'category': 'Generic Modules/Inventory Control',
    'description': """Extension of WMS : Crossdocking management

/!\ WARNING /!\\
THIS MODULE DOESN'T MANAGE PRODUCTS LOTS YET !""",
    'author': 'SYLEAM',
    'website': 'http://www.syleam.fr/',
    'depends': [
        'base',
        'wms',
        'stock_location',
    ],
    'init_xml': [],
    'images': [],
    'update_xml': [
        'product_view.xml',
        'stock_view.xml',
        'wms_crossdock_data.xml',
        #'security/groups.xml',
        #'security/ir.model.access.csv',
    ],
    'demo_xml': [],
    'test': [],
    #'external_dependancies': {'python': ['kombu'], 'bin': ['which']},
    'installable': True,
    'active': False,
    'license': 'AGPL-3',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
