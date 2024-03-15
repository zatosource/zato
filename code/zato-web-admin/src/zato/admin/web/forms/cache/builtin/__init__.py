# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Django
from django import forms

# Zato
from zato.common.api import CACHE
from zato.admin.web.forms import add_select

# ################################################################################################################################

class CreateForm(forms.Form):
    id = forms.CharField(widget=forms.HiddenInput())
    name = forms.CharField(widget=forms.TextInput(attrs={'class':'required', 'style':'width:100%'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    is_default = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    max_size = forms.CharField(
        initial=CACHE.DEFAULT.MAX_SIZE, widget=forms.TextInput(attrs={'class':'required', 'style':'width:15%'}))
    max_item_size = forms.CharField(
        initial=CACHE.DEFAULT.MAX_ITEM_SIZE, widget=forms.TextInput(attrs={'class':'required', 'style':'width:15%'}))
    extend_expiry_on_get = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    extend_expiry_on_set = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    sync_method = forms.ChoiceField(widget=forms.Select(attrs={'style':'width:50%'}))
    persistent_storage = forms.ChoiceField(widget=forms.Select(attrs={'style':'width:50%'}))
    cache_id = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, prefix=None, post_data=None, req=None):
        super(CreateForm, self).__init__(post_data, prefix=prefix)
        add_select(self, 'sync_method', CACHE.SYNC_METHOD())
        add_select(self, 'persistent_storage', CACHE.PERSISTENT_STORAGE())

# ################################################################################################################################

class EditForm(CreateForm):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    is_default = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    extend_expiry_on_get = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    extend_expiry_on_set = forms.BooleanField(required=False, widget=forms.CheckboxInput())

# ################################################################################################################################
