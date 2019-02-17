# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Django
from django import forms

# Zato
from zato.common import STOMP

class CreateForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    address = forms.CharField(initial=STOMP.DEFAULT.ADDRESS, widget=forms.TextInput(attrs={'style':'width:70%'}))
    username = forms.CharField(initial=STOMP.DEFAULT.USERNAME, widget=forms.TextInput(attrs={'style':'width:50%'}))
    proto_version = forms.ChoiceField(widget=forms.Select())
    timeout = forms.CharField(initial=STOMP.DEFAULT.TIMEOUT, widget=forms.TextInput(attrs={'style':'width:10%'}))
    service_name = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    sub_to = forms.CharField(widget=forms.Textarea(attrs={'style':'width:100%'}))

    def __init__(self, prefix=None, post_data=None):
        super(CreateForm, self).__init__(post_data, prefix=prefix)

        self.fields['proto_version'].choices = []
        for item in STOMP.PROTOCOL:
            self.fields['proto_version'].choices.append([item.id, item.name])

class EditForm(CreateForm):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())
