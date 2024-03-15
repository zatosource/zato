# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Django
from django import forms

# Zato
from zato.admin.web.forms import add_select, WithTLSForm
from zato.common.api import LDAP

class CreateForm(WithTLSForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))

    get_info = forms.ChoiceField(widget=forms.Select(), initial=LDAP.GET_INFO.SCHEMA.id)
    ip_mode = forms.ChoiceField(widget=forms.Select())

    connect_timeout = forms.CharField(widget=forms.TextInput(attrs={'style':'width:9%'}), initial=LDAP.DEFAULT.CONNECT_TIMEOUT)
    auto_bind = forms.ChoiceField(widget=forms.Select(), initial=LDAP.AUTO_BIND.DEFAULT)

    server_list = forms.CharField(
        widget=forms.Textarea(attrs={'style':'width:100%; height:30px'}), initial=LDAP.DEFAULT.Server_List)

    pool_name = forms.CharField(widget=forms.TextInput(attrs={'style':'width:29%'}))
    pool_size = forms.CharField(widget=forms.TextInput(attrs={'style':'width:9%'}), initial=LDAP.DEFAULT.POOL_SIZE)
    pool_exhaust_timeout = forms.CharField(
        widget=forms.TextInput(attrs={'style':'width:9%'}), initial=LDAP.DEFAULT.POOL_EXHAUST_TIMEOUT)
    pool_keep_alive = forms.CharField(widget=forms.TextInput(attrs={'style':'width:9%'}), initial=LDAP.DEFAULT.POOL_KEEP_ALIVE)
    pool_max_cycles = forms.CharField(widget=forms.TextInput(attrs={'style':'width:9%'}), initial=LDAP.DEFAULT.POOL_MAX_CYCLES)
    pool_lifetime = forms.CharField(widget=forms.TextInput(attrs={'style':'width:9%'}), initial=LDAP.DEFAULT.POOL_LIFETIME)
    pool_ha_strategy = forms.ChoiceField(widget=forms.Select(), initial=LDAP.POOL_HA_STRATEGY.ROUND_ROBIN.id)

    username = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}), initial=LDAP.DEFAULT.Username)

    auth_type = forms.ChoiceField(widget=forms.Select())
    sasl_mechanism = forms.ChoiceField(widget=forms.Select())

    is_read_only = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    is_stats_enabled = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    should_check_names = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    use_auto_range = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    should_return_empty_attrs = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))

    def __init__(self, *args, **kwargs):
        super(CreateForm, self).__init__(*args, **kwargs)

        add_select(self, 'get_info', LDAP.GET_INFO(), needs_initial_select=False)
        add_select(self, 'ip_mode', LDAP.IP_MODE(), needs_initial_select=False)
        add_select(self, 'auto_bind', LDAP.AUTO_BIND(), needs_initial_select=False)
        add_select(self, 'pool_ha_strategy', LDAP.POOL_HA_STRATEGY(), needs_initial_select=False)
        add_select(self, 'auth_type', LDAP.AUTH_TYPE(), needs_initial_select=False)
        add_select(self, 'sasl_mechanism', LDAP.SASL_MECHANISM(), needs_initial_select=True)

class EditForm(CreateForm):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    use_sasl_external = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    use_auto_range = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    should_return_empty_attrs = forms.BooleanField(required=False, widget=forms.CheckboxInput())
