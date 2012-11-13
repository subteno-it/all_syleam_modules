# -*- coding: utf-8 -*-
##############################################################################
#
#    fetchmail_parsing module for OpenERP, Allows to map variable names inside email body to fields on related model
#    Copyright (C) 2011 SYLEAM Info Services (<http://www.Syleam.fr/>)
#              Sylvain Garancher <sylvain.garancher@syleam.fr>
#
#    This file is a part of fetchmail_parsing
#
#    fetchmail_parsing is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    fetchmail_parsing is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import osv
import re
import email
import tools
import xmlrpclib
from tools import ustr


class email_server_tools(osv.osv_memory):
    _inherit = 'email.server.tools'

    def _get_message_parts(self, message):
        """
        Extracts all parts from a message and returns them in a dict
        Code from the mail_gateway module
        """
        if isinstance(message, xmlrpclib.Binary):
            message = str(message.data)

        # Warning: message_from_string doesn't always work correctly on unicode,
        # we must use utf-8 strings here :-(
        if isinstance(message, unicode):
            message = message.encode('utf-8')

        msg_txt = email.message_from_string(message)
        msg = {}

        fields = msg_txt.keys()

        if 'Subject' in fields:
            msg['subject'] = self._decode_header(msg_txt.get('Subject'))

        if 'Content-Type' in fields:
            msg['content-type'] = msg_txt.get('Content-Type')

        if 'From' in fields:
            msg['from'] = self._decode_header(msg_txt.get('From'))

        if 'Delivered-To' in fields:
            msg['to'] = self._decode_header(msg_txt.get('Delivered-To'))

        if 'CC' in fields:
            msg['cc'] = self._decode_header(msg_txt.get('CC'))

        if 'Reply-to' in fields:
            msg['reply-to'] = self._decode_header(msg_txt.get('Reply-To'))

        if 'Date' in fields:
            msg['date'] = self._decode_header(msg_txt.get('Date'))

        if 'Content-Transfer-Encoding' in fields:
            msg['encoding'] = msg_txt.get('Content-Transfer-Encoding')

        if 'References' in fields:
            msg['references'] = msg_txt.get('References')

        if 'In-Reply-To' in fields:
            msg['in-reply-to'] = msg_txt.get('In-Reply-To')

        if not msg_txt.is_multipart() or 'text/plain' in msg.get('Content-Type', ''):
            encoding = msg_txt.get_content_charset()
            body = msg_txt.get_payload(decode=True)

            if 'text/html' in msg_txt.get('Content-Type', ''):
                body = tools.html2plaintext(body)

            msg['body'] = tools.ustr(body, encoding)

        return msg

    def process_email(self, cr, uid, model, message, custom_values=None, attach=True, context=None):
        """
        Adds custom values on created object from email
        """
        if context is None:
            context = {}

        if custom_values is None:
            custom_values = {}

        model_obj = self.pool.get(model)

        message_parts = self._get_message_parts(message)

        # Retrieve information about the fields
        field_informations = model_obj.fields_get(cr, uid, [], context=context)
        # Search for patterns for specific fields
        for field_name, message_part, pattern in context.get('mapping_fields', {}):
            # Add the re.S flag to allow multi line matching data
            field_data = re.search(pattern, message_parts.get(message_part, ''), re.S)
            # If the pattern matches, add its value in custom values
            if field_data:
                # Retrieve data sent by email
                field_value = field_data.group(1)

                # If we fill a m2o field, call name_search
                if field_informations[field_name]['type'] == 'many2one':
                    name_search_value = self.pool.get(field_informations[field_name]['relation']).name_search(cr, uid, field_value.strip(), context=context)
                    if name_search_value:
                        custom_values[field_name] = name_search_value[0][0]
                else:
                    # Add data in custom_values
                    custom_values[field_name] = ' '.join((custom_values.get(field_name, ''), ustr(field_value).replace('&#13;', '')))

        return super(email_server_tools, self).process_email(cr, uid, model, message, custom_values=custom_values, attach=attach, context=context)

email_server_tools()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
