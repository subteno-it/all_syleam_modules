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

{
    'name': 'MRP Maintenance',
    'version': '1.0',
    "category" : "Manufacturing",
    'description': """Manage maintenance in production order""",
    'author': 'SYLEAM',
    'website': 'http://www.syleam.fr/',
    'depends': [
        'base',
        'mrp',
        'sale',
        'stock',
    ],
    'init_xml': [],
    'images': [],
    'update_xml': [
        'sale_view.xml',
        'procurement_workflow.xml',
        'mrp_view.xml',
        'mrp_maintenance_view.xml',
        'mrp_workflow.xml',
        'stock_view.xml',
        'wizard/mrp_invoice_view.xml',
        'security/ir.model.access.csv',
    ],
    'demo_xml': [],
    'test': [],
    'installable': True,
    'application': True,
    'active': False,
    'license': 'AGPL-3',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
