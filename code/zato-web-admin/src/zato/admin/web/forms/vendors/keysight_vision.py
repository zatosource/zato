# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Django
from django import forms

# Zato
from zato.admin.web.forms import add_sec_tls_ca_cert_id_select, WithAuditLog

# ################################################################################################################################
# ################################################################################################################################

class CreateForm(WithAuditLog):

    name = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))

    host = forms.CharField(initial='https://', widget=forms.TextInput(attrs={'style':'width:100%'}))
    sec_tls_ca_cert_id = forms.ChoiceField(widget=forms.Select())

    username = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    password = forms.CharField(strip=False, widget=forms.PasswordInput(attrs={'style':'width:100%'}))

    def __init__(self, req=None, prefix=None):
        super(CreateForm, self).__init__(prefix=prefix)
        add_sec_tls_ca_cert_id_select(req, self)

# ################################################################################################################################
# ################################################################################################################################

class EditForm(CreateForm):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())

# ################################################################################################################################
# ################################################################################################################################
