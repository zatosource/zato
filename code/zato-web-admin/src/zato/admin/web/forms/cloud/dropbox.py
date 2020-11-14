# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Django
from django import forms

# Zato
from zato.common.api import DROPBOX

# ################################################################################################################################
# ################################################################################################################################

class CreateForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))

    pool_size = forms.CharField(
        widget=forms.TextInput(attrs={'style':'width:12%'}), initial=DROPBOX.DEFAULT.POOL_SIZE)

    max_retries_on_error = forms.CharField(
        widget=forms.TextInput(attrs={'style':'width:12%'}), initial=DROPBOX.DEFAULT.MAX_RETRIES_ON_ERROR)

    max_retries_on_rate_limit = forms.CharField(
        widget=forms.TextInput(attrs={'style':'width:12%'}), initial=DROPBOX.DEFAULT.MAX_RETRIES_ON_RATE_LIMIT)

    timeout = forms.CharField(widget=forms.TextInput(attrs={'style':'width:12%'}), initial=DROPBOX.DEFAULT.TIMEOUT)
    oauth2_access_token_expiration = forms.CharField(
        widget=forms.TextInput(attrs={'style':'width:12%'}), initial=DROPBOX.DEFAULT.OAUTH2_ACCESS_TOKEN_EXPIRATION)

    oauth2_access_token = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))

    default_scope = forms.CharField(widget=forms.TextInput(attrs={'style':'width:30%'}))
    default_directory = forms.CharField(widget=forms.TextInput(attrs={'style':'width:46.7%'}))

    user_agent = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    http_headers = forms.CharField(widget=forms.Textarea(attrs={'style':'width:100%; height:90px'}))

    def __init__(self, prefix=None, req=None):
        super(CreateForm, self).__init__(prefix=prefix)

# ################################################################################################################################
# ################################################################################################################################

class EditForm(CreateForm):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())

# ################################################################################################################################
# ################################################################################################################################
