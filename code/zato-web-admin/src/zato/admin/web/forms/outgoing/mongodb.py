# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Django
from django import forms

# Zato
from zato.admin.web.forms import add_select, WithTLSForm
from zato.common.api import MONGODB

default = MONGODB.DEFAULT
timeout = default.TIMEOUT

class CreateForm(WithTLSForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))

    username = forms.CharField(widget=forms.TextInput(attrs={'style':'width:20%'}))
    app_name = forms.CharField(widget=forms.TextInput(attrs={'style':'width:30%'}))
    replica_set = forms.CharField(widget=forms.TextInput(attrs={'style':'width:20%'}))

    auth_source = forms.CharField(widget=forms.TextInput(attrs={'style':'width:15%'}), initial=default.AUTH_SOURCE)
    auth_mechanism = forms.ChoiceField(widget=forms.Select(), initial=MONGODB.AUTH_MECHANISM.SCRAM_SHA_1.id)

    pool_size_max = forms.CharField(widget=forms.TextInput(attrs={'style':'width:9%'}), initial=default.POOL_SIZE_MAX)

    connect_timeout = forms.CharField(widget=forms.TextInput(attrs={'style':'width:9%'}), initial=timeout.CONNECT)
    socket_timeout = forms.CharField(widget=forms.TextInput(attrs={'style':'width:9%'}), initial=timeout.SOCKET)
    server_select_timeout = forms.CharField(widget=forms.TextInput(attrs={'style':'width:9%'}), initial=timeout.SERVER_SELECT)
    wait_queue_timeout = forms.CharField(widget=forms.TextInput(attrs={'style':'width:9%'}), initial=timeout.WAIT_QUEUE)

    max_idle_time = forms.CharField(widget=forms.TextInput(attrs={'style':'width:9%'}), initial=default.MAX_IDLE_TIME)
    hb_frequency = forms.CharField(widget=forms.TextInput(attrs={'style':'width:8%'}), initial=default.HB_FREQUENCY)

    is_tz_aware = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    document_class = forms.CharField(widget=forms.TextInput(attrs={'style':'width:40%'}))

    compressor_list = forms.CharField(widget=forms.TextInput(attrs={'style':'width:30%'}))
    zlib_level = forms.CharField(widget=forms.TextInput(attrs={'style':'width:9%'}), initial=default.ZLIB_LEVEL)

    write_to_replica = forms.CharField(widget=forms.TextInput(attrs={'style':'width:9%'}), initial=default.WRITE_TO_REPLICA)
    write_timeout = forms.CharField(widget=forms.TextInput(attrs={'style':'width:9%'}), initial=default.WRITE_TIMEOUT)
    is_write_journal_enabled = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    is_write_fsync_enabled = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    should_retry_write = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))

    read_pref_type = forms.ChoiceField(widget=forms.Select(), initial=MONGODB.READ_PREF.PRIMARY.id)
    read_pref_tag_list = forms.CharField(widget=forms.TextInput(attrs={'style':'width:23%'}))
    read_pref_max_stale = forms.CharField(widget=forms.TextInput(attrs={'style':'width:9%'}), initial=default.MAX_STALENESS)

    server_list = forms.CharField(widget=forms.Textarea(attrs={'style':'width:100%; height:70px'}), initial=default.SERVER_LIST)

    def __init__(self, *args, **kwargs):
        super(CreateForm, self).__init__(*args, **kwargs)
        add_select(self, 'auth_mechanism', MONGODB.AUTH_MECHANISM(), needs_initial_select=False)
        add_select(self, 'read_pref_type', MONGODB.READ_PREF(), needs_initial_select=False)

class EditForm(CreateForm):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    tls_match_hostname = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    should_retry_write = forms.BooleanField(required=False, widget=forms.CheckboxInput())
