# -*- coding: utf-8 -*-

"""
Copyright (C) 2016, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# TextBlob
from textblob import TextBlob

class PatternMatcher(object):
    """ Matches text against patterns and returns information whether all patterns were found in text.
    """
    def __init__(self, text):
        self.blob = TextBlob(text)

    def match(self, pattern):
        """ Returns True if every element in pattern is contained in self.blob.words,
        pattern is assumed to be lower-cased.
        """
        return set(pattern) <= set(elem.lower() for elem in self.blob.words)
