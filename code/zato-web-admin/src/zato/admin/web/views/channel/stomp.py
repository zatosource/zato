# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging

# Django
from django.http import HttpResponse, HttpResponseServerError

# Zato
from zato.admin.web.forms import ChangePasswordForm
from zato.admin.web.forms.channel.stomp import CreateForm, EditForm
from zato.admin.web.views import change_password as _change_password, CreateEdit, Delete as _Delete, id_only_service, \
     Index as _Index, method_allowed
from zato.common.odb.model import ChannelSTOMP

logger = logging.getLogger(__name__)

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'channel-stomp'
    template = 'zato/channel/stomp.html'
    service_name = 'zato.channel.stomp.get-list'
    output_class = ChannelSTOMP
    paginate = True

    class SimpleIO(_Index.SimpleIO):
        input_required = ('cluster_id',)
        output_required = ('id', 'name', 'is_active', 'address', 'username',
            'proto_version', 'timeout', 'sub_to', 'service_id', 'service_name')
        output_repeated = True

    def handle(self):
        return {
            'change_password_form': ChangePasswordForm(),
            'create_form': CreateForm(),
            'edit_form': EditForm(prefix='edit'),
        }

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    class SimpleIO(CreateEdit.SimpleIO):
        input_required = ('name', 'is_active', 'address', 'username',
            'proto_version', 'timeout', 'sub_to', 'service_id', 'service_name')
        output_required = ('id',)

    def success_message(self, item):
        return 'Successfully {0} the channel STOMP connection [{1}]'.format(self.verb, item.name)

class Create(_CreateEdit):
    url_name = 'channel-stomp-create'
    service_name = 'zato.channel.stomp.create'

class Edit(_CreateEdit):
    url_name = 'channel-stomp-edit'
    form_prefix = 'edit-'
    service_name = 'zato.channel.stomp.edit'

class Delete(_Delete):
    url_name = 'channel-stomp-delete'
    error_message = 'Could not delete the channel STOMP connection'
    service_name = 'zato.channel.stomp.delete'

@method_allowed('POST')
def change_password(req):
    return _change_password(req, 'zato.channel.stomp.change-password')

@method_allowed('POST')
def ping(req, id, cluster_id):
    ret = id_only_service(req, 'zato.channel.stomp.ping', id, 'Could not ping the STOMP connection, e:`{}`')
    if isinstance(ret, HttpResponseServerError):
        return ret
    return HttpResponse(ret.data.info)
