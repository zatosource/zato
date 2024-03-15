# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Django
from django import forms

# Zato
from zato.admin.web.forms import add_initial_select, add_select_from_service, add_services
from zato.common.vault_ import VAULT

_auth_method = VAULT.AUTH_METHOD
vault_methods = [_auth_method.GITHUB, _auth_method.TOKEN, _auth_method.USERNAME_PASSWORD]

class CreateForm(forms.Form):

    id = forms.CharField(widget=forms.HiddenInput())
    name = forms.CharField(widget=forms.TextInput(attrs={'class':'required', 'style':'width:100%'}))
    url = forms.CharField(
        initial=VAULT.DEFAULT.URL, widget=forms.TextInput(attrs={'class':'required', 'style':'width:100%'}))
    token = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    default_auth_method = forms.ChoiceField(widget=forms.Select())
    timeout = forms.CharField(
        initial=VAULT.DEFAULT.TIMEOUT, widget=forms.TextInput(attrs={'class':'required', 'style':'width:15%'}))
    allow_redirects = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    tls_verify = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    service_id = forms.ChoiceField(widget=forms.Select())
    tls_key_cert_id = forms.ChoiceField(widget=forms.Select())
    tls_ca_cert_id = forms.ChoiceField(widget=forms.Select())

    def __init__(self, req, prefix=None, *args, **kwargs):
        super(CreateForm, self).__init__(prefix=prefix, *args, **kwargs)

        add_services(self, req, True)
        add_initial_select(self, 'default_auth_method')

        for item in vault_methods:
            self.fields['default_auth_method'].choices.append([item.id, item.name])

        add_select_from_service(self, req, 'zato.security.tls.key-cert.get-list', 'tls_key_cert_id')
        add_select_from_service(self, req, 'zato.security.tls.ca-cert.get-list', 'tls_ca_cert_id')

class EditForm(CreateForm):
    pass
