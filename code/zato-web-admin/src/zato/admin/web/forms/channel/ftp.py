# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Django
from django import forms

# Zato
from zato.admin.web.forms import add_services, add_topics
from zato.common import FTP

_default = FTP.CHANNEL.DEFAULT

class CreateForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    address = forms.CharField(widget=forms.TextInput(attrs={'style':'width:22%'}), initial=_default.ADDRESS)

    service_name = forms.ChoiceField(widget=forms.Select(attrs={'style':'width:100%'}))
    topic_name = forms.ChoiceField(widget=forms.Select(attrs={'style':'width:100%'}))

    max_connections = forms.CharField(widget=forms.TextInput(attrs={'style':'width:20%'}), initial=_default.MAX_CONN)
    max_conn_per_ip = forms.CharField(widget=forms.TextInput(attrs={'style':'width:20%'}), initial=_default.MAX_CONN_PER_IP)
    command_timeout = forms.CharField(widget=forms.TextInput(attrs={'style':'width:10%'}), initial=_default.COMMAND_TIMEOUT)

    banner = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}), initial=_default.BANNER)
    log_prefix = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}), initial=_default.LOG_PREFIX)
    base_directory = forms.CharField(widget=forms.TextInput(attrs={'style':'width:46%'}), initial=_default.BASE_DIRECTORY)

    read_throttle = forms.CharField(widget=forms.TextInput(attrs={'style':'width:20%'}), initial=_default.THROTTLE_READ)
    write_throttle = forms.CharField(widget=forms.TextInput(attrs={'style':'width:20%'}), initial=_default.THROTTLE_WRITE)

    log_level = forms.ChoiceField(widget=forms.Select(attrs={'style':'width:10%'}), initial=FTP.CHANNEL.LOG_LEVEL.INFO.id)
    srv_invoke_mode = forms.HiddenInput()

    def __init__(self, prefix=None, post_data=None, req=None):
        super(CreateForm, self).__init__(post_data, prefix=prefix)

        add_services(self, req)
        add_topics(self, req, by_id=False)

        '''
        self._add_field('socket_type', ZMQ.CHANNEL)
        self._add_field('socket_method', ZMQ.METHOD)
        self._add_field('pool_strategy', ZMQ.POOL_STRATEGY)
        self._add_field('service_source', ZMQ.SERVICE_SOURCE)

        add_services(self, req)

    def _add_field(self, field_name, source):
        self.fields[field_name].choices = []
        for code, name in source.items():
            self.fields[field_name].choices.append([code, name])
    '''

class EditForm(CreateForm):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())
