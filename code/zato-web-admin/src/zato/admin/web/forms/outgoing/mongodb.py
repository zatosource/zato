# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Django
from django import forms

# Zato
from zato.admin.web.forms import add_select
from zato.common import MONGODB, TLS

default = MONGODB.DEFAULT
timeout = default.TIMEOUT

class CreateForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))

    username = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    app_name = forms.CharField(widget=forms.TextInput(attrs={'style':'width:20%'}))
    replica_set = forms.CharField(widget=forms.TextInput(attrs={'style':'width:20%'}))

    auth_source = forms.CharField(widget=forms.TextInput(attrs={'style':'width:20%'}))
    auth_mechanism = forms.ChoiceField(widget=forms.Select())

    pool_size_max = forms.CharField(widget=forms.TextInput(attrs={'style':'width:9%'}), initial=default.POOL_SIZE_MAX)

    connect_timeout = forms.CharField(widget=forms.TextInput(attrs={'style':'width:9%'}), initial=timeout.CONNECT)
    socket_timeout = forms.CharField(widget=forms.TextInput(attrs={'style':'width:9%'}), initial=timeout.SOCKET)
    server_select_timeout = forms.CharField(widget=forms.TextInput(attrs={'style':'width:9%'}), initial=timeout.SERVER_SELECT)
    wait_queue_timeout = forms.CharField(widget=forms.TextInput(attrs={'style':'width:9%'}), initial=timeout.WAIT_QUEUE)

    max_idle_time = forms.CharField(widget=forms.TextInput(attrs={'style':'width:9%'}), initial=default.MAX_IDLE_TIME)
    hb_frequency = forms.CharField(widget=forms.TextInput(attrs={'style':'width:9%'}), initial=default.TIMEOUT)

    is_tz_aware = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    document_class = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))

    is_tls_enabled = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    tls_private_key_file = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    tls_cert_file = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    tls_ca_certs_file = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    tls_crl_file = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    tls_version = forms.ChoiceField(widget=forms.Select(), initial=TLS.DEFAULT)
    tls_validate = forms.ChoiceField(widget=forms.Select(), initial=TLS.CERT_VALIDATE.CERT_REQUIRED.id)
    tls_pem_passphrase = forms.CharField(widget=forms.HiddenInput(attrs={'style':'width:100%'}))
    tls_match_hostname_is_enabled = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))

    compressor_list = forms.CharField(widget=forms.TextInput(attrs={'style':'width:30%'}))
    zlib_level = forms.CharField(widget=forms.TextInput(attrs={'style':'width:9%'}))

    write_to = forms.CharField(widget=forms.TextInput(attrs={'style':'width:9%'}))
    write_timeout = forms.CharField(widget=forms.TextInput(attrs={'style':'width:9%'}))
    write_journal_is_enabled = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    write_fsync_is_enabled = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))

    read_pref_type = forms.ChoiceField(widget=forms.Select())
    read_pref_tag_list = forms.CharField(widget=forms.TextInput(attrs={'style':'width:30%'}))
    read_pref_max_stale = forms.CharField(widget=forms.TextInput(attrs={'style':'width:9%'}), initial=default.MAX_STALENESS)

    server_list = forms.CharField(widget=forms.Textarea(attrs={'style':'width:100%'}))

    def __init__(self, prefix=None, post_data=None):
        super(CreateForm, self).__init__(post_data, prefix=prefix)

class EditForm(CreateForm):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    tls_match_hostname = forms.BooleanField(required=False, widget=forms.CheckboxInput())
