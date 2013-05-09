# -*- coding: utf-8 -*-

"""
Copyright (C) 2011 Dariusz Suchojad <dsuch at gefira.pl>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Django
from django import forms

PORT = 1414
MAX_CHARS = 100

class CreateForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    host = forms.CharField(widget=forms.TextInput(attrs={'style':'width:50%'}))
    port = forms.CharField(initial=PORT, widget=forms.TextInput(attrs={'style':'width:20%'}))
    queue_manager = forms.CharField(widget=forms.TextInput(attrs={'style':'width:50%'}))
    channel = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    cache_open_send_queues = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    cache_open_receive_queues = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    use_shared_connections = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    ssl = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    ssl_cipher_spec = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    ssl_key_repository = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    needs_mcd = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    max_chars_printed = forms.CharField(initial=MAX_CHARS, widget=forms.TextInput(attrs={'style':'width:20%'}))

class EditForm(CreateForm):
    cache_open_send_queues = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    cache_open_receive_queues = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    use_shared_connections = forms.BooleanField(required=False, widget=forms.CheckboxInput())
