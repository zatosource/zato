# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Django
from django.http import HttpResponse, HttpResponseServerError
from django.template.response import TemplateResponse

# Zato
from zato.admin.web.forms import ChangePasswordForm, SearchForm
from zato.admin.web.forms.kvdb import CreateForm, EditForm, RemoteCommandForm
from zato.admin.web.views import change_password as _change_password, CreateEdit, Index as _Index, method_allowed
from zato.common.exception import ZatoException
from zato.common.json_internal import dumps
from zato.common.model.kvdb import KVDB as KVDBModel

# ################################################################################################################################
# ################################################################################################################################

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'kvdb'
    template = 'zato/outgoing/redis/index.html'
    service_name = 'zato.outgoing.redis.get-list'
    output_class = KVDBModel
    paginate = True

    class SimpleIO(_Index.SimpleIO):
        input_required = 'cluster_id',
        output_required = 'name', 'is_active', 'host', 'port', 'db', 'use_redis_sentinels', 'redis_sentinels', \
            'redis_sentinels_master'
        output_optional = 'id',
        output_repeated = True

    def handle(self):
        return {
            'create_form': CreateForm(),
            'edit_form': EditForm(prefix='edit'),
            'change_password_form': ChangePasswordForm(),
            'cluster_id': self.input.cluster_id,
        }

# ################################################################################################################################

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    class SimpleIO(CreateEdit.SimpleIO):
        input_optional = 'id', 'name', 'is_active', 'host', 'port', 'db', 'use_redis_sentinels', 'redis_sentinels', \
            'redis_sentinels_master'

    def post_process_return_data(self, return_data):
        return_data['id'] = self.input_dict['id']
        return return_data

    def success_message(self, item):
        return 'Outgoing Redis connection {} successfully'.format(self.verb)

# ################################################################################################################################

class Create(_CreateEdit):
    url_name = 'out-redis-create'
    service_name = 'kvdb1.create'

# ################################################################################################################################

class Edit(_CreateEdit):
    url_name = 'out-redis-edit'
    form_prefix = 'edit-'
    service_name = 'zato.outgoing.redis.edit'

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def change_password(req):
    return _change_password(req, 'zato.outgoing.redis.change-password')

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def remote_command(req):

    return_data = {
        'form':RemoteCommandForm(),
        'cluster':req.zato.get('cluster'),
        'search_form':SearchForm(req.zato.clusters, req.GET),
        'zato_clusters':req.zato.clusters,
        'cluster_id':req.zato.cluster_id,
    }

    return TemplateResponse(req, 'zato/kvdb/remote-command.html', return_data)

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def remote_command_execute(req):
    """ Executes a command against the key/value DB.
    """
    try:
        response = req.zato.client.invoke('zato.kvdb.remote-command.execute', {'command': req.POST['command']})
        if response.has_data:
            return HttpResponse(dumps({'message': dumps(response.data.result)}), content_type='application/javascript')
        else:
            raise ZatoException(msg=response.details)
    except Exception as e:
        return HttpResponseServerError(e.args[0])

# ################################################################################################################################
# ################################################################################################################################
