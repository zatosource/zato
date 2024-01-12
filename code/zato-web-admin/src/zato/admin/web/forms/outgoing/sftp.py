# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Django
from django import forms

# Zato
from zato.common.api import SFTP
from zato.admin.web.forms import add_select

# ################################################################################################################################
# ################################################################################################################################

class CreateForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    log_level = forms.ChoiceField(widget=forms.Select())

    host = forms.CharField(widget=forms.TextInput(attrs={'style':'width:70%'}))
    port = forms.CharField(widget=forms.TextInput(attrs={'style':'width:12%'}), initial=SFTP.DEFAULT.PORT)

    username = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    password = forms.CharField(widget=forms.TextInput(attrs={'style':'width:50%'}))
    identity_file = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    ssh_config_file = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))

    sftp_command = forms.CharField(widget=forms.TextInput(attrs={'style':'width:40%'}), initial=SFTP.DEFAULT.COMMAND_SFTP)
    ping_command = forms.CharField(widget=forms.TextInput(attrs={'style':'width:37%'}), initial=SFTP.DEFAULT.COMMAND_PING)

    buffer_size = forms.CharField(widget=forms.TextInput(attrs={'style':'width:12%'}), initial=SFTP.DEFAULT.BUFFER_SIZE)
    is_compression_enabled = forms.ChoiceField(widget=forms.Select())
    bandwidth_limit = forms.CharField(widget=forms.TextInput(attrs={'style':'width:10%'}), initial=SFTP.DEFAULT.BANDWIDTH_LIMIT)

    force_ip_type = forms.ChoiceField(widget=forms.Select())
    should_flush = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    should_preserve_meta = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))

    default_directory = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    ssh_options = forms.CharField(widget=forms.Textarea(attrs={'style':'width:100%'}))

    def __init__(self, prefix=None, req=None):
        super(CreateForm, self).__init__(prefix=prefix)
        add_select(self, 'log_level', SFTP.LOG_LEVEL(), needs_initial_select=False)
        add_select(self, 'force_ip_type', SFTP.IP_TYPE())

# ################################################################################################################################
# ################################################################################################################################

class EditForm(CreateForm):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())

# ################################################################################################################################
# ################################################################################################################################

class CommandShellForm(forms.Form):
    data = forms.CharField(widget=forms.Textarea(attrs={'style':'width:100%; height:70px'}), initial='ls .')
    stdout = forms.CharField(widget=forms.Textarea(attrs={'style':'width:100%; height:170px'}))
    stderr = forms.CharField(widget=forms.Textarea(attrs={'style':'width:100%; height:270px'}))
    log_level = forms.ChoiceField(widget=forms.Select())

    def __init__(self):
        super(CommandShellForm, self).__init__()
        add_select(self, 'log_level', SFTP.LOG_LEVEL(), needs_initial_select=False)

# ################################################################################################################################
# ################################################################################################################################
