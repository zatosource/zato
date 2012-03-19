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
from zato.admin.web.forms import ChooseClusterForm as _ChooseClusterForm
from zato.common import SOAP_VERSIONS, ZATO_NONE

class CreateForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    host = forms.CharField(initial='http://', widget=forms.TextInput(attrs={'style':'width:100%'}))
    url_path = forms.CharField(initial='/', widget=forms.TextInput(attrs={'style':'width:50%'}))
    method = forms.CharField(widget=forms.TextInput(attrs={'style':'width:20%'}))
    soap_action = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    soap_version = forms.ChoiceField(widget=forms.Select())
    service = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    security = forms.ChoiceField(widget=forms.Select())
    connection = forms.CharField(widget=forms.HiddenInput())
    transport = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, security_list=[], prefix=None, post_data=None):
        super(CreateForm, self).__init__(post_data, prefix=prefix)

        self.fields['soap_version'].choices = []
        for name in sorted(SOAP_VERSIONS):
            self.fields['soap_version'].choices.append([name, name])
            
        self.fields['security'].choices = []
        self.fields['security'].choices.append(['', '----------'])
        self.fields['security'].choices.append([ZATO_NONE, 'No security'])
        
        for value, label in security_list:
            self.fields['security'].choices.append([value, label])

class EditForm(CreateForm):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())

class ChooseClusterForm(_ChooseClusterForm):
    connection = forms.CharField(widget=forms.HiddenInput())
    transport = forms.CharField(widget=forms.HiddenInput())