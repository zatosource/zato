# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

This file is a proprietary product, not an open-source one.
"""

# stdlib
import logging
from http.client import BAD_GATEWAY, INTERNAL_SERVER_ERROR, NOT_FOUND, UNAUTHORIZED

# Django
from django.http import FileResponse, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt

# PyYAML
import yaml

# Zato
from zato.common.typing_ import cast_
from zato.common.webapp.auth.session_tokens import Session_Credentials_Key, decrypt_credentials, encrypt_credentials
from zato.openapi.console.branding import Branding_Files, get_branding_context, get_branding_file_path
from zato.openapi.console.client import OpenAPIConsoleClient

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict
    anydict = anydict

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

# The base URL under which try-it requests are relayed to the servers - the document's servers
# entry points here, so the browser only ever talks to the console, never to the servers.
_relay_url_base = '/openapi/console/relay'

# Maps rejection statuses from the reply stream to the HTTP status and message the browser receives
_relay_rejections = {
    'unauthorized': (UNAUTHORIZED, _unauthorized_message),
    'not_found': (NOT_FOUND, 'Not found'),
    'error': (INTERNAL_SERVER_ERROR, 'The invocation could not be completed'),
}

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

def _is_signed_in(req):
    """ Whether the session already has the caller's credentials.
    """
    out = Session_Credentials_Key in req.session
    return out

# ################################################################################################################################

def login_view(req):
    """ Renders the sign-in page and handles sign-in attempts. Credentials are validated by a Zato server
    and, once accepted, stored encrypted in the session cookie.
    """
    # Someone whose session already has credentials has nothing to do on the sign-in page
    if _is_signed_in(req):
        return redirect('console')

    context = get_branding_context()

    if req.method == 'POST':
        username = req.POST['username']
        password = req.POST['password']

        # Ask a server to validate the credentials by building the caller's document ..
        client = _get_client()
        spec = client.get_spec({
            'username': username,
            'password': password,
        })

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
    if not _is_signed_in(req):
        return redirect('login')

    context = get_branding_context()

    out = render(req, 'console.html', context)

    return out

# ################################################################################################################################

def _get_auth_or_error(req):
    """ Returns the signed-in caller's auth details and no error, or no details and an error response
    when there is no valid session. The details are the credentials the person signed in with.
    """
    # No session at all is unauthorized ..
    if not (token := req.session.get(Session_Credentials_Key)):
        return None, HttpResponse(_unauthorized_message, status=UNAUTHORIZED)

    # .. the token becomes invalid when the console is restarted, in which case the user signs in again ..
    credentials = decrypt_credentials(token)
    if not credentials:
        req.session.flush()
        return None, HttpResponse(_unauthorized_message, status=UNAUTHORIZED)

    username, password = credentials

    # .. and the session has what the person typed at the sign-in form.
    auth = {
        'username': username,
        'password': password,
    }
    return auth, None

# ################################################################################################################################

def _get_spec_or_error(req):
    """ Returns the signed-in caller's filtered document and no error, or no document and an error response
    when the session or the credentials are not valid.
    """
    auth, error = _get_auth_or_error(req)
    if error:
        return None, error

    # No error means the auth details are there, hence the cast
    auth = cast_('anydict', auth)

    client = _get_client()
    spec = client.get_spec(auth)

    if spec is None:
        return None, HttpResponse(_unauthorized_message, status=UNAUTHORIZED)

    # Try-it requests go through the console's relay, never directly to the servers
    spec['servers'] = [{'url': _relay_url_base}]

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

@csrf_exempt
def relay_view(req, relay_path):
    """ Relays a try-it invocation to the servers over Redis Streams and returns the response,
    so the browser only ever talks to the console. The target service is invoked with the signed-in
    user's own credentials and only if those credentials give access to the endpoint.
    """
    auth, error = _get_auth_or_error(req)
    if error:
        return error

    # No error means the auth details are there, hence the cast
    auth = cast_('anydict', auth)

    # The relay path arrives without its leading slash, which channels always have
    url_path = '/' + relay_path

    body = req.body.decode('utf-8')
    query_string = req.META['QUERY_STRING']

    client = _get_client()
    reply = client.invoke(auth, req.method, url_path, query_string, body)

    # No reply means no server was available in time
    if reply is None:
        return HttpResponse(_no_server_message, status=BAD_GATEWAY)

    status = reply['status']

    # A successful invocation passes the service's response through ..
    if status == 'ok':
        http_status = int(reply['http_status'])
        out = HttpResponse(reply['data'], status=http_status, content_type=reply['content_type'])

    # .. anything else maps to one of the known rejections.
    else:
        http_status, message = _relay_rejections[status]
        out = HttpResponse(message, status=http_status)

    return out

# ################################################################################################################################

def favicon_view(req):
    """ Answers the icon request browsers make at the root path on their own, with whichever
    icon the console is branded with.
    """
    branding = get_branding_context()
    out = redirect(branding['favicon_url'])
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
# ################################################################################################################################
