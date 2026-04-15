# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Django
from django import forms

# Zato
from zato.admin.web.forms import add_services

class _Base(forms.Form):
    id = forms.CharField(widget=forms.HiddenInput())
    name = forms.CharField(widget=forms.TextInput(attrs={'class':'required', 'style':'width:100%'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    service = forms.ChoiceField(widget=forms.Select(attrs={'class':'required', 'style':'width:100%'}))
    extra = forms.CharField(widget=forms.Textarea(attrs={'style':'width:100%'}))
    start_date = forms.CharField(widget=forms.TextInput(attrs={'class':'required', 'style':'width:30%; height:19px'}))

    def __init__(self, prefix, req):
        super(_Base, self).__init__(prefix=prefix)
        add_services(self, req, should_include_scheduler=True)

class OneTimeSchedulerJobForm(_Base):
    pass

_tz_choices = [('', '--- Same as server ---')] + sorted([
    ('Africa/Cairo', 'Africa/Cairo'),
    ('Africa/Johannesburg', 'Africa/Johannesburg'),
    ('Africa/Lagos', 'Africa/Lagos'),
    ('America/Argentina/Buenos_Aires', 'America/Argentina/Buenos_Aires'),
    ('America/Mexico_City', 'America/Mexico_City'),
    ('America/Sao_Paulo', 'America/Sao_Paulo'),
    ('Europe/Reykjavik', 'Europe/Reykjavik (Atlantic/Reykjavik)'),
    ('Asia/Bangkok', 'Asia/Bangkok'),
    ('Asia/Dubai', 'Asia/Dubai'),
    ('Asia/Hong_Kong', 'Asia/Hong_Kong'),
    ('Asia/Kolkata', 'Asia/Kolkata'),
    ('Asia/Seoul', 'Asia/Seoul'),
    ('Asia/Singapore', 'Asia/Singapore'),
    ('Asia/Tokyo', 'Asia/Tokyo'),
    ('Australia/Melbourne', 'Australia/Melbourne'),
    ('Australia/Perth', 'Australia/Perth'),
    ('Australia/Sydney', 'Australia/Sydney'),
    ('Canada/Central', 'Canada/Central'),
    ('Canada/Eastern', 'Canada/Eastern'),
    ('Canada/Pacific', 'Canada/Pacific'),
    ('Europe/Amsterdam', 'Europe/Amsterdam'),
    ('Europe/Athens', 'Europe/Athens'),
    ('Europe/Berlin', 'Europe/Berlin'),
    ('Europe/Brussels', 'Europe/Brussels'),
    ('Europe/Bucharest', 'Europe/Bucharest'),
    ('Europe/Helsinki', 'Europe/Helsinki'),
    ('Europe/Istanbul', 'Europe/Istanbul'),
    ('Europe/London', 'Europe/London'),
    ('Europe/Madrid', 'Europe/Madrid'),
    ('Europe/Oslo', 'Europe/Oslo'),
    ('Europe/Paris', 'Europe/Paris'),
    ('Europe/Prague', 'Europe/Prague'),
    ('Europe/Rome', 'Europe/Rome'),
    ('Europe/Stockholm', 'Europe/Stockholm'),
    ('Europe/Vienna', 'Europe/Vienna'),
    ('Europe/Warsaw', 'Europe/Warsaw'),
    ('Europe/Zurich', 'Europe/Zurich'),
    ('Pacific/Auckland', 'Pacific/Auckland'),
    ('US/Alaska', 'US/Alaska'),
    ('US/Central', 'US/Central'),
    ('US/Eastern', 'US/Eastern'),
    ('US/Hawaii', 'US/Hawaii'),
    ('US/Mountain', 'US/Mountain'),
    ('US/Pacific', 'US/Pacific'),
    ('UTC', 'UTC'),
], key=lambda x: x[1])

class IntervalBasedSchedulerJobForm(_Base):
    weeks = forms.CharField(widget=forms.TextInput(attrs={'class':'validate-digits', 'style':'width:8%'}))
    days = forms.CharField(widget=forms.TextInput(attrs={'class':'validate-digits', 'style':'width:8%'}))
    hours = forms.CharField(widget=forms.TextInput(attrs={'class':'validate-digits', 'style':'width:8%'}))
    minutes = forms.CharField(widget=forms.TextInput(attrs={'class':'validate-digits', 'style':'width:8%'}))
    seconds = forms.CharField(widget=forms.TextInput(attrs={'class':'validate-digits', 'style':'width:8%'}))
    start_date = forms.CharField(widget=forms.TextInput(attrs={'class':'required', 'style':'width:30%; height:19px'}))
    repeats = forms.CharField(widget=forms.TextInput(attrs={'style':'width:8%'}))
    jitter_ms = forms.CharField(required=False, initial='500', widget=forms.TextInput(attrs={'class':'validate-digits', 'style':'width:12%'}))
    timezone = forms.ChoiceField(required=False, choices=_tz_choices, widget=forms.Select(attrs={'style':'width:100%'}))
    on_missed = forms.ChoiceField(required=False, choices=[
        ('run_once', 'Run once'), ('skip', 'Skip'), ('run_all', 'Run all')
    ], widget=forms.Select(attrs={'style':'width:20%'}))
    max_execution_time_ms = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class':'validate-digits', 'style':'width:40%'}))
