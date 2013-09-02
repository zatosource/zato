# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Django
from django import forms

# Zato
from zato.common import SIMPLE_IO

INITIAL_CHOICES_DICT = {'': '----------'}
INITIAL_CHOICES = INITIAL_CHOICES_DICT.items()[0]

class ChooseClusterForm(forms.Form):

    cluster = forms.ChoiceField(widget=forms.Select())
    name_filter = forms.CharField(widget=forms.TextInput(
        attrs={'style':'width:30%', 'class':'required', 'placeholder':'Enter * or part of a service name, e.g. http soap'}))

    def __init__(self, clusters, data=None):
        super(ChooseClusterForm, self).__init__(data)
        self.fields['cluster'].choices = [INITIAL_CHOICES]
        for cluster in clusters:
            server_info = '{0} - http://{1}:{2}'.format(cluster.name, cluster.lb_host, cluster.lb_port)
            self.fields['cluster'].choices.append([cluster.id, server_info])

class ChangePasswordForm(forms.Form):
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class':'required'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class':'required validate-password-confirm'}))

class DataFormatForm(forms.Form):
    data_format = forms.ChoiceField(widget=forms.Select())
    
    def __init__(self, *args, **kwargs):
        super(DataFormatForm, self).__init__(*args, **kwargs)
        self.fields['data_format'].choices = []
        self.fields['data_format'].choices.append(INITIAL_CHOICES)
        for name in sorted(dir(SIMPLE_IO.FORMAT)):
            if name.upper() == name:
                self.fields['data_format'].choices.append([name.lower(), name])
                
class UploadForm(forms.Form):
    file = forms.FileField(widget=forms.FileInput(attrs={'size':'70'}))
