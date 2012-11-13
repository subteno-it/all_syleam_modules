# -*- coding: utf-8 -*-
##############################################################################
#
#    product_category_extended module for OpenERP, Add onchange on product category to fill sale and purchase taxes and uom on product
#    Copyright (C) 2011 SYLEAM Info Services (<http://www.Syleam.fr/>)
#              Sylvain Garancher <sylvain.garancher@syleam.fr>
#
#    This file is a part of product_category_extended
#
#    product_category_extended is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    product_category_extended is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Product Category Extended',
    'version': '1.0',
    'category': 'Generic Modules/Inventory Control',
    'description': """Add onchange on product category to fill sale and purchase taxes and uom on product""",
    'author': 'SYLEAM',
    'website': 'http://www.syleam.fr/',
    'depends': [
        'product',
        'stock',
        'account',
    ],
    'init_xml': [],
    'images': [],
    'update_xml': [
        #'security/ir.model.access.csv',
        #'wizard/wizard.xml',
        'product_product_view.xml',
    ],
    'demo_xml': [],
    'test': [],
    #'external_dependancies': {'python': ['kombu'], 'bin': ['which']},
    'installable': True,
    'active': False,
    'license': 'AGPL-3',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
