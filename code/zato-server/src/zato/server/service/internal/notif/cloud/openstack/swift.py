# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.server.service.internal import AdminService

class GetList(AdminService):
    def handle(self):
        self.response.payload = '[]'

class _CreateEdit(AdminService):
    pass

class Create(AdminService):
    pass

class Edit(AdminService):
    pass

class Delete(AdminService):
    pass

class RunNotifier(AdminService):
    pass
