# -*- coding: utf-8 -*-

"""
Copyright (C) 2012 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

from django import template

register = template.Library()

# Taken from http://djangosnippets.org/snippets/38/ and slightly updated

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
