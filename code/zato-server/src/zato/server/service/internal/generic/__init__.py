# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.server.service.internal import AdminService

# ################################################################################################################################

class _BaseService(AdminService):
    def _get_instance(self, session, model_class, id):
        return session.query(model_class).\
               filter(model_class.id==id).\
               one()

# ################################################################################################################################
