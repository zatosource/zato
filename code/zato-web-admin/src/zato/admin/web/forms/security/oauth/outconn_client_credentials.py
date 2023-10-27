# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# Django
from django import forms

# Zato
from zato.common.api import OAuth as OAuthCommon

# ################################################################################################################################
# ################################################################################################################################

_default = OAuthCommon.Default

# ################################################################################################################################
# ################################################################################################################################

class CreateForm(forms.Form):
    id = forms.CharField(widget=forms.HiddenInput())

    name = forms.CharField(widget=forms.TextInput(attrs={'class':'required', 'style':'width:100%'}))
    username = forms.CharField(widget=forms.TextInput(attrs={'class':'required', 'style':'width:100%'}))

    auth_server_url = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}), initial=_default.Auth_Server_URL)
    scopes = forms.CharField(widget=forms.Textarea(attrs={'style':'width:100%; height:30px'}), initial='\n'.join(_default.Scopes))

    client_id_field = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}), initial=_default.Client_ID_Field)
    client_secret_field = forms.CharField(
        widget=forms.TextInput(attrs={'style':'width:100%'}), initial=_default.Client_Secret_Field)

    grant_type = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}), initial=_default.Grant_Type)

    def __init__(self, prefix=None, post_data=None):
        super(CreateForm, self).__init__(post_data, prefix=prefix)

# ################################################################################################################################
# ################################################################################################################################

class EditForm(CreateForm):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())

# ################################################################################################################################
# ################################################################################################################################
