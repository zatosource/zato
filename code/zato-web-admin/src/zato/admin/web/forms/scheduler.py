# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Django
from django import forms

# Zato
from zato.admin.web.common import tz_names
from zato.admin.web.forms import add_services

class _Base(forms.Form):
    id = forms.CharField(widget=forms.HiddenInput())
    name = forms.CharField(widget=forms.TextInput(attrs={'class':'required', 'style':'width:100%'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    service = forms.ChoiceField(widget=forms.Select(attrs={'class':'required', 'style':'width:100%'}))
    extra = forms.CharField(widget=forms.Textarea(attrs={'style':'width:100%'}))
    start_date = forms.CharField(widget=forms.TextInput(attrs={'class':'required', 'style':'width:30%; height:19px'}))
    on_success_service = forms.ChoiceField(required=False, widget=forms.Select(attrs={'style':'width:100%'}))
    on_success_job = forms.ChoiceField(required=False, widget=forms.Select(attrs={'style':'width:100%'}))
    on_error_service = forms.ChoiceField(required=False, widget=forms.Select(attrs={'style':'width:100%'}))
    on_error_job = forms.ChoiceField(required=False, widget=forms.Select(attrs={'style':'width:100%'}))

    def __init__(self, prefix, req):
        super(_Base, self).__init__(prefix=prefix)
        add_services(self, req, should_include_scheduler=True)
        self._populate_job_choices(req)

    def _populate_job_choices(self, req):
        """ Populates the on_success_job and on_error_job select fields with existing scheduler job names.
        """
        job_choices = [('', '------')]

        if req.zato.cluster_id:
            response = req.zato.client.invoke('zato.scheduler.job.get-list', {
                'cluster_id': req.zato.cluster_id,
                'paginate': False,
                'query': '',
            })

            for job_elem in response.data:
                job_choices.append([job_elem.name, job_elem.name])

        self.fields['on_success_job'].choices = job_choices
        self.fields['on_error_job'].choices = job_choices

class OneTimeSchedulerJobForm(_Base):
    pass

_tz_choices = [('', '--- Same as server ---')] + [(tz, tz) for tz in tz_names]

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
    max_execution_time_ms = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class':'validate-digits', 'style':'width:12%'}))
