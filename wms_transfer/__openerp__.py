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

{
    'name': 'Wms Transfer',
    'version': '0.1',
    'category': 'Generic Modules/Inventory Control',
    'description': """Wizard for transfer product in stock in other warehouse""",
    'author': 'SYLEAM',
    'website': 'http://www.syleam.fr/',
    'depends': [
        'base',
        'wms',
    ],
    'init_xml': [],
    'images': [],
    'update_xml': [
        'wizard/warehouse_transfer_view.xml',
        'wms_view.xml',
        #'security/groups.xml',
        #'security/ir.model.access.csv',
        #'wizard/wizard.xml',
    ],
    'demo_xml': [],
    'test': [],
    'installable': True,
    'active': False,
    'license': 'AGPL-3',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
