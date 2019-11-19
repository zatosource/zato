# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Django
from django import forms

# Zato
from zato.common import CACHE
from zato.admin.web.forms import add_select

# ################################################################################################################################

class CreateForm(forms.Form):
    id = forms.CharField(widget=forms.HiddenInput())
    key = forms.CharField(widget=forms.Textarea(attrs={'class':'required', 'style':'width:100%; height:70px'}))
    value = forms.CharField(widget=forms.Textarea(attrs={'class':'required', 'style':'width:100%%; height:240px'}))
    expiry = forms.CharField(widget=forms.TextInput(attrs={'class':'required', 'style':'width:40%'}), initial=0)
    key_data_type = forms.ChoiceField(widget=forms.Select(), initial=CACHE.BUILTIN_KV_DATA_TYPE.STR.id)
    value_data_type = forms.ChoiceField(widget=forms.Select(), initial=CACHE.BUILTIN_KV_DATA_TYPE.STR.id)
    replace_existing = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    cache_id = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, post_data=None, req=None):
        super(CreateForm, self).__init__(post_data)
        add_select(self, 'key_data_type', CACHE.BUILTIN_KV_DATA_TYPE())
        add_select(self, 'value_data_type', CACHE.BUILTIN_KV_DATA_TYPE())

# ################################################################################################################################

class EditForm(CreateForm):
    replace_existing = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    old_key = forms.CharField(widget=forms.Textarea(attrs={'class':'required', 'style':'display:none'}))

# ################################################################################################################################
