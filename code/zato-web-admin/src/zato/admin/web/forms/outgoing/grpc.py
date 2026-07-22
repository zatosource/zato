# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Django
from django import forms

# Zato
from zato.admin.web.forms import add_security_select
from zato.common.api import GRPC

# ################################################################################################################################
# ################################################################################################################################

class CreateForm(forms.Form):

    name = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    address = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}), initial=GRPC.Default.Address)
    security_id = forms.ChoiceField(widget=forms.Select())

    is_tls = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    tls_ca_certs_file = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}), required=False)

    proto_path = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}), required=False)
    stub_module = forms.CharField(widget=forms.TextInput(attrs={'style':'width:47%'}), required=False)
    stub_class = forms.CharField(widget=forms.TextInput(attrs={'style':'width:47%'}), required=False)

    ping_timeout = forms.CharField(
        widget=forms.TextInput(attrs={'style':'width:10%'}), initial=GRPC.Default.Ping_Timeout, required=False)
    max_send_message_size = forms.CharField(
        widget=forms.TextInput(attrs={'style':'width:20%'}), initial=GRPC.Default.Max_Message_Size, required=False)
    max_recv_message_size = forms.CharField(
        widget=forms.TextInput(attrs={'style':'width:20%'}), initial=GRPC.Default.Max_Message_Size, required=False)

    def __init__(self, req, security_list, prefix=None):
        super(CreateForm, self).__init__(prefix=prefix)
        add_security_select(self, security_list, field_name='security_id')

# ################################################################################################################################
# ################################################################################################################################

class EditForm(CreateForm):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    is_tls = forms.BooleanField(required=False, widget=forms.CheckboxInput())

# ################################################################################################################################
# ################################################################################################################################
