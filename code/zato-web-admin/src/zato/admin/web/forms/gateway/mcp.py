# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Django
from django import forms

# Zato
from zato.common.util.safeguards.names import get_detector_choices, get_land_choices

# ################################################################################################################################

_mode_choices = (
    ('clean', 'Clean'),
    ('reject', 'Reject'),
)

_url_mode_choices = (
    ('remove', 'Remove'),
    ('defang', 'Defang'),
    ('reject', 'Reject'),
)

_size_cap_mode_choices = (
    ('truncate', 'Truncate'),
    ('block', 'Block'),
)

# ################################################################################################################################

class CreateForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={'class':'required', 'style':'width:100%'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    url_path = forms.CharField(initial='/mcp/', widget=forms.TextInput(attrs={'class':'required', 'style':'width:100%'}))

    # Response shaping - the filter expression itself has no form field, an editor pane
    # holds it in the page and the page's JS injects it as a hidden input on submit.
    allow_client_filters = forms.BooleanField(required=False)
    max_response_size = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'style':'width:30%'}))
    size_cap_mode = forms.ChoiceField(choices=_size_cap_mode_choices)
    min_size_threshold = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'style':'width:30%'}))

    # Response safeguards - compaction
    safeguards_strip_nulls = forms.BooleanField(required=False)
    safeguards_collapse_whitespace = forms.BooleanField(required=False)
    safeguards_strip_base64 = forms.BooleanField(required=False)

    # Response safeguards - PII removal
    safeguards_pii_enabled = forms.BooleanField(required=False)
    safeguards_pii_lands = forms.MultipleChoiceField(required=False, choices=get_land_choices,
        widget=forms.SelectMultiple(attrs={'class':'chosen-multi', 'data-placeholder':'None selected'}))
    safeguards_pii_detectors = forms.MultipleChoiceField(required=False, choices=get_detector_choices,
        widget=forms.SelectMultiple(attrs={'class':'chosen-multi', 'data-placeholder':'None selected'}))
    safeguards_pii_exclude = forms.MultipleChoiceField(required=False, choices=get_detector_choices,
        widget=forms.SelectMultiple(attrs={'class':'chosen-multi', 'data-placeholder':'Nothing excluded'}))
    safeguards_pii_validate = forms.BooleanField(required=False)
    safeguards_pii_stable_tokens = forms.BooleanField(required=False)

    # Response safeguards - unicode
    safeguards_normalize_unicode = forms.BooleanField(required=False)
    safeguards_unicode_mode = forms.ChoiceField(choices=_mode_choices)

    # Response safeguards - markup
    safeguards_sanitize_markup = forms.BooleanField(required=False)
    safeguards_markup_mode = forms.ChoiceField(choices=_mode_choices)

    # Response safeguards - URL policy
    safeguards_url_policy_enabled = forms.BooleanField(required=False)
    safeguards_url_allow_list = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'style':'width:100%', 'placeholder':'example.com, api.example.com'}))
    safeguards_url_mode = forms.ChoiceField(choices=_url_mode_choices)

# ################################################################################################################################

class EditForm(CreateForm):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())

# ################################################################################################################################
