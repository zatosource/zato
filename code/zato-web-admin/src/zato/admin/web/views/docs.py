# -*- coding: utf-8 -*-

"""
Copyright (C) 2016, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Zato
from zato.admin.web.views import Index as _Index

class Index(_Index):
    method_allowed = 'GET'
    url_name = 'docs-index'
    template = 'zato/docs.html'
    service_name = 'zato.apispec.get-api-spec'

    class SimpleIO(_Index.SimpleIO):
        input_required = ('cluster_id',)
        input_optional = ('query',)
        output_required = ('spec',)

    def handle(self):
        return {
            'show_search_form':True
        }
