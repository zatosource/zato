# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Django
from django import forms

# Zato
from zato.admin.web.forms import add_select, add_sec_tls_ca_cert_id_select, add_security_select
from zato.common.api import HL7 as HL7Commonn

# ################################################################################################################################
# ################################################################################################################################

_const = HL7Commonn.Const
_default = HL7Commonn.Default

# ################################################################################################################################
# ################################################################################################################################

class CreateForm(forms.Form):

    name = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    pool_size = forms.CharField(widget=forms.TextInput(attrs={'style':'width:10%'}), initial=_default.pool_size)

    address = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}), initial=_default.address_fhir)
    auth_type = forms.ChoiceField(widget=forms.Select())

    username = forms.CharField(widget=forms.TextInput(attrs={'style':'width:50%'}))
    password = forms.CharField(strip=False, widget=forms.PasswordInput(attrs={'style':'width:100%'}))

    security_id = forms.ChoiceField(widget=forms.Select())
    sec_tls_ca_cert_id = forms.ChoiceField(widget=forms.Select())

    extra = forms.CharField(widget=forms.Textarea(attrs={'style':'height:60px'}))

    def __init__(self, req, security_list, prefix=None):
        super(CreateForm, self).__init__(prefix=prefix)
        add_select(self, 'auth_type', _const.FHIR_Auth_Type(), needs_initial_select=True)

        add_security_select(self, security_list, field_name='security_id', needs_rbac=False)
        add_sec_tls_ca_cert_id_select(req, self)

# ################################################################################################################################
# ################################################################################################################################

class EditForm(CreateForm):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())

# ################################################################################################################################
# ################################################################################################################################
