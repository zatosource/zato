# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Django
from django import forms

class RemoteCommandForm(forms.Form):
    """ Form to directly interface the key/value DB.
    """
    command = forms.CharField(widget=forms.Textarea(attrs={'style':'overflow:auto; width:100%; white-space: pre-wrap;height:80px'}))
    result = forms.CharField(widget=forms.Textarea(attrs={'style':'overflow:auto; width:100%; white-space: pre-wrap;height:400px'}))

    def __init__(self, initial={}):
        super(RemoteCommandForm, self).__init__(initial=initial)
