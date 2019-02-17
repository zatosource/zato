# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Django
from django import forms

class CreateForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    log_level = forms.ChoiceField(widget=forms.Select())

    host = forms.CharField(widget=forms.TextInput(attrs={'style':'width:70%'}))
    port = forms.CharField(widget=forms.TextInput(attrs={'style':'width:12%'}))

    username = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    password = forms.CharField(widget=forms.TextInput(attrs={'style':'width:50%'}))
    identity_file = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    ssh_config_file = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))

    buffer_size = forms.CharField(widget=forms.TextInput(attrs={'style':'width:12%'}))
    is_compression_enabled = forms.ChoiceField(widget=forms.Select())
    bandwidth_limit = forms.CharField(widget=forms.TextInput(attrs={'style':'width:10%'}))

    force_ip_type = forms.ChoiceField(widget=forms.Select())
    should_flush = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    should_preserve_meta = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))

    ssh_options = forms.CharField(widget=forms.Textarea(attrs={'style':'width:100%'}))

    def __init__(self, prefix=None, req=None):
        super(CreateForm, self).__init__(prefix=prefix)


class EditForm(CreateForm):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())
