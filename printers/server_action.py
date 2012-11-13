# -*- coding: utf-8 -*-
##############################################################################
#
#    printers module for OpenERP, Allow to manage printers un OpenERP
#    Copyright (C) 2011 SYLEAM Info Services (<http://www.Syleam.fr/>)
#              Sylvain Garancher <sylvain.garancher@syleam.fr>
#              Christophe CHAUVET <christophe.chauvet@syleam.fr>
#
#    This file is a part of printers
#
#    printers is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    printers is distributed in the hope that it will be useful,
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
import traceback
import logging
import time
from tools.translate import _

logger = logging.getLogger('printers')


class ir_actions_server(osv.osv):
    _inherit = 'ir.actions.server'

    _columns = {
        'printing_source': fields.char('Source', size=256, help='Add condition to found the id of the printer, use:\n- c for context\n- o for object\n- time for date and hour\n- u for user\n eg: o.warehouse_id.printer_id.id'),
        'printing_function': fields.char('Function', size=64, help='Name of the function to launch for printing.\nDEPRECATED'),
        'printing_report_id': fields.property('ir.actions.report.xml', method=True, string='Report', type='many2one', relation='ir.actions.report.xml', view_load=True, help='The report which will be printed'),
        'model_name': fields.related('model_id', 'model', type='char', string='Model Name', help='Name of the model, used to filter ir.actions.report.xml'),
    }

    _defaults = {
        'printing_source': False,
        'printing_function': False,
    }

    def __init__(self, pool, cr):
        """
        Extend to add 'printing' in state list
        """
        super(ir_actions_server, self).__init__(pool, cr)
        logger.info('Add printing as key')

        # Add printing as key
        states_list = self._columns['state'].selection
        if 'printing' not in [key for key, value in states_list]:
            self._columns['state'].selection.append(('printing', 'Printing'))

    def run(self, cr, uid, ids, context=None):
        """
        Executed by workflow
        """
        if context is None:
            context = {}

        result = False
        # Loop on actions to run
        for action in self.browse(cr, uid, ids, context=context):
            logger.debug('Action : %s' % action.name)

            # Check if there is an active_id (this situation should not appear)
            if not context.get('active_id', False):
                logger.warning('active_id not found in context')
                continue

            # Retrieve the model related object
            action_model_obj = self.pool.get(action.model_id.model)
            action_model = action_model_obj.browse(cr, uid, context['active_id'], context=context)

            # Check the action condition
            values = {
                'context': context,
                'object': action_model,
                'time': time,
                'cr': cr,
                'pool': self.pool,
                'uid': uid,
            }
            expression = eval(str(action.condition), values)
            if not expression:
                logger.debug('This action doesn\'t match with this object : %s' % action.condition)
                continue

            # If state is 'printing', execute the action
            if action.state == 'printing':
                # Get the printer id
                user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
                values = {
                    'c': context,
                    'o': action_model,
                    'time': time,
                    'u': user,
                }
                try:
                    # Retrieve the printer id
                    printer_id = eval(str(action.printing_source), values)

                    # Check if the printer was found
                    if not printer_id:
                        raise osv.except_osv(_('Error'), _('Printer not found !'))

                except Exception, e:
                    logger.error(traceback.format_exc())
                    raise osv.except_osv(_('Error'), _('Printer not found !'))

                # Get the report id
                # TODO : Check for a specific function, on action_model, which will return False or a report id. If False is returned, use the report put in the printing_report_id.
                # Prototype of the function : def get_printing_report_id(self, cr, uid, ids, context=None)
                # report_id = False
                # if getattr(action_model, 'get_printing_report_id', None) and callable(action_model.get_printing_report_id):
                #     report_id = action_model.get_printing_report_id()[action_model.id]
                #
                # if not report_id:
                report_id = action.printing_report_id.id

                # Log the printer and report id
                logger.debug('ID of the printer : %s' % str(printer_id))
                logger.debug('ID of the report : %s' % str(report_id))

                # Print the requested ir.actions.report.xml
                if report_id:
                    self.pool.get('printers.list').send_printer(cr, uid, printer_id, report_id, [action_model.id], context=context)
                else:
                    raise osv.except_osv(_('Error'), _('Report to print not found !'))

            # If the state is not 'printing', let the server action run itself
            else:
                result = super(ir_actions_server, self).run(cr, uid, [action.id], context=context)

        return result

ir_actions_server()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
