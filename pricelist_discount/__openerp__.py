# -*- coding: utf-8 -*-
##############################################################################
#
#    pricelist_discount module for OpenERP, Pricelist Discount
#    Copyright (C) 2009 SYLEAM Info Services (<http://www.syleam.fr/>)
#              Jean-Sébastien SUZANNE <jean-sebastien.suzanne@syleam.fr>
#    Copyright (C) 2012 SYLEAM Info Services (<http://www.syleam.fr/>)
#              Benoît MOTTIN <benoit.mottin@syleam.fr>
#              Sebastien LANGE <sebastien.lange@syleam.fr>
#
#    This file is a part of pricelist_discount
#
#    pricelist_discount is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    pricelist_discount is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Pricelist Discount',
    'version': '0.1.2',
    'category': 'Sales Management',
    'description': """Add discount in pricelist""",
    'author': 'SYLEAM',
    'depends': [
            'base',
            'product',
        ],
    'init_xml': [],
    'update_xml': [
        'product_view.xml',
        ],
    'demo_xml': [],
    'installable': True,
    'active': False,
    'license': 'AGPL-3',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
