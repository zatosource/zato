# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Django
from django import forms

# Zato
from zato.admin.web.forms import add_security_select
from zato.common.api import DEFAULT_HTTP_PING_METHOD, MISC, SOAP_VERSIONS

# ################################################################################################################################
# ################################################################################################################################

_validate_tls_choices = [
    (True, 'Yes'),
    (False, 'No'),
]

# ################################################################################################################################
# ################################################################################################################################

class CreateForm(forms.Form):

    # Main
    name = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    host = forms.CharField(initial='https://', widget=forms.TextInput(attrs={'style':'width:100%'}))
    url_path = forms.CharField(required=False, initial='/', widget=forms.TextInput(attrs={'style':'width:100%'}))
    soap_action = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:100%'}))
    timeout = forms.CharField(initial=MISC.DEFAULT_HTTP_TIMEOUT, widget=forms.TextInput(attrs={'style':'width:10%'}))

    # SOAP
    soap_version = forms.ChoiceField(widget=forms.Select())
    use_ws_addressing = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    use_mtom = forms.BooleanField(required=False, widget=forms.CheckboxInput())

    # Security
    security_id = forms.ChoiceField(widget=forms.Select(attrs={'style':'width:100%'}))
    validate_tls = forms.ChoiceField(widget=forms.Select())
    tls_client_cert = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:100%'}))
    tls_client_key = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:100%'}))

    # Body credentials - a JSON list of mapping rows managed in JavaScript
    body_credentials = forms.CharField(required=False, widget=forms.HiddenInput())

    # More
    ping_method = forms.CharField(initial=DEFAULT_HTTP_PING_METHOD, widget=forms.TextInput(attrs={'style':'width:20%'}))
    content_type = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:100%'}))

    serialization_type = forms.CharField(initial='string', widget=forms.HiddenInput())

    def __init__(self, security_list=None, prefix=None, post_data=None, req=None):
        security_list = security_list or []
        super(CreateForm, self).__init__(post_data, prefix=prefix)

        self.fields['soap_version'].choices = []
        for name in sorted(SOAP_VERSIONS):
            self.fields['soap_version'].choices.append([name, name])

        self.fields['validate_tls'].choices = []
        for value, label in _validate_tls_choices:
            self.fields['validate_tls'].choices.append([value, label])

        add_security_select(self, security_list, field_name='security_id')

# ################################################################################################################################
# ################################################################################################################################

class EditForm(CreateForm):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())

# ################################################################################################################################
# ################################################################################################################################
