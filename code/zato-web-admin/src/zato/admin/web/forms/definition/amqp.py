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

# pika
from pika.spec import FRAME_MAX_SIZE, PORT

# Django
from django import forms

# Zato
from zato.common.util import make_repr


class CreateForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    host = forms.CharField(widget=forms.TextInput(attrs={'style':'width:50%'}))
    port = forms.CharField(initial=PORT, widget=forms.TextInput(attrs={'style':'width:20%'}))
    vhost = forms.CharField(initial='/', widget=forms.TextInput(attrs={'style':'width:50%'}))
    username = forms.CharField(widget=forms.TextInput(attrs={'style':'width:50%'}))
    frame_max = forms.CharField(initial=FRAME_MAX_SIZE, widget=forms.TextInput(attrs={'style':'width:20%'}))
    heartbeat = forms.CharField(initial=0, widget=forms.TextInput(attrs={'style':'width:10%'}))

    def __repr__(self):
        return make_repr(self)
    
class EditForm(CreateForm):
    pass

    