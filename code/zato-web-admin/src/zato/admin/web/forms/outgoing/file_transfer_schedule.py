# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Django
from django import forms

# Zato
from zato.admin.web.forms import add_services
from zato.common.api import FileTransfer

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydictnone, strnone
    any_ = any_
    anydictnone = anydictnone
    strnone = strnone

# ################################################################################################################################
# ################################################################################################################################

_scheduler = FileTransfer.Scheduler

# What the wizard starts out with before the user changes anything.
_default_run_every = '5'
_default_run_unit  = _scheduler.Unit.Minutes

# ################################################################################################################################
# ################################################################################################################################

class CreateForm(forms.Form):

    # What to pick up
    name = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'e.g. invoices.hourly'}))
    is_active = forms.BooleanField(required=False, initial=True, widget=forms.CheckboxInput())
    directory = forms.CharField(widget=forms.TextInput(attrs={'placeholder':'/incoming/invoices'}))
    pattern = forms.CharField(initial=_scheduler.Default_Pattern, widget=forms.TextInput())

    # When is a file ready - the choice cards write the mode into the hidden field
    ready_how = forms.CharField(initial=_scheduler.ReadyHow.Stability, widget=forms.HiddenInput())
    stability_delay = forms.CharField(
        initial=_scheduler.Default_Stability_Delay, widget=forms.TextInput(attrs={'class':'validate-digits'}))
    marker_suffix = forms.CharField(initial=_scheduler.Default_Marker_Suffix, widget=forms.TextInput())

    # Competing consumers
    should_claim = forms.BooleanField(required=False, widget=forms.CheckboxInput())

    # What happens next
    scheduler_service = forms.ChoiceField(widget=forms.Select())
    on_success = forms.CharField(initial=_scheduler.OnSuccess.Move, widget=forms.HiddenInput())
    move_directory = forms.CharField(initial=_scheduler.Default_Move_Directory, widget=forms.TextInput())

    # How often to look
    run_every = forms.CharField(initial=_default_run_every, widget=forms.TextInput(attrs={'class':'validate-digits'}))
    run_unit = forms.ChoiceField(initial=_default_run_unit, widget=forms.Select())
    start_date = forms.CharField(widget=forms.TextInput())

    def __init__(self, prefix:'strnone'=None, post_data:'anydictnone'=None, req:'any_'=None) -> 'None':
        super().__init__(post_data, prefix=prefix)
        add_services(self, req)

        # One choice per interval unit the scheduler understands.
        choices = []
        for item in _scheduler.UnitList:
            choices.append([item, item])

        self.fields['run_unit'].choices = choices

# ################################################################################################################################
# ################################################################################################################################
