# -*- coding: utf-8 -*-
##############################################################################
#
#    document_csv module for OpenERP
#    Copyright (C) 2009-2011 SYLEAM (<http://www.syleam.fr>) Christophe CHAUVET
#    Copyright (C) 2011 Camptocamp Guewen Baconnier
#
#    This file is a part of document_csv
#
#    document_csv is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    document_csv is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import osv, fields
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
import base64
from tools.translate import _


class ExportYaml(osv.osv_memory):

    _name = 'document.import.csv.export.yaml'

    _columns = {
        'name': fields.char('Filename', size=128),
        'filename': fields.binary('Select a filename and save it', required=True, filters='*.yml'),
    }

    def default_get(self, cr, uid, fields_list, context=None):
        if context is None:
            context = {}
        res = super(ExportYaml, self).default_get(cr, uid, fields_list, context=context)

        try:
            import yaml
        except ImportError:
            raise osv.except_osv(_('Error'), _('Python Yaml Module not found, see description module'))

        doc_id = context.get('active_id')
        doc_obj = self.pool.get('document.import.list')
        doc = doc_obj.browse(cr, uid, doc_id, context=context)

        yml_file = '%s.yml' % doc.name.lower().replace(' ', '_').replace('-', '')
        content = {
            'version': '1.3',
            'name': doc.name,
            'object': doc.model_id.model,
            'context': doc.ctx,
            'separator': doc.csv_sep,
            'escape': doc.csv_esc,
            'encoding': doc.encoding,
            'key_field_name': doc.key_field_name,
            'reject_all': doc.err_reject,
            'log_filename': doc.log_filename,
            'reject_filename': doc.reject_filename,
            'backup_filename': doc.backup_filename,
            'lang': doc.lang_id.code or 'en_US',
            'notes': doc.notes or '',
            'send_mail': doc.err_mail,
            'mail_from': doc.mail_from,
            'mail_cc': doc.mail_cc,
            'mail_subject': doc.mail_subject,
            'mail_body': doc.mail_body,
            'mail_cc_err': doc.mail_cc_err,
            'mail_subject_err': doc.mail_subject_err,
            'mail_body_err': doc.mail_body_err,
        }
        lines = []
        for l in doc.line_ids:
            line = {}
            line['name'] = l.name
            line['field'] = l.field_id.name
            if l.field_id.ttype in ('many2one', 'one2many', 'many2many'):
                line['model'] = l.model_relation_id.model and str(l.model_relation_id.model) or False
                line['model_field'] = l.field_relation_id.name and str(l.field_relation_id.name) or False
                line['relation'] = l.relation and str(l.relation) or False
            line['refkey'] = l.refkey
            lines.append(line)

        content['lines'] = lines
        buf = StringIO()
        buf.write(yaml.dump(content, encoding='utf-8', default_flow_style=False))
        out = base64.encodestring(buf.getvalue())
        buf.close()
        res.update({'filename': out, 'name': yml_file})
        return res

ExportYaml()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
