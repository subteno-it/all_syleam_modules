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

from osv import osv
from osv import fields


class product_pricelist(osv.osv):
    _inherit = "product.pricelist"

    def price_get(self, cr, uid, ids, prod_id, qty, partner=None, context=None):
        """
        Add discount if set in result
        """
        result = super(product_pricelist, self).price_get(cr, uid, ids, prod_id, qty, partner=partner, context=context)
        if 'discount' in context:
            discount = self.pool.get('product.pricelist.item').browse(cr, uid, result['item_id'].values()[0], context=context).discount or False
            if discount:
                result.update({'discount': discount})
        return result

product_pricelist()


class product_pricelist_item(osv.osv):
    _inherit = 'product.pricelist.item'

    _columns = {
        'discount': fields.float('Discount (%)', digits=(16, 2)),
    }

    _defaults = {
        'discount': 0.0,
    }

product_pricelist_item()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
