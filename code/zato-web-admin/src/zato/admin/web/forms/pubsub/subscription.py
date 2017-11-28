# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Django
from django import forms

# ################################################################################################################################

class CreateForm(forms.Form):

    id = forms.CharField(widget=forms.HiddenInput())
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    endpoint_id = forms.ChoiceField(widget=forms.Select())
    topic_list_text = forms.CharField(widget=forms.Textarea(attrs={'style':'width:100%; height:120px'}))
    topic_list_json = forms.CharField(widget=forms.Textarea(attrs={'display':'none'}))

    def __init__(self, req, *args, **kwargs):
        super(CreateForm, self).__init__(*args, **kwargs)

# ################################################################################################################################

class EditForm(CreateForm):
    pass

# ################################################################################################################################
