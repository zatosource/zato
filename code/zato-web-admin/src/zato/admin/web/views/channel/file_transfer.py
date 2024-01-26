# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Zato
from zato.admin.web.forms.channel.file_transfer import CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, get_outconn_rest_list, Index as _Index
from zato.common.api import FILE_TRANSFER, GENERIC
from zato.common.json_internal import dumps
from zato.common.model.file_transfer import FileTransferChannel

# ################################################################################################################################
# ################################################################################################################################

source_type_ftp   = FILE_TRANSFER.SOURCE_TYPE.FTP.id
source_type_local = FILE_TRANSFER.SOURCE_TYPE.LOCAL.id
source_type_sftp  = FILE_TRANSFER.SOURCE_TYPE.SFTP.id

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
        output_required = 'id', 'name', 'is_active', 'source_type', 'pickup_from_list'
        output_optional = 'service_list', 'topic_list', 'move_processed_to', 'file_patterns', 'parse_with', \
            'should_read_on_pickup', 'should_parse_on_pickup', 'should_delete_after_pickup', 'ftp_source_id', 'sftp_source_id', \
            'scheduler_job_id', 'ftp_source_name', 'sftp_source_name', 'is_case_sensitive', 'is_line_by_line', 'is_hot_deploy', \
            'binary_file_patterns', 'data_encoding', 'outconn_rest_list'
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

        if item.outconn_rest_list:

            # All REST outgoing connections for the cluster
            all_outconn_rest_list = get_outconn_rest_list(self.req)

            item.outconn_rest_list = item.outconn_rest_list if isinstance(item.outconn_rest_list, list) else \
                [item.outconn_rest_list]
            item.outconn_rest_list_by_name = sorted(all_outconn_rest_list[int(elem)] for elem in item.outconn_rest_list if elem)
            item.outconn_rest_list_json = dumps(item.outconn_rest_list)

        return item

# ################################################################################################################################
# ################################################################################################################################

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    class SimpleIO(CreateEdit.SimpleIO):
        input_required = 'name', 'is_active', 'source_type', 'pickup_from_list'
        input_optional = 'service_list', 'topic_list', 'move_processed_to', 'file_patterns', 'parse_with', 'should_read_on_pickup', \
            'should_parse_on_pickup', 'should_delete_after_pickup', 'ftp_source_id', 'sftp_source_id', 'scheduler_job_id', \
            'is_case_sensitive', 'is_line_by_line', 'is_hot_deploy', 'binary_file_patterns', 'data_encoding', \
            'outconn_rest_list'
        output_required = 'id', 'name'

    def populate_initial_input_dict(self, initial_input_dict):
        initial_input_dict['type_'] = GENERIC.CONNECTION.TYPE.CHANNEL_FILE_TRANSFER
        initial_input_dict['is_internal'] = False
        initial_input_dict['is_channel'] = True
        initial_input_dict['is_outconn'] = False
        initial_input_dict['sec_use_rbac'] = False
        initial_input_dict['pool_size'] = 1

    def pre_process_item(self, name, value):
        if name in ('service_list', 'topic_list', 'outconn_rest_list'):
            if value:
                if isinstance(value, list):
                    value = sorted({elem for elem in value if elem})
                else:
                    value = [value] if value else []

        return value

    def post_process_return_data(self, return_data):

        service_list_html = ''
        topic_list_html   = ''
        outconn_rest_list_html   = ''

        cluster_id = self.input_dict['cluster_id']
        service_list = sorted(set(self.input_dict['service_list'] or []))
        topic_list = sorted(set(self.input_dict['topic_list'] or []))
        outconn_rest_list = self.input_dict['outconn_rest_list'] or []

        if outconn_rest_list:

            # All REST outgoing connections for the cluster
            all_outconn_rest_list = get_outconn_rest_list(self.req)

            outconn_rest_list = outconn_rest_list if isinstance(outconn_rest_list, list) else [outconn_rest_list]
            outconn_rest_list = sorted({all_outconn_rest_list[int(elem)] for elem in outconn_rest_list if elem})

        #
        # Services
        #

        for service_name in service_list:

            if not service_name:
                continue

            # The list of services as HTML
            service_list_html += """
            <span class="form_hint">S</span>→
                <a href="/zato/service/overview/{service_name}/?cluster={cluster_id}">{service_name}</a>
            <br/>
            """.format(**{
                'service_name': service_name,
                'cluster_id': cluster_id
            })

        #
        # Topics
        #

        for topic_name in topic_list:

            if not topic_name:
                continue

            # The list of topics as HTML
            topic_list_html += """
            <span class="form_hint">T</span>→
                <a href="/zato/pubsub/topic/?cluster={cluster_id}&amp;query={topic_name}">{topic_name}</a>
            <br/>
            """.format(**{
                'topic_name': topic_name,
                'cluster_id': cluster_id
            })

        #
        # REST
        #

        for outconn_name in outconn_rest_list:

            if not outconn_name:
                continue

            # The list of REST outconns as HTML
            outconn_rest_list_html += """
            <span class="form_hint">R</span>→
                <a href="/zato/http-soap/?cluster={cluster_id}&amp;connection=outgoing&amp;transport=plain_http&amp;query={outconn_name}">{outconn_name}</a>
            <br/>
            """.format(**{
                'outconn_name': outconn_name,
                'cluster_id': cluster_id
            })

        # Get human-readable names of the source for this channel
        if self.input.source_type == source_type_local:
            # Nothing to do in this case
            pass

        elif self.input.source_type == source_type_ftp:

            if self.input.ftp_source_id:
                response = self.req.zato.client.invoke('zato.outgoing.ftp.get-by-id', {
                    'cluster_id': cluster_id,
                    'id': self.input.ftp_source_id,
                })

                return_data['ftp_source_name'] = response.data['name']

        elif self.input.source_type == source_type_sftp:
            raise NotImplementedError()

        else:
            raise ValueError('Unknown self.input.source_type')

        #
        # Return data
        #

        return_data['recipients_html'] = service_list_html + topic_list_html + outconn_rest_list_html
        return_data['service_list'] = service_list
        return_data['topic_list'] = topic_list
        return_data['outconn_rest_list'] = outconn_rest_list

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
