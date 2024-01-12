# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Django
from django import forms

# Zato
from zato.common.api import SAP

class CreateForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    host = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    sysnr = forms.CharField(initial=SAP.DEFAULT.INSTANCE, widget=forms.TextInput(attrs={'style':'width:10%'}))
    sysid = forms.CharField(widget=forms.TextInput(attrs={'style':'width:20%'}))
    user = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    client = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    router = forms.CharField(initial='', widget=forms.TextInput(attrs={'style':'width:100%'}))
    pool_size = forms.CharField(initial=SAP.DEFAULT.POOL_SIZE, widget=forms.TextInput(attrs={'style':'width:10%'}))

    def __init__(self, prefix=None, post_data=None):
        super(CreateForm, self).__init__(post_data, prefix=prefix)

class EditForm(CreateForm):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())
