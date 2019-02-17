# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.server.service.internal import AdminService

# ################################################################################################################################

class _BaseService(AdminService):

# ################################################################################################################################

    def _get_instance_by_id(self, session, model_class, id):
        return session.query(model_class).\
               filter(model_class.id==id).\
               one()

# ################################################################################################################################

    def _get_instance_by_name(self, session, model_class, type_, name):
        return session.query(model_class).\
               filter(model_class.type_==type_).\
               filter(model_class.name==name).\
               one()

# ################################################################################################################################
