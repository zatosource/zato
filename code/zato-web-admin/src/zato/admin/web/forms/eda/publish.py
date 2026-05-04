# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from django import forms

class PublishForm(forms.Form):

    topic_name = forms.CharField(widget=forms.Select(attrs={
        'class': 'required',
        'style': 'width:100%',
    }))

    data = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'required',
        'style': 'width:100%; height:200px; font-family:monospace; font-size:13px',
    }))

    priority = forms.ChoiceField(
        choices=[(str(i), str(i)) for i in range(1, 10)],
        initial='5',
    )

    expiration = forms.IntegerField(
        initial=86400,
        widget=forms.NumberInput(attrs={'style': 'width:120px'}),
    )
