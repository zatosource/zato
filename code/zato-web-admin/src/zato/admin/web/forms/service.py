# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Django
from django import forms

# Zato
from zato.admin.web.forms import UploadForm, WithJSONSchema, WithRateLimiting

class CreateForm(WithJSONSchema, WithRateLimiting):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    slow_threshold = forms.CharField(widget=forms.TextInput(attrs={'style':'width:15%'}))
    is_rate_limit_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    rate_limit_check_parent_def = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))

class EditForm(CreateForm):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'style':'text-align:left'}))

class WSDLUploadForm(UploadForm):
    pass
