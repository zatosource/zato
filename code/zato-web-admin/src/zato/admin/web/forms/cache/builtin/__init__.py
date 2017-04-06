# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Django
from django import forms

# Zato
from zato.common import CACHE

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

class EditForm(CreateForm):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    extend_expiry_on_get = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    extend_expiry_on_set = forms.BooleanField(required=False, widget=forms.CheckboxInput())
