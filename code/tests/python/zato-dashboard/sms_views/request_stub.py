# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The request a Dashboard view is called with directly - the form data the browser posts and the client
# the Dashboard's middleware builds.

# Django
from django.http import QueryDict

# Zato
from zato.client import ZatoClient
from zato.common.const import ServiceConst
from zato.common.ext.bunch import Bunch

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict

# ################################################################################################################################
# ################################################################################################################################

# The cluster ID
Cluster_Id = 1

# The user of the server's admin.invoke channel
Admin_Invoke_Username = 'admin.invoke'

# ################################################################################################################################
# ################################################################################################################################

def new_client(server_address:'str', password:'str') -> 'ZatoClient':
    """ The client a view invokes services through.
    """
    auth = (Admin_Invoke_Username, password)
    out = ZatoClient(server_address, ServiceConst.API_Invoke_Url_Path, auth, to_bunch=True)
    return out

# ################################################################################################################################

def new_request(
    client:'ZatoClient',
    post_data:'stranydict | None'=None,
    get_data:'stranydict | None'=None,
    method:'str'='POST',
    id:'str'='',
    ) -> 'any_':
    """ Builds the request of a view - the posted form data, the query string and the client of the session's server.
    """
    post = QueryDict('', mutable=True)

    if post_data:
        for key, value in post_data.items():
            post[key] = value

    get = QueryDict('', mutable=True)

    if get_data:
        for key, value in get_data.items():
            get[key] = value

    out = Bunch()

    out.method = method
    out.POST = post
    out.GET = get

    out.zato = Bunch()
    out.zato.args = {}
    out.zato.id = id
    out.zato.cluster_id = Cluster_Id
    out.zato.cluster = Bunch()
    out.zato.cluster.id = Cluster_Id
    out.zato.clusters = []
    out.zato.search_form = None
    out.zato.client = client

    return out

# ################################################################################################################################
# ################################################################################################################################
