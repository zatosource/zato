# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging

# Zato
from zato.admin.web.forms.cloud.aws.s3 import CreateForm, EditForm
from zato.admin.web.views import get_security_id_from_select, CreateEdit, Delete as _Delete, Index as _Index, SecurityList
from zato.common.odb.model import AWSS3

logger = logging.getLogger(__name__)

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'cloud-aws-s3'
    template = 'zato/cloud/aws/s3.html'
    service_name = 'zato.cloud.aws.s3.get-list'
    output_class = AWSS3
    paginate = True

    class SimpleIO(_Index.SimpleIO):
        input_required = ('cluster_id',)
        output_required = ('id', 'name', 'is_active', 'pool_size', 'address', 'debug_level', 'suppr_cons_slashes',
            'content_type', 'security_id', 'encrypt_at_rest', 'storage_class')
        output_optional = ('metadata_', 'bucket')
        output_repeated = True

    def handle(self):
        if self.req.zato.cluster_id:
            sec_list = SecurityList.from_service(self.req.zato.client, self.req.zato.cluster.id, ['aws'])
        else:
            sec_list = []

        return {
            'create_form': CreateForm(sec_list),
            'edit_form': EditForm(sec_list, prefix='edit'),
        }

# ################################################################################################################################
# ################################################################################################################################

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    class SimpleIO(CreateEdit.SimpleIO):
        input_required = ('cluster_id', 'name', 'is_active', 'pool_size', 'address', 'debug_level', 'suppr_cons_slashes',
            'content_type', 'security_id', 'encrypt_at_rest', 'storage_class')
        input_optional = ('metadata_', 'bucket')
        output_required = ('id', 'name')

    def on_after_set_input(self):
        self.input_dict['security_id'] = get_security_id_from_select(self.input, '', 'security_id')

    def success_message(self, item):
        return 'AWS S3 connection `{}` {} successfully'.format(item.name, self.verb)

# ################################################################################################################################
# ################################################################################################################################

class Create(_CreateEdit):
    url_name = 'cloud-aws-s3-create'
    service_name = 'zato.cloud.aws.s3.create'

# ################################################################################################################################
# ################################################################################################################################

class Edit(_CreateEdit):
    url_name = 'cloud-aws-s3-edit'
    form_prefix = 'edit-'
    service_name = 'zato.cloud.aws.s3.edit'

# ################################################################################################################################
# ################################################################################################################################

class Delete(_Delete):
    url_name = 'cloud-aws-s3-delete'
    error_message = 'AWS S3 connection could not be deleted'
    service_name = 'zato.cloud.aws.s3.delete'

# ################################################################################################################################
# ################################################################################################################################
