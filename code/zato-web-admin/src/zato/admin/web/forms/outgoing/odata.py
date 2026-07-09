# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Django
from django import forms

# Zato
from zato.admin.web.forms import add_select
from zato.common.api import ODATA

# ################################################################################################################################
# ################################################################################################################################

class CreateForm(forms.Form):

    name = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))

    address = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))

    odata_version = forms.ChoiceField(widget=forms.Select(), initial=ODATA.DEFAULT.ODATA_VERSION)
    auth_type = forms.ChoiceField(widget=forms.Select())

    username = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}), required=False)

    token_url = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}), required=False)
    tenant_id = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}), required=False)
    client_id = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}), required=False)
    scopes = forms.CharField(widget=forms.Textarea(attrs={'style':'width:100%; height:40px'}), required=False)

    needs_csrf_token = forms.BooleanField(required=False, widget=forms.CheckboxInput())

    page_size = forms.CharField(widget=forms.TextInput(attrs={'style':'width:9%'}), initial=ODATA.DEFAULT.PAGE_SIZE)
    timeout = forms.CharField(widget=forms.TextInput(attrs={'style':'width:9%'}), initial=ODATA.DEFAULT.TIMEOUT)
    pool_size = forms.CharField(widget=forms.TextInput(attrs={'style':'width:9%'}), initial=ODATA.DEFAULT.POOL_SIZE)

    def __init__(self, *args, **kwargs):
        super(CreateForm, self).__init__(*args, **kwargs)

        add_select(self, 'odata_version', ODATA.VERSION(), needs_initial_select=False)
        add_select(self, 'auth_type', ODATA.AUTH_TYPE(), needs_initial_select=False)

# ################################################################################################################################
# ################################################################################################################################

class EditForm(CreateForm):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())

# ################################################################################################################################
# ################################################################################################################################
