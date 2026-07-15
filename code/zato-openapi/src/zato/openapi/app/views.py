# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

This file is a proprietary product, not an open-source one.
"""

# stdlib
import logging
import os
from http.client import NOT_FOUND, UNAUTHORIZED

# Django
from django.conf import settings
from django.http import FileResponse, HttpResponse, JsonResponse
from django.shortcuts import redirect, render

# PyYAML
import yaml

# Zato
from zato.openapi.console.branding import Branding_Files, get_branding_context, get_branding_file_path
from zato.openapi.console.client import OpenAPIConsoleClient
from zato.openapi.console.session import Session_Credentials_Key, decrypt_credentials, encrypt_credentials

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# The message shown on the sign-in page when the credentials are rejected
_invalid_credentials_message = 'Invalid username or password'

# The message shown when no server replied in time
_no_server_message = 'No server is available, please try again'

# The one message returned to any caller without a valid session - always the same
# so that anonymous callers cannot tell apart missing, expired and rejected sessions.
_unauthorized_message = 'Unauthorized'

# Created lazily so that the console starts even when Redis is briefly unavailable
_client = None

# ################################################################################################################################
# ################################################################################################################################

def _get_client() -> 'OpenAPIConsoleClient':
    global _client
    if _client is None:
        _client = OpenAPIConsoleClient()

    return _client

# ################################################################################################################################

def login_view(req):
    """ Renders the sign-in page and handles sign-in attempts. Credentials are validated by a Zato server
    and, once accepted, stored encrypted in the session cookie.
    """
    context = get_branding_context()

    if req.method == 'POST':
        username = req.POST['username']
        password = req.POST['password']

        # Ask a server to validate the credentials by building the caller's document ..
        client = _get_client()
        spec = client.get_spec(username, password)

        # .. a document means the credentials are valid and the session can be established ..
        if spec is not None:
            req.session[Session_Credentials_Key] = encrypt_credentials(username, password)
            return redirect('console')

        # .. otherwise, show the sign-in page again with an error message.
        context['error'] = _invalid_credentials_message

    return render(req, 'login.html', context)

# ################################################################################################################################

def logout_view(req):
    """ Ends the session and returns to the sign-in page.
    """
    req.session.flush()

    out = redirect('login')

    return out

# ################################################################################################################################

def console_view(req):
    """ Renders the console page - the actual document is loaded by the browser from the spec endpoint.
    """
    if Session_Credentials_Key not in req.session:
        return redirect('login')

    context = get_branding_context()

    out = render(req, 'console.html', context)

    return out

# ################################################################################################################################

def _get_spec_or_error(req):
    """ Returns the signed-in caller's filtered document and no error, or no document and an error response
    when the session or the credentials are not valid.
    """
    if not (token := req.session.get(Session_Credentials_Key)):
        return None, HttpResponse(_unauthorized_message, status=UNAUTHORIZED)

    # The token becomes invalid when the console is restarted, in which case the user signs in again
    credentials = decrypt_credentials(token)
    if not credentials:
        req.session.flush()
        return None, HttpResponse(_unauthorized_message, status=UNAUTHORIZED)

    username, password = credentials

    client = _get_client()
    spec = client.get_spec(username, password)

    if spec is None:
        return None, HttpResponse(_unauthorized_message, status=UNAUTHORIZED)

    return spec, None

# ################################################################################################################################

def spec_view(req):
    """ Serves the OpenAPI document filtered down to what the signed-in user's credentials give access to.
    The filtering happens on Zato servers - the document never contains endpoints the caller cannot invoke.
    """
    spec, error = _get_spec_or_error(req)
    if error:
        return error

    out = JsonResponse(spec)

    return out

# ################################################################################################################################

def spec_yaml_view(req):
    """ Serves the same per-caller filtered OpenAPI document as the JSON view, rendered as YAML.
    """
    spec, error = _get_spec_or_error(req)
    if error:
        return error

    document = yaml.dump(spec, sort_keys=False, allow_unicode=True)

    out = HttpResponse(document, content_type='application/yaml')

    return out

# ################################################################################################################################

def branding_view(req, file_name):
    """ Serves a user-provided branding file from the well-known branding directory.
    """
    full_path = get_branding_file_path(file_name)

    if not full_path:
        return HttpResponse('No such file', status=NOT_FOUND)

    content_type = Branding_Files[file_name]

    out = FileResponse(open(full_path, 'rb'), content_type=content_type)

    return out

# ################################################################################################################################

def static_view(req, file_path):
    """ Serves the console's own static files with explicit content types.
    """
    full_path = os.path.join(settings.STATICFILES_DIRS[0], file_path)

    if not os.path.exists(full_path):
        return HttpResponse('No such file', status=NOT_FOUND)

    extension = os.path.splitext(file_path)[1]
    content_type = settings.MIMETYPES[extension]

    out = FileResponse(open(full_path, 'rb'), content_type=content_type)

    return out

# ################################################################################################################################
# ################################################################################################################################
