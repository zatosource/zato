# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Zato
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index

# ################################################################################################################################

class ConfigFile:
    def __init__(self):
        self.id = None
        self.name = None
        self.type = None
        self.data = None
        self.size = None
        self.size_pretty = None
        self.last_modified = None
        self.last_modified_utc = None

# ################################################################################################################################

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'config-file'
    template = 'zato/config_file/index.html'
    service_name = 'config-file.get-list'
    output_class = ConfigFile
    paginate = True

    class SimpleIO(_Index.SimpleIO):
        input_required = ('cluster_id',)
        output_required = ('id', 'name', 'type', 'size', 'size_pretty')
        output_repeated = True

    def handle(self):
        return {}

# ################################################################################################################################

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    class SimpleIO(CreateEdit.SimpleIO):
        input_required = ('id', 'name', 'type', 'data')

    def success_message(self, ignored_item):
        return 'File saved succesfully'

# ################################################################################################################################

class Create(_CreateEdit):
    url_name = 'config-file-create'
    service_name = 'config-file.create'

# ################################################################################################################################

class Edit(_CreateEdit):
    url_name = 'config-file-edit'
    form_prefix = 'edit-'
    service_name = 'config-file.edit'

# ################################################################################################################################

class Delete(_Delete):
    url_name = 'config-file-delete'
    error_message = 'File could not be deleted'
    service_name = 'config-file.delete'

# ################################################################################################################################
