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

class _Base(forms.Form):
    system1 = forms.ChoiceField()
    key1 = forms.ChoiceField()
    value1 = forms.ChoiceField()
    system2 = forms.ChoiceField()
    key2 = forms.ChoiceField()

    def __init__(self, systems=None, *args, **kwargs):
        systems = systems or []
        super(_Base, self).__init__(*args, **kwargs)
        for name, value in self.fields.items():
            if isinstance(value, forms.ChoiceField):
                self.fields[name].choices = [INITIAL_CHOICES]

        for system_id, system in systems:
            for name in('system1', 'system2'):
                self.fields[name].choices.append([system_id, system])

class CreateForm(_Base):
    value2 = forms.ChoiceField()

class EditForm(CreateForm):
    pass

class TranslateForm(_Base):
    pass
