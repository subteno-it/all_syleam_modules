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
from osv import fields
import re


class email_server_mapping_field(osv.osv):
    _name = 'email.server.mapping.field'
    _description = 'Variable to field mapping'
    _order = 'field_id, sequence, id'

    _columns = {
        'email_server_id': fields.many2one('email.server', 'Email server', help='Email server configuration'),
        'field_id': fields.many2one('ir.model.fields', 'Field', required=True, help='The model\'s field on which the variable value will be written, if found'),
        'pattern': fields.char('Pattern', size=128, required=True, help='Pattern which will be sarched for to find the field\'s value.\nPut (.*?) for the variable part.\nExample : [[phone:(.*?)]].\nIn case of full content, put only (.*), without the question mark.'),
        'message_part': fields.selection([
            ('body', 'Body'),
            ('subject', 'Subject'),
            ('to', 'To'),
            ('cc', 'CC'),
            ('from', 'From'),
            ('reply-to', 'Reply to'),
            ('in-reply-to', 'In reply to'),
            ('date', 'Date'),
            ('references', 'References'),
        ], 'Message Part', required=True, help='This field defines the part of the email where the data will be searched for'),
        'sequence': fields.integer('Sequence', help='Will concatenate fields contents ordered by sequence'),

    }

    _defaults = {
        'pattern': '[[Field identifier:(.*?)]]',
        'message_part': 'body',
        'sequence': 1,
    }

email_server_mapping_field()


class email_server(osv.osv):
    _inherit = 'email.server'

    _columns = {
        'mapping_field_ids': fields.one2many('email.server.mapping.field', 'email_server_id', 'Mapping fields', help='Allow to map fields with custom variables in email body'),
    }

    def list_mapping_fields(self, cr, uid, ids, context=None):
        """
        Generates a list of patterns to fetch specific fields from message body
        """
        mapping_fields_data = {}

        for email_server in self.browse(cr, uid, ids, context=context):
            mapping_fields_data[email_server.id] = []
            # Generates a list of patterns, format : [(field_name, pattern)]
            for mapping_field in email_server.mapping_field_ids:
                # Escape all regex special characters but (.*?) from pattern
                mapping_fields_data[email_server.id].append((mapping_field.field_id.name, mapping_field.message_part, re.sub('([[\^$|+])', '\\\\\\1', mapping_field.pattern)))

        return mapping_fields_data

    def fetch_mail(self, cr, uid, ids, context=None):
        """
        Redefine the fetch_mail method to add custm parameters
        """
        if context is None:
            context = {}

        for server in self.browse(cr, uid, ids, context=context):
            # Add patterns in context
            context['mapping_fields'] = server.list_mapping_fields(context=context)[server.id]

            # Call to super for standard behaviour
            super(email_server, self).fetch_mail(cr, uid, [server.id], context=context)

            # Destroy value, it must not be reused automatically for the next mail
            del(context['mapping_fields'])

email_server()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
