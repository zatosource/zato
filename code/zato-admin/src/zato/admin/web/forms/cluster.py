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

# stdlib
from operator import itemgetter

# Django
from django import forms

# Zato
from zato.admin.settings import odb_engine_friendly_name
from zato.common.util import make_repr

# We let the user delete a cluster only if the answer on the form is equal to the
# one given below.
OK_TO_DELETE = 'YES'

class CreateClusterForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={'class':'required', 'style':'width:100%'}))
    description = forms.CharField(widget=forms.Textarea(), required=False)

    odb_type = forms.ChoiceField(widget=forms.Select())
    odb_host = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    odb_port = forms.CharField(widget=forms.TextInput(attrs={'style':'width:50%'}))
    odb_db_name = forms.CharField(widget=forms.TextInput(attrs={'class':'required', 'style':'width:100%'}))
    odb_user = forms.CharField(widget=forms.TextInput(attrs={'class':'required', 'style':'width:100%'}))
    odb_schema = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}), required=False)

    lb_host = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    lb_port = forms.CharField(widget=forms.TextInput(attrs={'style':'width:50%'}))
    lb_agent_port = forms.CharField(widget=forms.TextInput(attrs={'style':'width:50%'}))

    broker_host = forms.CharField(widget=forms.TextInput(attrs={'class':'required', 'style':'width:100%'}))
    broker_start_port = forms.CharField(widget=forms.TextInput(attrs={'style':'width:30%'}))
    broker_token = forms.CharField(widget=forms.TextInput(attrs={'class':'required', 'style':'width:100%'}))

    def __init__(self, post_data=None, initial={}, prefix=None):
        super(CreateClusterForm, self).__init__(post_data, initial=initial, prefix=prefix)
        self.fields['odb_type'].choices = []

        # Sort engines by their friendly name.
        engines = sorted(odb_engine_friendly_name.iteritems(), key=itemgetter(1))

        for engine, friendly_name in engines:
            self.fields['odb_type'].choices.append([engine, friendly_name])

        if 'odb_type' in initial:
            self.base_fields['odb_type'].initial = initial['odb_type']

    def __repr__(self):
        return make_repr(self)

class EditClusterForm(CreateClusterForm):
    pass

class DeleteClusterForm(forms.Form):
    answer = forms.CharField(widget=forms.TextInput(attrs={'class':'required', 'style':'width:10%'}))
    cluster_id = forms.CharField(widget=forms.HiddenInput(attrs={'class':'required'}))

    def clean_answer(self):
        data = self.cleaned_data['answer']
        if data != OK_TO_DELETE:
            msg = "Can't delete the cluster, answer [{data}] wasn't equal to [{expected}]".format(
                data=data, expected=OK_TO_DELETE)
            raise Exception(msg)

        return data
    
class EditServerForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={'class':'required', 'style':'width:100%'}))