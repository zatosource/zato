# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Django
from django import forms

# Zato
from zato.common import CLOUD

class CreateForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    pool_size = forms.CharField(initial=CLOUD.AWS.S3.DEFAULTS.POOL_SIZE, widget=forms.TextInput(attrs={'style':'width:15%'}))
    debug_level = forms.CharField(initial=CLOUD.AWS.S3.DEFAULTS.DEBUG_LEVEL, widget=forms.TextInput(attrs={'style':'width:15%'}))
    content_type = forms.CharField(initial=CLOUD.AWS.S3.DEFAULTS.CONTENT_TYPE, widget=forms.TextInput(attrs={'style':'width:100%'}))

    suppr_cons_slashes = forms.BooleanField(initial=True, required=False, widget=forms.CheckboxInput())
    address = forms.CharField(initial=CLOUD.AWS.S3.DEFAULTS.ADDRESS, widget=forms.TextInput(attrs={'style':'width:100%'}))
    metadata_ = forms.CharField(widget=forms.Textarea(attrs={'style':'width:100%'}))

    def __init__(self, prefix=None, post_data=None):
        super(CreateForm, self).__init__(post_data, prefix=prefix)

class EditForm(CreateForm):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    suppr_cons_slashes = forms.BooleanField(required=False, widget=forms.CheckboxInput())

