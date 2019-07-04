# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Django
from django import forms

# Zato
from zato.common import CLOUD

class CreateForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    auth_version = forms.CharField(
        initial=CLOUD.OPENSTACK.SWIFT.DEFAULTS.AUTH_VERSION, widget=forms.TextInput(attrs={'style':'width:100%'}))
    pool_size = forms.CharField(
        initial=CLOUD.OPENSTACK.SWIFT.DEFAULTS.POOL_SIZE, widget=forms.TextInput(attrs={'style':'width:20%'}))
    auth_url = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    user = forms.CharField(widget=forms.TextInput(attrs={'style':'width:50%'}))
    tenant_name = forms.CharField(widget=forms.TextInput(attrs={'style':'width:50%'}))
    key = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    retries = forms.CharField(
        initial=CLOUD.OPENSTACK.SWIFT.DEFAULTS.RETRIES, widget=forms.TextInput(attrs={'style':'width:100%'}))
    starting_backoff = forms.CharField(
        initial=CLOUD.OPENSTACK.SWIFT.DEFAULTS.BACKOFF_STARTING, widget=forms.TextInput(attrs={'style':'width:100%'}))
    max_backoff = forms.CharField(
        initial=CLOUD.OPENSTACK.SWIFT.DEFAULTS.BACKOFF_MAX, widget=forms.TextInput(attrs={'style':'width:20%'}))
    should_validate_cert = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    cacert = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    should_retr_ratelimit = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    needs_tls_compr = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    is_snet = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    custom_options = forms.CharField(widget=forms.Textarea(attrs={'style':'width:100%'}))

    def __init__(self, prefix=None, post_data=None):
        super(CreateForm, self).__init__(post_data, prefix=prefix)

class EditForm(CreateForm):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    should_validate_cert = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    needs_tls_compr = forms.BooleanField(required=False, widget=forms.CheckboxInput())
