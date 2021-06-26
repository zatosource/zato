# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# Django
from django import template
from django.utils.safestring import mark_safe

# ################################################################################################################################

register = template.Library()

# ################################################################################################################################

# Taken from https://djangosnippets.org/snippets/38/ and slightly updated

@register.filter
def bunchget(obj, args):
    """ Try to get an attribute from an object.

    Example: {% if block|getattr:"editable,True" %}

    Beware that the default is always a string, if you want this
    to return False, pass an empty second argument:
    {% if block|getattr:"editable," %}
    """
    args = str(args).split(',')
    if len(args) == 1:
        (attribute, default) = [args[0], '']
    else:
        (attribute, default) = args

    if attribute in obj:
        return obj[attribute]

    return default

# ################################################################################################################################

# Taken from https://stackoverflow.com/a/16609498

@register.simple_tag
def url_replace(request, field, value):
    dict_ = request.GET.copy()
    dict_[field] = value

    return dict_.urlencode()

# ################################################################################################################################

@register.filter
def no_value_indicator(value):
    return value or mark_safe('<span class="form_hint">---</span>')

# ################################################################################################################################
