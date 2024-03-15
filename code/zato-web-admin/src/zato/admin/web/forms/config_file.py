# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Django
from django import forms

class CreateForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    data = forms.CharField(widget=forms.Textarea(attrs={'style':'overflow:auto; width:100%; white-space: pre-wrap;height:400px'}))

class EditForm(CreateForm):
    pass
