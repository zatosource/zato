# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Django
from django import forms

# Zato
from zato.admin.web.forms import INITIAL_CHOICES

class NForm(forms.Form):
    n = forms.IntegerField(widget=forms.TextInput(attrs={'style':'width:30px', 'id':'n'}))

class CompareForm(forms.Form):
    compare_to = forms.ChoiceField(widget=forms.Select(attrs={'id':'shift'}))

    def __init__(self, compare_to=None, *args, **kwargs):
        compare_to = compare_to or []
        super(CompareForm, self).__init__(*args, **kwargs)
        for name, value in self.fields.items():
            if isinstance(value, forms.ChoiceField):
                self.fields[name].choices = [INITIAL_CHOICES]

        for name, label in compare_to:
            self.fields['compare_to'].choices.append([name, label])

        self.fields['compare_to'].choices.append(['custom', 'Choose a time span ..'])

class SettingsForm(forms.Form):
    """ Various statistics settings.
    """
    scheduler_raw_times_interval = forms.CharField(widget=forms.TextInput(attrs={'style':'width:20%'}))
    scheduler_raw_times_batch = forms.CharField(widget=forms.TextInput(attrs={'style':'width:20%'}))
    scheduler_per_minute_aggr_interval = forms.CharField(widget=forms.TextInput(attrs={'style':'width:20%'}))

    atttention_slow_threshold = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100px'}))
    atttention_top_threshold = forms.CharField(widget=forms.TextInput(attrs={'style':'width:100px'}))

class MaintenanceForm(forms.Form):
    """ Statistics maintenance.
    """
    start = forms.CharField(widget=forms.TextInput(attrs={'class':'required', 'style':'width:150px; height:19px'}))
    stop = forms.CharField(widget=forms.TextInput(attrs={'class':'required', 'style':'width:150px; height:19px'}))
