# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at gefira.pl>

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

class CreateForm(forms.Form):
    id = forms.CharField(widget=forms.HiddenInput())
    name = forms.CharField(widget=forms.TextInput(attrs={"class":"required", "style":"width:90%"}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    username = forms.CharField(widget=forms.TextInput(attrs={"class":"required", "style":"width:90%"}))
    reject_empty_nonce_creat = forms.BooleanField(widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    reject_stale_tokens = forms.BooleanField(widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    reject_expiry_limit = forms.IntegerField(widget=forms.TextInput(attrs={"class":"required validate-digits", "style":"width:20%"}))
    nonce_freshness_time = forms.IntegerField(widget=forms.TextInput(attrs={"class":"required validate-digits", "style":"width:20%"}))
            
class EditForm(CreateForm):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    reject_empty_nonce_creat = forms.BooleanField(widget=forms.CheckboxInput())
    reject_stale_tokens = forms.BooleanField(widget=forms.CheckboxInput())
