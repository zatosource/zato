# -*- coding: utf-8 -*-

"""
Copyright (C) 2011 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from ftplib import FTP_PORT

# Django
from django import forms

class CreateForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    host = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    port = forms.CharField(initial=FTP_PORT, widget=forms.TextInput(attrs={'style':'width:10%'}))
    user = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    acct = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    timeout = forms.CharField(widget=forms.TextInput(attrs={'style':'width:10%'}))
    dircache = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    use_ftps = forms.BooleanField(required=False, widget=forms.CheckboxInput())

    def __init__(self, prefix=None, post_data=None):
        super(CreateForm, self).__init__(post_data, prefix=prefix)

class EditForm(CreateForm):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    dircache = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    use_ftps = forms.BooleanField(required=False, widget=forms.CheckboxInput())
