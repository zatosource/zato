# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Django
from django import forms

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

class CreateForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={'class':'required', 'style':'width:100%'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    url_path = forms.CharField(initial='/mcp/', widget=forms.TextInput(attrs={'class':'required', 'style':'width:100%'}))

    # Response shaping - the textarea is hidden, a syntax-highlighting editor pane
    # renders on top of it and the two are kept in sync by the page's JS.
    filter_expression = forms.CharField(required=False, widget=forms.Textarea(attrs={'style':'display:none'}))

    # Response safeguards - compaction
    safeguards_strip_nulls = forms.BooleanField(required=False)
    safeguards_collapse_whitespace = forms.BooleanField(required=False)
    safeguards_strip_base64 = forms.BooleanField(required=False)

    # Response safeguards - PII removal
    safeguards_pii_enabled = forms.BooleanField(required=False)
    safeguards_pii_lands = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'style':'width:100%', 'placeholder':'es, de, fr, us, intl'}))
    safeguards_pii_detectors = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'style':'width:100%', 'placeholder':'es_dni, intl_iban'}))
    safeguards_pii_exclude = forms.CharField(required=False, widget=forms.TextInput(attrs={'style':'width:100%'}))
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
