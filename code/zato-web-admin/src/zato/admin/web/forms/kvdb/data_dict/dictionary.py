# -*- coding: utf-8 -*-

"""
Copyright (C) 2012 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Django
from django import forms

class CreateForm(forms.Form):
    system = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    key = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    value = forms.CharField(required=False, widget=forms.Textarea(attrs={'style':'width:100%'}))

class EditForm(CreateForm):
    pass
