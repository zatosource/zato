# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Zato
from zato.admin.web.forms.kvdb.data_dict.dictionary import CreateForm, EditForm
from zato.admin.web.views import CreateEdit, Delete as _Delete, Index as _Index

class DictItem:
    pass

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'kvdb-data-dict-dictionary'
    template = 'zato/kvdb/data_dict/dictionary.html'
    service_name = 'zato.kvdb.data-dict.dictionary.get-list'
    output_class = DictItem

    class SimpleIO(_Index.SimpleIO):
        output_required = ('id', 'system', 'key', 'value')
        output_repeated = True

    def handle(self):
        return {
            'create_form': CreateForm(),
            'edit_form': EditForm(prefix='edit'),
        }

class _CreateEdit(CreateEdit):
    method_allowed = 'POST'

    class SimpleIO(CreateEdit.SimpleIO):
        input_required = ('system', 'key', 'value')
        output_required = ('id',)

    def success_message(self, item):
        return 'Successfully {} the dictionary entry system:[{}], key:[{}], value:[{}]'.format(
            self.verb, self.input_dict['system'], self.input_dict['key'], self.input_dict['value'])

class Create(_CreateEdit):
    url_name = 'kvdb-data-dict-dictionary-create'
    service_name = 'zato.kvdb.data-dict.dictionary.create'

class Edit(_CreateEdit):
    url_name = 'kvdb-data-dict-dictionary-edit'
    form_prefix = 'edit-'
    service_name = 'zato.kvdb.data-dict.dictionary.edit'

class Delete(_Delete):
    url_name = 'kvdb-data-dict-dictionary-delete'
    error_message = 'Could not delete the data dictionary'
    service_name = 'zato.kvdb.data-dict.dictionary.delete'
