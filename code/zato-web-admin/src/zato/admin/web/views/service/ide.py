# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Django
from django.template.response import TemplateResponse

# Zato
from zato.admin.web.views import BaseCallView

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class IDE(BaseCallView):
    method_allowed = 'GET'
    url_name = 'service-ide'
    template = 'zato/service/ide.html'
    service_name = 'dev.service.ide'

    def get_input_dict(self):
        return {
            'cluster_id': self.cluster_id
        }

# ################################################################################################################################

    def build_http_response(self, response):
        return_data = {
            'cluster_id':self.req.zato.cluster_id,
            'data': response.data.response
        }

        print()
        print(111, response.data)
        print()

        return TemplateResponse(self.req, self.template, return_data)

# ################################################################################################################################
# ################################################################################################################################

'''
# -*- coding: utf-8 -*-

# Zato
from zato.server.service import List, Service

# ################################################################################################################################
# ################################################################################################################################

# ################################################################################################################################
# ################################################################################################################################

class ServiceIDE(Service):
    name = 'dev.service.ide'

    input = '-service_name'
    output = '-service_source', List('file_name_list'), 'file_num', 'service_num', 'file_num_human', 'service_num_human'

    def handle(self):

        # Default data structures to fill out with details
        service_source = None
        file_name_list = set()
        file_num = 0
        service_num = 0
        file_num_human = '0 files'
        service_num_human = '0 services'

        service_list_kwargs = {
            'needs_details': False,
            'include_internal': False,
            'skip_response_elem': True,
        }
        service_list = self.invoke('zato.service.get-deployment-info-list', **service_list_kwargs)

        for item in service_list:
            #print()
            #print(111, item)
            #print()
            file_name_list.add(item['file_name'])

        response = {
            'service_source': service_source,
            'file_name_list': sorted(file_name_list),
            'file_num': file_num,
            'service_num': service_num,
            'file_num_human': file_num_human,
            'service_num_human': service_num_human,
        }

        self.response.payload = response

# ################################################################################################################################
# ################################################################################################################################
'''
