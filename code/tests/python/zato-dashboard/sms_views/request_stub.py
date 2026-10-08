# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# What a Dashboard view is called with when it is called directly against a live server - a request with the form
# the browser posts and the client the Dashboard's middleware builds, pointed at the server of the session.

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

# The one cluster everything in the Dashboard belongs to
Cluster_Id = 1

# The user the server's admin.invoke channel authenticates
Admin_Invoke_Username = 'admin.invoke'

# ################################################################################################################################
# ################################################################################################################################

def new_client(server_address:'str', password:'str') -> 'ZatoClient':
    """ The client a view invokes services through, as the middleware builds it.
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
    """ Builds the request a view is called with - its form filled in with what the browser would have posted,
    its query string with what the page's URL has and its client reaching the server of the session.
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
