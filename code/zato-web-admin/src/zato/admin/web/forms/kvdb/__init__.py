# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Django
from django import forms

# Zato
from zato.common.api import REDIS

# ################################################################################################################################
# ################################################################################################################################

class CreateForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={'style':'width:30%'}))
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'checked':'checked'}))
    host = forms.CharField(widget=forms.TextInput(attrs={'style':'width:50%'}))
    port = forms.CharField(initial=REDIS.DEFAULT.PORT, widget=forms.TextInput(attrs={'style':'width:15%'}))
    db = forms.CharField(initial=REDIS.DEFAULT.DB, widget=forms.TextInput(attrs={'style':'width:8%'}))
    use_redis_sentinels = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    redis_sentinels_master = forms.CharField(widget=forms.TextInput(attrs={'style':'width:71%'}))
    redis_sentinels = forms.CharField(widget=forms.Textarea(attrs={'style':'width:100%'}))

    def __init__(self, prefix=None, post_data=None):
        super(CreateForm, self).__init__(post_data, prefix=prefix)

# ################################################################################################################################
# ################################################################################################################################

class EditForm(CreateForm):
    is_active = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    use_redis_sentinels = forms.BooleanField(required=False, widget=forms.CheckboxInput())

# ################################################################################################################################
# ################################################################################################################################

class RemoteCommandForm(forms.Form):
    """ Form to send Redis commands through.
    """
    command = forms.CharField(widget=forms.Textarea(attrs={'style':'overflow:auto; width:100%; white-space: pre-wrap;height:80px'}))
    result = forms.CharField(widget=forms.Textarea(attrs={'style':'overflow:auto; width:100%; white-space: pre-wrap;height:400px'}))

    def __init__(self, initial=None):
        initial = initial or {}
        super(RemoteCommandForm, self).__init__(initial=initial)

# ################################################################################################################################
# ################################################################################################################################

# ################################################################################################################################
# ################################################################################################################################
