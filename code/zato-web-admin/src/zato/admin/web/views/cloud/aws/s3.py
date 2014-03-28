# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging

# Zato
from zato.admin.web.forms.cloud.aws.s3 import CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index
from zato.common.odb.model import AWSS3

logger = logging.getLogger(__name__)

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'cloud-aws-s3'
    template = 'zato/cloud/aws/s3.html'
    service_name = 'zato.cloud.aws.s3.get-list'
    output_class = AWSS3

    class SimpleIO(_Index.SimpleIO):
        input_required = ('cluster_id',)
        output_required = ('id', 'name', 'is_active', 'pool_size', 'address', 'debug_level', 'suppr_cons_slashes',
            'content_type', 'sec_def_id')
        output_optional = ('metadata_',)
        output_repeated = True

    def handle(self):
        return {
            'create_form': CreateForm(),
            'edit_form': EditForm(prefix='edit'),
        }

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    class SimpleIO(CreateEdit.SimpleIO):
        input_required = ('cluster_id', 'name', 'is_active', 'pool_size', 'address', 'debug_level', 'suppr_cons_slashes',
            'content_type', 'sec_def_id')
        output_required = ('id', 'name')

    def success_message(self, item):
        return 'Successfully {0} the AWS S3 connection [{1}]'.format(self.verb, item.name)

class Create(_CreateEdit):
    url_name = 'cloud-aws-s3-create'
    service_name = 'zato.cloud.aws.s3.create'

class Edit(_CreateEdit):
    url_name = 'cloud-aws-s3-edit'
    form_prefix = 'edit-'
    service_name = 'zato.cloud.aws.s3.edit'

class Delete(_Delete):
    url_name = 'cloud-aws-s3-delete'
    error_message = 'Could not delete the AWS S3 connection'
    service_name = 'zato.cloud.aws.s3.delete'
