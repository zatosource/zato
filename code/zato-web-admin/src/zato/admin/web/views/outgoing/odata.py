# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.admin.web.forms import ChangePasswordForm
from zato.admin.web.forms.outgoing.odata import CreateForm, EditForm
from zato.admin.web.views import change_password as _change_password, CreateEdit, Delete as _Delete, Index as _Index, \
     method_allowed, ping_connection
from zato.common.api import ODATA_Subtype

# Bunch
from zato.common.ext.bunch import Bunch

# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################

class Index(_Index):
    """ One index view serves every subtype of the OData implementation - urls.py mounts it once per subtype,
    e.g. as the OData page and as the SAP page.
    """
    method_allowed = 'GET'
    template = 'zato/outgoing/odata.html'
    service_name = 'zato.generic.connection.get-list'
    output_class = Bunch
    paginate = True

    input_required = 'cluster_id', 'type_'
    output_required = 'id', 'name', 'is_active', 'address', 'odata_version', 'auth_type'
    output_optional = ('username', 'token_url', 'tenant_id', 'client_id', 'scopes', 'needs_csrf_token', 'page_size',
        'timeout', 'pool_size')
    output_repeated = True

    def __init__(self, subtype:'str') -> 'None':
        super().__init__()
        self.subtype = ODATA_Subtype[subtype]
        self.url_name = self.subtype['url_prefix']

    def handle(self):

        # The defaults the create form opens with are per-subtype,
        # e.g. SAP connections start with OData 2.0 and CSRF tokens enabled.
        form_initial = {
            'odata_version': self.subtype['odata_version'],
            'needs_csrf_token': self.subtype['needs_csrf_token'],
        }

        # The url names the template's forms post to
        url_prefix = self.subtype['url_prefix']

        return {
            'show_search_form': True,
            'create_form': CreateForm(initial=form_initial),
            'edit_form': EditForm(prefix='edit'),
            'change_password_form': ChangePasswordForm(),
            'subtype': self.subtype,
            'create_url': f'{url_prefix}-create',
            'edit_url': f'{url_prefix}-edit',
            'change_password_url': f'{url_prefix}-change-password',
        }

# ################################################################################################################################

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    input_required = 'name', 'address', 'odata_version', 'auth_type'
    input_optional = ('is_active', 'username', 'token_url', 'tenant_id', 'client_id', 'scopes', 'needs_csrf_token',
        'page_size', 'timeout', 'pool_size')
    output_required = 'id', 'name'

    def __init__(self, subtype:'str') -> 'None':
        super().__init__()
        self.subtype = ODATA_Subtype[subtype]
        self.url_name = '{}-{}'.format(self.subtype['url_prefix'], self.action)

    def populate_initial_input_dict(self, initial_input_dict):
        initial_input_dict['type_'] = self.subtype['type_']
        initial_input_dict['is_internal'] = False
        initial_input_dict['is_channel'] = False
        initial_input_dict['is_outconn'] = True

    def success_message(self, item):
        label = self.subtype['label']
        return 'Successfully {} outgoing {} connection `{}`'.format(self.verb, label, item.name)

# ################################################################################################################################

class Create(_CreateEdit):
    action = 'create'
    service_name = 'zato.generic.connection.create'

# ################################################################################################################################

class Edit(_CreateEdit):
    action = 'edit'
    form_prefix = 'edit-'
    service_name = 'zato.generic.connection.edit'

# ################################################################################################################################

class Delete(_Delete):
    service_name = 'zato.generic.connection.delete'

    def __init__(self, subtype:'str') -> 'None':
        super().__init__()
        self.subtype = ODATA_Subtype[subtype]
        self.url_name = '{}-delete'.format(self.subtype['url_prefix'])
        self.error_message = 'Could not delete outgoing {} connection'.format(self.subtype['label'])

# ################################################################################################################################

@method_allowed('POST')
def change_password(req):
    return _change_password(req, 'zato.generic.connection.change-password')

# ################################################################################################################################

@method_allowed('POST')
def ping(req, id, cluster_id, subtype):
    label = ODATA_Subtype[subtype]['label']
    return ping_connection(req, 'zato.generic.connection.ping', id, '{} connection'.format(label))

# ################################################################################################################################
