# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Django
from django.http import HttpResponseServerError, JsonResponse

# Zato
from zato.admin.web.forms.outgoing.as4 import CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, id_only_service, Index as _Index, method_allowed
from zato.common.api import AS4, CONNECTION, URL_TYPE
from zato.common.util.xml_.keystore import load_certificates_pem

# ################################################################################################################################
# ################################################################################################################################

_as4_field_names = AS4.Common_Fields + AS4.Outgoing_Fields

# ################################################################################################################################
# ################################################################################################################################

def get_cert_expiry(signing_cert_chain:'str') -> 'str':
    """ Returns the not-after date of the first certificate in a pasted PEM chain,
    or an empty string when there is nothing to parse.
    """
    if not signing_cert_chain:
        return ''

    try:
        certificates = load_certificates_pem(signing_cert_chain.encode('utf8'))
    except Exception:
        return ''

    not_after = certificates[0].not_valid_after_utc
    out = not_after.strftime('%Y-%m-%d')
    return out

# ################################################################################################################################
# ################################################################################################################################

class OutgoingAS4ConfigObject:
    """ A config object for outgoing AS4 connections, filled in with attributes from the get-list response.
    """

# ################################################################################################################################
# ################################################################################################################################

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'out-as4'
    template = 'zato/outgoing/as4.html'
    service_name = 'zato.http-soap.get-list'
    output_class = OutgoingAS4ConfigObject
    paginate = True

    def get_initial_input(self):

        return {
            'connection': CONNECTION.OUTGOING,
            'transport': URL_TYPE.AS4,
        }

    input_required = 'cluster_id',
    output_required = 'id', 'name', 'is_active', 'is_internal'
    output_optional = ('host', 'url_path', 'validate_tls', 'timeout') + _as4_field_names
    output_repeated = True

# ################################################################################################################################

    def on_before_append_item(self, item):

        # The expiry of the pasted signing certificate is computed for display only.
        signing_cert_chain = getattr(item, 'as4_signing_cert_chain', '')
        item.as4_cert_expiry = get_cert_expiry(signing_cert_chain)

        return item

# ################################################################################################################################

    def handle(self):
        return {
            'show_search_form': True,
            'create_form': CreateForm(req=self.req),
            'edit_form': EditForm(prefix='edit', req=self.req),
        }

# ################################################################################################################################
# ################################################################################################################################

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    input_required = 'name', 'host'
    input_optional = ('is_active', 'url_path', 'validate_tls', 'timeout') + _as4_field_names
    output_required = 'id', 'name'

# ################################################################################################################################

    def populate_initial_input_dict(self, initial_input_dict):
        initial_input_dict['connection'] = CONNECTION.OUTGOING
        initial_input_dict['transport'] = URL_TYPE.AS4
        initial_input_dict['is_internal'] = False

# ################################################################################################################################

    def pre_process_input_dict(self, input_dict):

        if not input_dict.get('url_path'):
            input_dict['url_path'] = '/'

        # Checkboxes arrive as 'on' or not at all - the backend expects real booleans.
        input_dict['as4_use_discovery'] = bool(input_dict.get('as4_use_discovery'))

# ################################################################################################################################

    def success_message(self, item):
        return 'Successfully {} outgoing AS4 connection `{}`'.format(self.verb, item.name)

# ################################################################################################################################
# ################################################################################################################################

class Create(_CreateEdit):
    url_name = 'out-as4-create'
    service_name = 'zato.http-soap.create'

# ################################################################################################################################
# ################################################################################################################################

class Edit(_CreateEdit):
    url_name = 'out-as4-edit'
    form_prefix = 'edit-'
    service_name = 'zato.http-soap.edit'

# ################################################################################################################################
# ################################################################################################################################

class Delete(_Delete):
    url_name = 'out-as4-delete'
    error_message = 'Could not delete outgoing AS4 connection'
    service_name = 'zato.http-soap.delete'

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def ping(req, id, cluster_id): # type: ignore
    response = id_only_service(req, 'zato.http-soap.ping', id, 'Could not ping the connection, e:`{}`')

    if isinstance(response, HttpResponseServerError):
        err = response.content.decode('utf-8', 'replace')
        return JsonResponse({
            'is_success': False,
            'info': err,
        })

    data = response.data
    return JsonResponse({
        'is_success': data.is_success,
        'info': data.info,
    })

# ################################################################################################################################
# ################################################################################################################################
