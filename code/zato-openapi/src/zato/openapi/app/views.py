# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

This file is a proprietary product, not an open-source one.
"""

# stdlib
import logging
import os
from http.client import BAD_GATEWAY, INTERNAL_SERVER_ERROR, NOT_FOUND, UNAUTHORIZED

# Django
from django.conf import settings
from django.http import FileResponse, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt

# PyYAML
import yaml

# Zato
from zato.common.api import OpenAPI_Console_Auth
from zato.common.typing_ import cast_
from zato.openapi.console.branding import Branding_Files, get_branding_context, get_branding_file_path
from zato.openapi.console.client import OpenAPIConsoleClient
from zato.openapi.console.entra_auth import AuthType, complete_auth_code_flow, EntraAuthError, get_authorize_url, \
    is_entra_enabled
from zato.openapi.console.session import Session_Credentials_Key, Session_Entra_Key, decrypt_credentials, \
    decrypt_entra_identity, encrypt_credentials, encrypt_entra_identity

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

def login_view(req):
    """ Renders the sign-in page and handles sign-in attempts. Credentials are validated by a Zato server
    and, once accepted, stored encrypted in the session cookie. With Entra ID enabled, a GET may go
    straight to Microsoft instead, the same way the Dashboard's login view does it.
    """
    context = get_branding_context()
    context['entra_enabled'] = is_entra_enabled()

    if req.method == 'GET':

        # With Entra ID enabled, a GET goes to Microsoft when the person clicked the Microsoft button.
        # The auth=built-in query parameter always keeps the plain form reachable so that sign-ins
        # against security definitions keep working too - the two mechanisms coexist.
        if is_entra_enabled():
            if req.GET.get('auth') == AuthType.Entra:
                authorize_url = get_authorize_url(req, '/openapi/console')
                return redirect(authorize_url)

    if req.method == 'POST':
        username = req.POST['username']
        password = req.POST['password']

        # Ask a server to validate the credentials by building the caller's document ..
        client = _get_client()
        spec = client.get_spec({
            'auth_type': OpenAPI_Console_Auth.Type_Credentials,
            'username': username,
            'password': password,
            'is_admin': OpenAPI_Console_Auth.Is_Admin_False,
        })

        # .. a document means the credentials are valid and the session can be established ..
        if spec is not None:
            req.session[Session_Credentials_Key] = encrypt_credentials(username, password)
            return redirect('console')

        # .. otherwise, show the sign-in page again with an error message.
        context['error'] = _invalid_credentials_message

    return render(req, 'login.html', context)

# ################################################################################################################################

def login_callback_view(req):
    """ Completes an Entra ID sign-in - the identity confirmed by Microsoft is stored encrypted
    in the session cookie, admin rights following the Entra group membership.
    """
    context = get_branding_context()
    context['entra_enabled'] = is_entra_enabled()

    try:
        username, _display_name, is_admin, _next_path = complete_auth_code_flow(req)
    except EntraAuthError as e:
        logger.warning('Entra ID sign-in error -> `%s`', e.args[0])
        context['error'] = e.args[0]
        return render(req, 'login.html', context)

    req.session[Session_Entra_Key] = encrypt_entra_identity(username, is_admin)

    logger.info('User `%s` signed in to the console through Entra ID (is_admin=%s)', username, is_admin)

    return redirect('console')

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
        if Session_Entra_Key not in req.session:
            return redirect('login')

    context = get_branding_context()

    out = render(req, 'console.html', context)

    return out

# ################################################################################################################################

def _get_auth_or_error(req):
    """ Returns the signed-in caller's auth details and no error, or no details and an error response
    when there is no valid session. The details carry either the credentials the person signed in with
    or the identity that Entra ID confirmed.
    """
    # A credentials session takes what the person typed at the sign-in form ..
    if token := req.session.get(Session_Credentials_Key):

        # The token becomes invalid when the console is restarted, in which case the user signs in again
        credentials = decrypt_credentials(token)
        if not credentials:
            req.session.flush()
            return None, HttpResponse(_unauthorized_message, status=UNAUTHORIZED)

        username, password = credentials

        auth = {
            'auth_type': OpenAPI_Console_Auth.Type_Credentials,
            'username': username,
            'password': password,
            'is_admin': OpenAPI_Console_Auth.Is_Admin_False,
        }
        return auth, None

    # .. an Entra ID session carries the identity Microsoft confirmed instead ..
    if token := req.session.get(Session_Entra_Key):

        identity = decrypt_entra_identity(token)
        if not identity:
            req.session.flush()
            return None, HttpResponse(_unauthorized_message, status=UNAUTHORIZED)

        username, is_admin = identity

        if is_admin:
            is_admin_value = OpenAPI_Console_Auth.Is_Admin_True
        else:
            is_admin_value = OpenAPI_Console_Auth.Is_Admin_False

        auth = {
            'auth_type': OpenAPI_Console_Auth.Type_Entra,
            'username': username,
            'password': '',
            'is_admin': is_admin_value,
        }
        return auth, None

    # .. and no session at all is unauthorized.
    return None, HttpResponse(_unauthorized_message, status=UNAUTHORIZED)

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
