# -*- coding: utf-8 -*-

"""
Copyright (C) 2022 Dariusz Suchojad <dsuch at zato.io>

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
    scopes = forms.CharField(widget=forms.Textarea(attrs={'style':'width:100%; height:80px'}), initial='\n'.join(_default.Scopes))

    def __init__(self, prefix=None, post_data=None):
        super(CreateForm, self).__init__(post_data, prefix=prefix)

# ################################################################################################################################
# ################################################################################################################################

class EditForm(CreateForm):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())

# ################################################################################################################################
# ################################################################################################################################
