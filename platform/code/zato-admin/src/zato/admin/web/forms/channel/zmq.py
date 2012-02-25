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

# Zato
from zato.common import ZMQ_CHANNEL_TYPES

class CreateForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    address = forms.CharField(widget=forms.TextInput(attrs={'style':'width:50%'}))
    socket_type = forms.ChoiceField(widget=forms.Select())
    service = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    sub_key = forms.CharField(widget=forms.TextInput(attrs={'style':'width:50%'}))

    def __init__(self, prefix=None, post_data=None):
        super(CreateForm, self).__init__(post_data, prefix=prefix)
        
        self.fields['socket_type'].choices = []
        for name in sorted(ZMQ_CHANNEL_TYPES):
            self.fields['socket_type'].choices.append([name, name])

class EditForm(CreateForm):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    