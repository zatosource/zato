# -*- coding: utf-8 -*-

"""
Copyright (C) 2017, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Django
from django import forms

class MsgForm(forms.Form):
    correl_id = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    in_reply_to = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    expiration = forms.CharField(widget=forms.TextInput(attrs={'class':'required', 'style':'width:50%'}))
    priority = forms.CharField(widget=forms.TextInput(attrs={'class':'required', 'style':'width:20%'}))
    mime_type = forms.CharField(widget=forms.HiddenInput())
