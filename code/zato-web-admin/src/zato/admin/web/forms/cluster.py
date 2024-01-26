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

# We let the user delete a cluster only if the answer on the form is equal to the
# one given below.
OK_TO_DELETE = 'GO AHEAD'

class EditClusterForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={'class':'required', 'style':'width:100%'}))
    description = forms.CharField(widget=forms.Textarea(), required=False)

    lb_host = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    lb_port = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))
    lb_agent_port = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100%'}))

    def __repr__(self):
        return make_repr(self)

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
    old_name = forms.CharField(widget=forms.HiddenInput(attrs={'class':'required'}))
