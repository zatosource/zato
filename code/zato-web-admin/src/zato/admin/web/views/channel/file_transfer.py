# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Zato
from zato.admin.web.forms.channel.file_transfer import CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index
from zato.common.api import GENERIC
from zato.common.json_internal import dumps
from zato.common.model import FileTransferChannel

# ################################################################################################################################
# ################################################################################################################################

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'channel-file-transfer'
    template = 'zato/channel/file-transfer.html'
    service_name = 'zato.generic.connection.get-list'
    output_class = FileTransferChannel
    paginate = True

    class SimpleIO(_Index.SimpleIO):
        input_required = 'cluster_id', 'type_'
        output_required = 'id', 'name', 'is_active', 'source_type', 'pickup_from'
        output_optional = 'service_list', 'topic_list', 'move_processed_to', 'file_patterns', 'parse_with', 'should_read_on_pickup', \
            'should_parse_on_pickup', 'should_delete_after_pickup', 'ftp_source_id', 'sftp_source_id', 'scheduler_job_id', \
            'ftp_source_name', 'sftp_source_name', 'is_case_sensitive', 'is_line_by_line', 'is_hot_deploy', \
            'binary_file_patterns', 'data_encoding'
        output_repeated = True

# ################################################################################################################################

    def handle(self):
        return {
            'create_form': CreateForm(req=self.req),
            'edit_form': EditForm(prefix='edit', req=self.req),
        }

# ################################################################################################################################

    def on_before_append_item(self, item):
        # type: (FileTransferChannel) -> FileTransferChannel

        if item.service_list:
            item.service_list = item.service_list if isinstance(item.service_list, list) else [item.service_list]
            item.service_list = sorted(item.service_list)
            item.service_list_json = dumps(item.service_list)

        if item.topic_list:
            item.topic_list = item.topic_list if isinstance(item.topic_list, list) else [item.topic_list]
            item.topic_list = sorted(item.topic_list)
            item.topic_list_json = dumps(item.topic_list)

        return item

# ################################################################################################################################
# ################################################################################################################################

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    class SimpleIO(CreateEdit.SimpleIO):
        input_required = 'name', 'is_active', 'source_type', 'pickup_from'
        input_optional = 'service_list', 'topic_list', 'move_processed_to', 'file_patterns', 'parse_with', 'should_read_on_pickup', \
            'should_parse_on_pickup', 'should_delete_after_pickup', 'ftp_source_id', 'sftp_source_id', 'scheduler_job_id', \
            'is_case_sensitive', 'is_line_by_line', 'is_hot_deploy', 'binary_file_patterns', 'data_encoding'
        output_required = 'id', 'name'

    def populate_initial_input_dict(self, initial_input_dict):
        initial_input_dict['type_'] = GENERIC.CONNECTION.TYPE.CHANNEL_FILE_TRANSFER
        initial_input_dict['is_internal'] = False
        initial_input_dict['is_channel'] = True
        initial_input_dict['is_outconn'] = False
        initial_input_dict['sec_use_rbac'] = False
        initial_input_dict['pool_size'] = 1

    def pre_process_item(self, name, value):
        if name in ('service_list', 'topic_list'):
            if value:
                if isinstance(value, list):
                    value = sorted(set(elem for elem in value if elem))
                else:
                    value = [value] if value else []
        return value

    def post_process_return_data(self, return_data):

        service_list_json = []
        topic_list_json   = []

        service_list_html = ''
        topic_list_html   = ''

        cluster_id = self.input_dict['cluster_id']
        service_list = sorted(self.input_dict['service_list'] or [])
        topic_list = sorted(self.input_dict['topic_list'] or [])

        for service_name in service_list:

            if not service_name:
                continue

            # The raw list of services, to be read by JavaScript
            service_list_json.append(service_name)

            # The list of services as HTML
            service_list_html += """
            <span class="form_hint">S</span>→
                <a href="/zato/service/overview/{service_name}/?cluster={cluster_id}">{service_name}</a>
            <br/>
            """.format(**{
                'service_name': service_name,
                'cluster_id': cluster_id
            })

        for topic_name in topic_list:

            if not topic_name:
                continue

            # The raw list of services, to be read by JavaScript
            topic_list_json.append(topic_name)

            # The list of topics as HTML
            topic_list_html += """
            <span class="form_hint">T</span>→
                <a href="/zato/pubsub/topic/?cluster={cluster_id}&amp;query={topic_name}">{topic_name}</a>
            <br/>
            """.format(**{
                'topic_name': topic_name,
                'cluster_id': cluster_id
            })

        return_data['recipients_html'] = service_list_html + topic_list_html
        return_data['service_list_json'] = service_list_json
        return_data['topic_list_json'] = topic_list_json

    def success_message(self, item):
        return 'Successfully {} file transfer channel `{}`'.format(self.verb, item.name)

# ################################################################################################################################
# ################################################################################################################################

class Create(_CreateEdit):
    url_name = 'channel-file-transfer-create'
    service_name = 'zato.generic.connection.create'

# ################################################################################################################################
# ################################################################################################################################

class Edit(_CreateEdit):
    url_name = 'channel-file-transfer-edit'
    form_prefix = 'edit-'
    service_name = 'zato.generic.connection.edit'

# ################################################################################################################################
# ################################################################################################################################

class Delete(_Delete):
    url_name = 'channel-file-transfer-delete'
    error_message = 'Could not delete file transfer channel'
    service_name = 'zato.generic.connection.delete'

# ################################################################################################################################
# ################################################################################################################################
