# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from operator import itemgetter

# Django
from django import forms

class CreateForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={'class':'required', 'style':'width:100%'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    host = forms.CharField(widget=forms.TextInput(attrs={'class':'required', 'style':'width:50%'}))
    port = forms.CharField(widget=forms.TextInput(attrs={'class':'required', 'style':'width:20%'}))
    bind_dn = forms.CharField(widget=forms.TextInput(attrs={'class':'required'}))
    pool_size = forms.IntegerField(initial=1, widget=forms.TextInput(attrs={'class':'required validate-digits', 'style':'width:30px'}))
    extra = forms.CharField(widget=forms.Textarea())


class EditForm(CreateForm):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())
