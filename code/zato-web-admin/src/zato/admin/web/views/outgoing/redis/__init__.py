# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# Django
from django.http import HttpResponse, HttpResponseServerError
from django.template.response import TemplateResponse

# Zato
from zato.admin.web.forms import SearchForm
from zato.admin.web.forms.kvdb import CreateForm, EditForm, RemoteCommandForm
from zato.admin.web.views import CreateEdit, Index as _Index, method_allowed
from zato.common.exception import ZatoException
from zato.common.json_internal import dumps
from zato.common.model.kvdb import KVDB as KVDBModel

# ################################################################################################################################
# ################################################################################################################################

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'kvdb'
    template = 'zato/outgoing/redis/index.html'
    service_name = 'kvdb1.get-list'
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
            'cluster_id': self.input.cluster_id,
        }

# ################################################################################################################################

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    class SimpleIO(CreateEdit.SimpleIO):
        input_optional = 'id', 'name', 'is_active', 'host', 'port', 'db', 'use_redis_sentinels', 'redis_sentinels', \
            'redis_sentinels_master'

    def success_message(self, item):
        return 'Outgoing Redis connection successfully {}'.format(self.verb)

# ################################################################################################################################

class Create(_CreateEdit):
    url_name = 'out-redis-create'
    service_name = 'kvdb1.create'

# ################################################################################################################################

class Edit(_CreateEdit):
    url_name = 'out-redis-edit'
    form_prefix = 'edit-'
    service_name = 'kvdb1.edit'

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def remote_command(req):

    return_data = {'form':RemoteCommandForm(),
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

'''
# -*- coding: utf-8 -*-

# Zato
from zato.common.util import get_config
from zato.server.service import AsIs, Bool, Int, Service, SIOElem
from zato.server.service.internal import AdminService

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from typing import Union as union
    from zato.server.base.parallel import ParallelServer

    ParallelServer = ParallelServer

# ################################################################################################################################
# ################################################################################################################################

class MyService(AdminService):
    name = 'kvdb1.get-list'

    class SimpleIO:
        input_optional = 'id', 'name'
        output_optional = AsIs('id'), 'is_active', 'name', 'host', Int('port'), 'db', Bool('use_redis_sentinels'), \
            'redis_sentinels', 'redis_sentinels_master'
        default_value = None

# ################################################################################################################################

    def get_data(self):

        # Response to produce
        out = []

        # For now, we only return one item containing data read from server.conf
        item = {
            'id': 'default',
            'name': 'default',
            'is_active': True,
        }

        repo_location = self.server.repo_location
        config_name   = 'server.conf'

        config = get_config(repo_location, config_name, bunchified=False)
        config = config['kvdb']

        for elem in self.SimpleIO.output_optional:

            # Extract the embedded name or use it as is
            name = elem.name if isinstance(elem, SIOElem) else elem

            # These will not exist in server.conf
            if name in ('id', 'is_active', 'name'):
                continue

            # Add it to output
            item[name] = config[name]

        # Add our only item to response
        out.append(item)

        return out

# ################################################################################################################################

    def handle(self):

        self.response.payload[:] = self.get_data()

# ################################################################################################################################
# ################################################################################################################################

class Edit(AdminService):
    name = 'kvdb1.edit'

    class SimpleIO:
        input_optional = AsIs('id'), 'name', Bool('use_redis_sentinels')
        input_required = 'host', 'port', 'db', 'redis_sentinels', 'redis_sentinels_master'
        output_optional = 'name'
        default_value = ''

    def handle(self):
        self.logger.warn('QQQ %s', self.request.input)

        self.response.payload.name = self.request.input.name

# ################################################################################################################################
# ################################################################################################################################
'''
