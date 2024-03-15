# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Django
from django import forms

# Zato
from zato.common.util.api import make_repr

# Defaults per AMQP spec
FRAME_MAX_SIZE = 131072
PORT = 5672

class CreateForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    host = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    port = forms.CharField(initial=PORT, widget=forms.TextInput(attrs={'style':'width:20%'}))
    vhost = forms.CharField(initial='/', widget=forms.TextInput(attrs={'style':'width:50%'}))
    username = forms.CharField(widget=forms.TextInput(attrs={'style':'width:50%'}))
    frame_max = forms.CharField(initial=FRAME_MAX_SIZE, widget=forms.TextInput(attrs={'style':'width:20%'}))
    heartbeat = forms.CharField(initial=1, widget=forms.TextInput(attrs={'style':'width:10%'}))

    def __repr__(self):
        return make_repr(self)

class EditForm(CreateForm):
    pass
