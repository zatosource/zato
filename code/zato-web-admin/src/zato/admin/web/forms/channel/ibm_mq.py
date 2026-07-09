# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Django
from django import forms

# Zato
from zato.admin.web.forms import add_services

class CreateForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    address = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}), initial='localhost:1414')
    queue_manager = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}), initial='QM1')
    mq_channel_name = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}), initial='DEV.APP.SVRCONN')
    queue = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    service = forms.ChoiceField(widget=forms.Select(attrs={'style':'width:100%'}))
    username = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:100%'}))
    ssl = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    cipher_spec = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:100%'}),
        initial='ANY_TLS12_OR_HIGHER')
    ssl_ca_file = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:100%'}))
    ssl_cert_file = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:100%'}))
    ssl_key_file = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:100%'}))
    remove_jms_headers = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))

    def __init__(self, prefix=None, post_data=None, req=None):
        super().__init__(post_data, prefix=prefix)
        add_services(self, req)

class EditForm(CreateForm):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    remove_jms_headers = forms.BooleanField(required=False, widget=forms.CheckboxInput())
