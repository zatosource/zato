# -*- coding: utf-8 -*-

"""
Copyright (C) 2012 Dariusz Suchojad <dsuch at gefira.pl>

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
from zato.admin.web.forms import INITIAL_CHOICES

class NForm(forms.Form):
    n = forms.IntegerField(widget=forms.TextInput(attrs={'style':'width:30px'}))

class CompareForm(forms.Form):
    compare_to = forms.ChoiceField()
    
    def __init__(self, compare_to=[], *args, **kwargs):
        super(CompareForm, self).__init__(*args, **kwargs)
        for name, value in self.fields.items():
            if isinstance(value, forms.ChoiceField):
                self.fields[name].choices = [INITIAL_CHOICES]
                
        for name, label in compare_to:
            self.fields['compare_to'].choices.append([name, label])
            
        self.fields['compare_to'].choices.append(['custom', 'Choose a time span ..'])
