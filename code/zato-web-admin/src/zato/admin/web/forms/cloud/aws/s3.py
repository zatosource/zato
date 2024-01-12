# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Django
from django import forms

# Zato
from zato.admin.web.forms import add_security_select
from zato.common.api import CLOUD

class CreateForm(forms.Form):

    name = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    pool_size = forms.CharField(initial=CLOUD.AWS.S3.DEFAULTS.POOL_SIZE, widget=forms.TextInput(attrs={'style':'width:15%'}))
    debug_level = forms.CharField(initial=CLOUD.AWS.S3.DEFAULTS.DEBUG_LEVEL, widget=forms.TextInput(attrs={'style':'width:15%'}))
    content_type = forms.CharField(initial=CLOUD.AWS.S3.DEFAULTS.CONTENT_TYPE, widget=forms.TextInput(attrs={'style':'width:100%'}))

    suppr_cons_slashes = forms.BooleanField(initial=True, required=False, widget=forms.CheckboxInput())
    address = forms.CharField(initial=CLOUD.AWS.S3.DEFAULTS.ADDRESS, widget=forms.TextInput(attrs={'style':'width:100%'}))
    metadata_ = forms.CharField(widget=forms.Textarea(attrs={'style':'width:100%'}))

    bucket = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    encrypt_at_rest = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    storage_class = forms.ChoiceField(widget=forms.Select())

    security_id = forms.ChoiceField(widget=forms.Select())

    def __init__(self, security_list=None, storage_class_list=None, prefix=None, post_data=None):
        super(CreateForm, self).__init__(post_data, prefix=prefix)
        add_security_select(self, security_list, False, 'security_id', False)

        self.fields['storage_class'].choices = []
        for name in CLOUD.AWS.S3.STORAGE_CLASS():
            self.fields['storage_class'].choices.append([name, name])

class EditForm(CreateForm):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    suppr_cons_slashes = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    encrypt_at_rest = forms.BooleanField(required=False, widget=forms.CheckboxInput())
