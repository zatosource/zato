# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging

# Zato
from zato.admin.web.forms.channel.ftp import CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index
from zato.common.model import FTPChannel

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'channel-ftp'
    template = 'zato/channel/ftp/index.html'
    service_name = 'channel.ftp.get-list'
    output_class = FTPChannel
    paginate = True

    class SimpleIO(_Index.SimpleIO):
        input_required = 'cluster_id',
        output_required = 'id', 'name', 'is_active', 'max_connections', 'max_conn_per_ip', 'command_timeout', \
           'banner', 'log_prefix', 'base_directory', 'read_throttle', 'write_throttle', 'masq_address', \
           'passive_ports', 'log_level', 'service_name', 'srv_invoke_mode'
        output_repeated = True

    def handle(self):
        return {
            'create_form': CreateForm(req=self.req),
            'edit_form': EditForm(prefix='edit', req=self.req),
        }

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    class SimpleIO(CreateEdit.SimpleIO):
        input_required = 'name',  'is_active',  'max_connections',  'max_conn_per_ip',  'command_timeout', \
            'banner',  'log_prefix',  'base_directory',  'read_throttle',  'write_throttle',  'masq_address', \
            'passive_ports',  'log_level',  'service_name', 'srv_invoke_mode'
        output_required = 'id', 'name'

    def success_message(self, item):
        return 'FTP channel `{}` successfully {}'.format(item.name, self.verb)

class Create(_CreateEdit):
    url_name = 'channel-ftp-create'
    service_name = 'channel.ftp.create'

class Edit(_CreateEdit):
    url_name = 'channel-ftp-edit'
    form_prefix = 'edit-'
    service_name = 'channel.ftp.edit'

class Delete(_Delete):
    url_name = 'channel-ftp-delete'
    error_message = 'FTP channel could not be deleted'
    service_name = 'channel.ftp.delete'

'''
# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Zato
from zato.server.service import Int, Service

class GetList(Service):
    name = 'channel.ftp.get-list'

    class SimpleIO:
        input_required = 'cluster_id',
        output_required = 'id',  'name',  'is_active',  Int('max_connections'),  Int('max_conn_per_ip'),  \
            Int('command_timeout'), 'banner',  'log_prefix',  'base_directory',  'read_throttle',  'write_throttle', \
            'masq_address', 'passive_ports', 'log_level',  'service_name', 'srv_invoke_mode'
        output_repeated = True

    def handle(self):
        pass
'''
