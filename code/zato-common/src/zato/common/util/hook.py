# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Zato
from zato.common.util.api import is_func_overridden

# ################################################################################################################################

class HookTool(object):
    def __init__(self, server, hook_ctx_class, hook_type_to_method, invoke_func):
        self.server = server
        self.hook_ctx_class = hook_ctx_class
        self.hook_type_to_method = hook_type_to_method
        self.invoke_func = invoke_func

# ################################################################################################################################

    def is_hook_overridden(self, service_name, hook_type):
        impl_name = self.server.service_store.name_to_impl_name[service_name]
        service_class = self.server.service_store.service_data(impl_name)['service_class']
        func_name = self.hook_type_to_method[hook_type]
        func = getattr(service_class, func_name)

        return is_func_overridden(func)

# ################################################################################################################################

    def get_hook_service_invoker(self, service_name, hook_type):
        """ Returns a function that will invoke ooks or None if a given service does not implement input hook_type.
        """
        # Do not continue if we already know that user did not override the hook method
        if not self.is_hook_overridden(service_name, hook_type):
            return

        def _invoke_hook_service(*args, **kwargs):
            """ A function to invoke hook services.
            """
            ctx = self.hook_ctx_class(hook_type, *args, **kwargs)
            return self.invoke_func(service_name, {'ctx':ctx}, serialize=False).getvalue(serialize=False)['response']

        return _invoke_hook_service

# ################################################################################################################################
