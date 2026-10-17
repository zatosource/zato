# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The services of the OpenAPI console suite - a case management API whose REST channels the console documents.
# The server deploys this module at startup from the hot-deployment directory the suite points it at.

# Zato
from zato.server.service import Service

# ################################################################################################################################
# ################################################################################################################################

class CreateCase(Service):
    """ Opens a new case for a customer.
    """
    name = 'api.cases.create'
    input = 'customer_name', 'description'
    output = 'case_id'

    def handle(self) -> 'None':
        self.response.payload.case_id = 'case-1'

# ################################################################################################################################
# ################################################################################################################################

class UpdateCase(Service):
    """ Changes the description of an existing case.
    """
    name = 'api.cases.update'
    input = 'case_id', '-description'
    output = 'case_id'

    def handle(self) -> 'None':
        self.response.payload.case_id = self.request.input.case_id

# ################################################################################################################################
# ################################################################################################################################

class GetCase(Service):
    """ Returns one case.
    """
    name = 'api.cases.get'
    input = 'case_id'
    output = 'case_id', 'customer_name'

    def handle_GET(self) -> 'None':
        self.response.payload.case_id = self.request.input.case_id
        self.response.payload.customer_name = 'John Smith'

# ################################################################################################################################
# ################################################################################################################################
