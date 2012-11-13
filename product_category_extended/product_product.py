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
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    product_category_extended is distributed in the hope that it will be useful,
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
from tools.translate import _


class product_category(osv.osv):
    _inherit = 'product.category'

    _columns = {
        'sale_taxes_ids': fields.many2many('account.tax', 'product_cat_tax_cust_rel', 'cat_id', 'tax_id', 'Sale Taxes', domain=[('parent_id', '=', False), ('type_tax_use', 'in', ['sale', 'all'])], help='Taxes applied on sale orders'),
        'purchase_taxes_ids': fields.many2many('account.tax', 'product_cat_tax_supp_rel', 'cat_id', 'tax_id', 'Purchase Taxes', domain=[('parent_id', '=', False), ('type_tax_use', 'in', ['purchase', 'all'])], help='Taxes applied on purchase orders'),
        'uom_id': fields.many2one('product.uom', 'Default UoM', help='Default Unit of Measure'),
        'uom_po_id': fields.many2one('product.uom', 'Purchase UoM', help='Unit of Measure for purchase'),
        'uos_id': fields.many2one('product.uom', 'Unit of Sale', help='See product definition'),
        'uos_coef': fields.float('UOM -> UOS coef', digits=(16,4), help='See product definition'),
    }

product_category()



class product_product(osv.osv):
    _inherit = 'product.product'

    def onchange_category(self, cr, uid, ids, category_id, context=None):
        """
        When category changes, we search for taxes, UOM and product type
        """
        if context is None:
            context = self.pool.get('res.users').context_get(cr, uid, context=context)

        res = {}
        warn = False

        if not category_id:
            res = {
                'categ_id': False,
                'uom_id': False,
                'uom_po_id': False,
                'taxes_id': [],
                'supplier_taxes_id': [],
            }
        else:
            # Search for the default value on this category
            category_data = self.pool.get('product.category').read(cr, uid, category_id, [], context=context)
            res['categ_id'] = category_id
            if category_data['sale_taxes_ids']:
                res['taxes_id'] = category_data['sale_taxes_ids']
            if category_data['purchase_taxes_ids']:
                res['supplier_taxes_id'] = category_data['purchase_taxes_ids']
            if category_data['uom_id']:
                res['uom_id'] = category_data['uom_id']
            if category_data['uom_po_id']:
                res['uom_po_id'] = category_data['uom_po_id']
            if category_data['uos_id']:
                res['uos_id'] = category_data['uos_id']
                res['uos_coef'] = category_data['uos_coef']

            if ids:
                warn = {
                    'title': _('Caution'),
                    'message': _("""The product category has changed, thanks to control :
* Sale and Purchase taxes
* Unit sale and stock
* The price with return unit"""),
                }

        return {'value': res, 'warning': warn}

product_product()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
