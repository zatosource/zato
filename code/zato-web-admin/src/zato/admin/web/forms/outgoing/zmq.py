# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Django
from django import forms

# Zato
from zato.common.api import ZMQ

class CreateForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    address = forms.CharField(widget=forms.TextInput(attrs={'style':'width:50%'}))
    socket_type = forms.ChoiceField(widget=forms.Select())
    socket_method = forms.ChoiceField(widget=forms.Select())

    def __init__(self, prefix=None, post_data=None):
        super(CreateForm, self).__init__(post_data, prefix=prefix)

        self._add_field('socket_type', ZMQ.OUTGOING)
        self._add_field('socket_method', ZMQ.METHOD)

    def _add_field(self, field_name, source):
        self.fields[field_name].choices = []
        for code, name in source.items():
            self.fields[field_name].choices.append([code, name])

class EditForm(CreateForm):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())
