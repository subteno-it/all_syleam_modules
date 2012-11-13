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
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    wms_routing is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Stock Routing',
    'version': '1.0',
    'category': 'Generic Modules/Inventory Control',
    'description': """This module allows to assing rounds to orders to set default locations automatically on moves""",
    'author': 'SYLEAM',
    'website': 'http://www.syleam.fr/',
    'depends': [
        'base',
        'sale',
        'stock',
    ],
    'init_xml': [],
    'images': [],
    'update_xml': [
        'security/ir.model.access.csv',
        #'wizard/wizard.xml',
        'stock_round_view.xml',
        'base_view.xml',
        'sale_view.xml',
        'stock_view.xml',
        'ir_rule_data.xml',
    ],
    'demo_xml': [],
    'test': [
        'test/wms_routing_test01.yml',
        'test/wms_routing_test02.yml',
        'test/wms_routing_test03.yml',
        'test/wms_routing_test04.yml',
        'test/wms_routing_test05.yml',
        'test/wms_routing_test06.yml',
        'test/wms_routing_test07.yml',
        'test/wms_routing_test08.yml',
        'test/wms_routing_test09.yml',
        'test/wms_routing_test10.yml',
        'test/wms_routing_test11.yml',
        'test/wms_routing_test12.yml',
        'test/wms_routing_test13.yml',
        'test/wms_routing_test14.yml',
        'test/wms_routing_test15.yml',
        'test/wms_routing_test16.yml',
        'test/wms_routing_test17.yml',
        'test/wms_routing_test18.yml',
        'test/wms_routing_test19.yml',
#        'test/wms_routing_test20.yml',# TODO
#        'test/wms_routing_test21.yml',# TODO
#        'test/wms_routing_test22.yml',# TODO
#        'test/wms_routing_test23.yml',# TODO
        'test/wms_routing_test24.yml',
        'test/wms_routing_test25.yml',
        'test/wms_routing_test26.yml',
        'test/wms_routing_test27.yml',
        'test/wms_routing_test28.yml',
        'test/wms_routing_test29.yml',
#        'test/wms_routing_test30.yml',# TODO
    ],
    #'external_dependancies': {'python': ['kombu'], 'bin': ['which']},
    'installable': True,
    'active': False,
    'license': 'AGPL-3',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
