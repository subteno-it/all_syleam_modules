# -*- coding: utf-8 -*-
##############################################################################
#
#    sale_pricelist_discount module for OpenERP, Sale pricelist discount
#    Copyright (C) 2009 SYLEAM Info Services (<http://www.syleam.fr/>)
#              Jean-Sébastien SUZANNE <jean-sebastien.suzanne@syleam.fr>
#    Copyright (C) 2012 SYLEAM Info Services (<http://www.syleam.fr/>)
#              Benoît MOTTIN <benoit.mottin@syleam.fr>
#              Sebastien LANGE <sebastien.lange@syleam.fr>
#
#    This file is a part of sale_pricelist_discount
#
#    sale_pricelist_discount is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    sale_pricelist_discount is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import osv
import time
from tools import DEFAULT_SERVER_DATE_FORMAT


class sale_order_line(osv.osv):
    _inherit = 'sale.order.line'

    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False, context=None):
        """
        Get discount if exists
        """
        result =  super(sale_order_line, self).product_id_change( cr, uid, ids, pricelist, product, qty,
            uom, qty_uos, uos, name, partner_id,
            lang, update_tax, date_order, packaging, fiscal_position, flag, context=context)
        if not product:
            return result
        if not date_order:
            date_order = time.strftime(DEFAULT_SERVER_DATE_FORMAT)

        # get discount
        price_dict = self.pool.get('product.pricelist').price_get(cr, uid, [pricelist],
                product, qty or 1.0, partner_id, {
                    'uom': uom or self.pool.get('product.product').browse(cr, uid, product, context=context).uom_id.id,
                    'date': date_order,
                    'discount': True,
                    })
        if price_dict.get('discount', False):
            result['value']['discount'] = price_dict['discount']
        return result

sale_order_line()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
