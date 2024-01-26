# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Django
from django import forms

MAX_CHARS = 100
PORT = 1414

class CreateForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={'style':'width:35%'}))
    host = forms.CharField(widget=forms.TextInput(attrs={'style':'width:35%'}))
    port = forms.CharField(initial=PORT, widget=forms.TextInput(attrs={'style':'width:20%'}))
    use_jms = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    queue_manager = forms.CharField(widget=forms.TextInput(attrs={'style':'width:35%'}))
    channel = forms.CharField(widget=forms.TextInput(attrs={'style':'width:35%'}))
    username = forms.CharField(widget=forms.TextInput(attrs={'style':'width:35%'}))
    cache_open_send_queues = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    cache_open_receive_queues = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    use_shared_connections = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    ssl = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    ssl_cipher_spec = forms.CharField(widget=forms.TextInput(attrs={'style':'width:60%'}))
    ssl_key_repository = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    needs_mcd = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    max_chars_printed = forms.CharField(initial=MAX_CHARS, widget=forms.TextInput(attrs={'style':'width:20%'}))

class EditForm(CreateForm):
    use_jms = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    cache_open_send_queues = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    cache_open_receive_queues = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    use_shared_connections = forms.BooleanField(required=False, widget=forms.CheckboxInput())
