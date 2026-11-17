# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The services of the tests that run without a server are deployed as the service store of a server deploys them
# and built through their constructors.

# stdlib
import inspect

# Zato
from zato.server.service.store import ServiceStore

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_
    from zato.server.service import Service

    any_ = any_
    Service = Service

# ################################################################################################################################
# ################################################################################################################################

def deploy_service(class_:'type[Service]', server:'any_') -> 'any_':
    """ Returns an instance of a service class, deployed with the given server as the service store deploys it
    and built through its constructor.
    """
    store = ServiceStore(services={}, odb=server.odb, server=server, is_testing=False)

    # The names of the class are assigned as during a deployment ..
    _ = class_.zato_set_module_name(inspect.getfile(class_))
    _ = class_.get_name()
    _ = class_.get_impl_name()

    # .. and so are the attributes that all of its instances share.
    store.set_up_class_attributes(class_, store)

    out = class_()
    return out

# ################################################################################################################################
# ################################################################################################################################
