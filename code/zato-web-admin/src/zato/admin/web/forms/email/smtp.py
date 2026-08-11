# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Django
from django import forms

# Zato
from zato.common.api import EMAIL

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, strnone

# ################################################################################################################################
# ################################################################################################################################

class CreateForm(forms.Form):
    id = forms.CharField(widget=forms.HiddenInput())
    name = forms.CharField(widget=forms.TextInput(attrs={'class':'required', 'style':'width:100%'}))

    # The checkbox cluster - active, audit log, TLS verification and protocol debugging
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    is_audit_log_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    needs_tls_verify = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    is_debug = forms.BooleanField(required=False, widget=forms.CheckboxInput())

    # What kind of server the connection speaks to - generic SMTP or Microsoft 365
    server_type = forms.ChoiceField(widget=forms.Select())

    # The provider preset and connection mode share one row
    provider = forms.ChoiceField(widget=forms.Select(attrs={'style':'width:45%'}))
    mode = forms.ChoiceField(widget=forms.Select(attrs={'style':'width:45%'}))

    # The host and port share one row - a Microsoft 365 connection leaves them empty
    host = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:73%'}))
    port = forms.CharField(initial=EMAIL.DEFAULT.SMTP_PORT,
        widget=forms.TextInput(attrs={'style':'width:19%'}))

    # The username and From address share one row
    username = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:46%', 'autocomplete':'off'}))
    from_address = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:46%'}))

    # The Microsoft 365 tenant and application the connection authenticates as
    tenant_id = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:100%'}))
    client_id = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:100%'}))

    # Rarely used options, collapsed by default
    timeout = forms.CharField(initial=EMAIL.DEFAULT.TIMEOUT,
        widget=forms.TextInput(attrs={'class':'required', 'style':'width:19%'}))
    helo_hostname = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:100%'}))
    ca_certs_path = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:100%'}))
    ping_address = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:100%'}))

    def __init__(self, prefix:'strnone'=None, post_data:'any_'=None) -> 'None':
        super(CreateForm, self).__init__(post_data, prefix=prefix)

        # Modes are iterated in their preferred order, which makes STARTTLS the default one
        mode_choices = []
        for item in EMAIL.SMTP.MODE():
            mode_choices.append((item, item))

        self.fields['mode'].choices = mode_choices

        # Provider presets are filled into the other fields by the accompanying JS code
        provider_choices = []
        for item in EMAIL.SMTP.ProviderList:
            provider_choices.append((item['name'], item['name']))

        self.fields['provider'].choices = provider_choices

        server_type_choices = []
        for key, value in EMAIL.SMTP.ServerTypeHuman.items():
            server_type_choices.append((key, value))

        self.fields['server_type'].choices = server_type_choices

# ################################################################################################################################
# ################################################################################################################################

class EditForm(CreateForm):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    is_audit_log_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    needs_tls_verify = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    is_debug = forms.BooleanField(required=False, widget=forms.CheckboxInput())

# ################################################################################################################################
# ################################################################################################################################
