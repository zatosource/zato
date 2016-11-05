# -*- coding: utf-8 -*-

"""
Copyright (C) 2016, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# TextBlob
from textblob import TextBlob

def match_pattern(text, pattern):
    """ Returns True if every element in pattern is contained in words extracted ouf of text,
    pattern is assumed to be lower-cased.
    """
    return set(pattern) <= set(elem.lower() for elem in TextBlob(text).words)
