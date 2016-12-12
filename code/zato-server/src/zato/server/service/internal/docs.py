# -*- coding: utf-8 -*-

"""
Copyright (C) 2016, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Bunch
from bunch import bunchify

# docformatter
from docformatter import format_docstring, split_summary_and_description as split_docstring

# Zato
from zato.server.service import Service

# ################################################################################################################################

class Docstring(object):
    """ Details of a given service's docstring.
    """
    def __init__(self):
        self.summary = ''
        self.description = ''
        self.full = ''

# ################################################################################################################################

class ServiceInfo(object):
    """ Contains information about a service basing on which documentation is generated.
    """
    def __init__(self, name, service_class):
        self.name = name
        self.service_class = service_class
        self.docstring = Docstring()
        self.invokes = []
        self.invoked_by = []
        self.parse()

# ################################################################################################################################

    def parse(self):
        self.set_summary_desc()

# ################################################################################################################################

    def set_summary_desc(self):

        if not self.service_class.__doc__:
            return

        summary, _ = split_docstring(self.service_class.__doc__)

        # This gives us the full docstring out of which we need to extract description alone.
        full_docstring = format_docstring('', '"{}"'.format(self.service_class.__doc__), post_description_blank=False)
        description = full_docstring.lstrip('"""').rstrip('"""').splitlines()

        # If there are multiple lines and the second one is empty this means it is an indicator of a summary to follow.
        if len(description) > 1 and not description[1]:
            description = '\n'.join(description[2:])
        else:
            description = ''

        self.docstring.summary = summary.strip()
        self.docstring.description = description
        self.docstring.full = full_docstring

# ################################################################################################################################

class Generator(Service):
    """ Generates static documentation for Zato services.
    """
    def handle(self):
        for impl_name, details in self.server.service_store.services.iteritems():
            if not impl_name.startswith('zato'):
                details = bunchify(details)
                info = ServiceInfo(details['name'], details['service_class'])
                print(33, info.docstring.summary)
                print(33, info.docstring.description)

# ################################################################################################################################