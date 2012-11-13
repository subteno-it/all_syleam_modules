# -*- coding: utf-8 -*-
##############################################################################
#
#    stock_scanner_print module for OpenERP, Allows to attach a printer to a barcode scanner
#    Copyright (C) 2012 SYLEAM Info Services (<http://www.Syleam.fr/>)
#              Sylvain Garancher <sylvain.garancher@syleam.fr>
#
#    This file is a part of stock_scanner_print
#
#    stock_scanner_print is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    stock_scanner_print is distributed in the hope that it will be useful,
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


class scanner_hardware(osv.osv):
    _inherit = 'scanner.hardware'

    _columns = {
        'default_printer_id': fields.many2one('printers.list', 'Default Printer', help='Default printer used by this hardware'),
    }

scanner_hardware()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
