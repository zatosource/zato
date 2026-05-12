# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Django
from django import forms

# Zato
from zato.common.api import OAuth as OAuthCommon, IO
from zato.admin.web.forms import add_select

# ################################################################################################################################
# ################################################################################################################################

_default = OAuthCommon.Default

# ################################################################################################################################
# ################################################################################################################################

class CreateForm(forms.Form):
    id = forms.CharField(widget=forms.HiddenInput())

    name = forms.CharField(widget=forms.TextInput(attrs={'class':'required', 'style':'width:60%'}))
    username = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:100%'}))
    secret = forms.CharField(required=False, widget=forms.PasswordInput(attrs={'style':'width:100%'}))

    auth_server_url = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:100%'}), initial=_default.Auth_Server_URL)
    scopes = forms.CharField(required=False, widget=forms.Textarea(attrs={'style':'width:100%; height:30px'}), initial='\n'.join(_default.Scopes))

    client_id_field = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:100%'}), initial=_default.Client_ID_Field)
    client_secret_field = forms.CharField(
        required=False, widget=forms.TextInput(attrs={'style':'width:100%'}), initial=_default.Client_Secret_Field)

    grant_type = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:100%'}), initial=_default.Grant_Type)
    extra_fields = forms.CharField(required=False, widget=forms.Textarea(attrs={'style':'width:100%; height:30px'}))

    data_format = forms.ChoiceField(widget=forms.Select())

    # Static token fields
    static_header = forms.CharField(
        required=False, widget=forms.TextInput(attrs={'style':'width:100%'}), initial='Authorization')
    static_token = forms.CharField(
        required=False, widget=forms.PasswordInput(attrs={'style':'width:100%'}))
    static_prefix = forms.CharField(
        required=False, widget=forms.TextInput(attrs={'style':'width:100%'}), initial='bearer')

    def __init__(self, prefix=None, post_data=None):
        super(CreateForm, self).__init__(post_data, prefix=prefix)

        add_select(self, 'data_format', IO.Bearer_Token_Format, needs_initial_select=False)

# ################################################################################################################################
# ################################################################################################################################

class EditForm(CreateForm):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())

# ################################################################################################################################
# ################################################################################################################################
