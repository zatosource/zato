# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Django
from django import forms

class DefinitionForm(forms.Form):
    id = forms.CharField(widget=forms.HiddenInput())
    url_pattern = forms.CharField(widget=forms.TextInput(attrs={'class':'required', 'style':'width:90%'}))
