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

# stdlib
from operator import itemgetter

# Zato
from zato.common.util.api import needs_suffix
from zato.server.service import List, Service

# ################################################################################################################################
# ################################################################################################################################

# ################################################################################################################################
# ################################################################################################################################

class ServiceIDE(Service):
    name = 'dev.service.ide'

    input = '-service_name'
    output = '-service_source', List('file_list'), 'file_count', 'service_count', 'file_count_human', 'service_count_human', \
        List('service_list')

    def handle(self):

        # Default data structures to fill out with details
        service_source = None
        file_item_dict = {}
        service_list = []

        service_list_response = self.invoke('zato.service.get-deployment-info-list', **{
            'needs_details': False,
            'include_internal': False,
            'skip_response_elem': True,
        })

        # The file_item_dict dictionary maps file system locations to file names which means that keys
        # are always unique (because FS locations are always unique).
        for item in service_list_response:
            fs_location = item['fs_location']
            file_name = item['file_name']
            file_item_dict[fs_location] = file_name

            # Appending to our list of services is something that we can always do
            service_list.append({
                'name': item['service_name'],
                'fs_location': fs_location,
            })

        # This list may have file names that are not unique
        # but their FS locations will be always unique.
        file_list = []

        for fs_location, file_name in file_item_dict.items():
            file_list.append({
                'name': file_name,
                'fs_location': fs_location
            })

        file_count = len(file_list)
        service_count = len(service_list)

        file_list_suffix = 's' if needs_suffix(file_count) else ''
        service_list_suffix = 's' if needs_suffix(service_count) else ''

        file_count_human = f'{file_count} file{file_list_suffix}'
        service_count_human = f'{service_count} service{service_list_suffix}'

        response = {
            'service_source': service_source,
            'service_list': sorted(service_list, key=itemgetter('name')),
            'file_list': sorted(file_list, key=itemgetter('name')),
            'file_count': file_count,
            'service_count': service_count,
            'file_count_human': file_count_human,
            'service_count_human': service_count_human,
        }

        self.response.payload = response

# ################################################################################################################################
# ################################################################################################################################
'''
