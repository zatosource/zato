# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging

# Zato
from zato.admin.web.forms import ChangePasswordForm
from zato.admin.web.forms.outgoing.ftp import CreateForm, EditForm
from zato.admin.web.views import change_password as _change_password, CreateEdit, Delete as _Delete, Index as _Index, method_allowed
from zato.common.odb.model import OutgoingFTP

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'out-ftp'
    template = 'zato/outgoing/ftp.html'
    service_name = 'zato.outgoing.ftp.get-list'
    output_class = OutgoingFTP
    paginate = True

    class SimpleIO(_Index.SimpleIO):
        input_required = ('cluster_id',)
        output_required = ('id', 'name', 'is_active', 'host', 'user', 'acct', 'timeout', 'port', 'dircache', 'default_directory')
        output_repeated = True

    def handle(self):
        return {
            'create_form': CreateForm(),
            'edit_form': EditForm(prefix='edit'),
            'change_password_form': ChangePasswordForm()
        }

# ################################################################################################################################
# ################################################################################################################################

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    class SimpleIO(CreateEdit.SimpleIO):
        input_required = ('name', 'is_active', 'host', 'user', 'timeout', 'acct', 'port', 'dircache', 'default_directory')
        output_required = ('id', 'name')

    def success_message(self, item):
        return 'Outgoing FTP connection `{}` successfully {}'.format(item.name, self.verb)

# ################################################################################################################################
# ################################################################################################################################

class Create(_CreateEdit):
    url_name = 'out-ftp-create'
    service_name = 'zato.outgoing.ftp.create'

# ################################################################################################################################
# ################################################################################################################################

class Edit(_CreateEdit):
    url_name = 'out-ftp-edit'
    form_prefix = 'edit-'
    service_name = 'zato.outgoing.ftp.edit'

# ################################################################################################################################
# ################################################################################################################################

class Delete(_Delete):
    url_name = 'out-ftp-delete'
    error_message = 'Outgoing FTP connection could not be deleted'
    service_name = 'zato.outgoing.ftp.delete'

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def change_password(req):
    return _change_password(req, 'zato.outgoing.ftp.change-password')

# ################################################################################################################################
# ################################################################################################################################
