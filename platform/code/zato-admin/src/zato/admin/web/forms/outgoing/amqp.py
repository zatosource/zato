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

# stdlib
from operator import itemgetter

# Django
from django import forms

# Zato
from zato.admin.settings import delivery_friendly_name
from zato.common.odb import AMQP_DEFAULT_PRIORITY
from zato.common.util import make_repr


class CreateForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    delivery_mode = forms.ChoiceField(widget=forms.Select())
    priority = forms.CharField(initial=AMQP_DEFAULT_PRIORITY, widget=forms.TextInput(attrs={'style':'width:5%'}))
    content_type = forms.CharField(widget=forms.TextInput(attrs={'style':'width:50%'}))
    content_encoding = forms.CharField(widget=forms.TextInput(attrs={'style':'width:50%'}))
    expiration = forms.CharField(widget=forms.TextInput(attrs={'style':'width:20%'}))
    user_id = forms.CharField(widget=forms.TextInput(attrs={'style':'width:50%'}))
    app_id = forms.CharField(widget=forms.TextInput(attrs={'style':'width:50%'}))
    def_id = forms.ChoiceField(widget=forms.Select())

    def __init__(self, prefix=None, post_data=None):
        super(CreateForm, self).__init__(post_data, prefix=prefix)
        
        self.fields['delivery_mode'].choices = []
        self.fields['def_id'].choices = []

        # Sort modes by their friendly name.
        modes = sorted(delivery_friendly_name.iteritems(), key=itemgetter(1))

        for mode, friendly_name in modes:
            self.fields['delivery_mode'].choices.append([mode, friendly_name])
            
    def set_def_id(self, def_ids):
        # Sort AMQP definitions by their names.
        def_ids = sorted(def_ids.iteritems(), key=itemgetter(1))

        for id, name in def_ids:
            self.fields['def_id'].choices.append([id, name])

class EditForm(CreateForm):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    