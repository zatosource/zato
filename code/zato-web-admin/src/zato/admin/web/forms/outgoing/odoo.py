# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Django
from django import forms

# Zato
from zato.common.api import ODOO

class CreateForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    host = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    port = forms.CharField(initial=ODOO.DEFAULT.PORT, widget=forms.TextInput(attrs={'style':'width:10%'}))
    user = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    database = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    protocol = forms.ChoiceField(widget=forms.Select())
    pool_size = forms.CharField(initial=ODOO.DEFAULT.POOL_SIZE, widget=forms.TextInput(attrs={'style':'width:10%'}))

    def __init__(self, prefix=None, post_data=None):
        super(CreateForm, self).__init__(post_data, prefix=prefix)

        self.fields['protocol'].choices = []
        for item in ODOO.PROTOCOL():
            self.fields['protocol'].choices.append([item.id, item.name])

class EditForm(CreateForm):
    pass
