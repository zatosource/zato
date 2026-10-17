# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

This file is a proprietary product, not an open-source one.
"""

# stdlib
import logging
from http.client import BAD_GATEWAY, INTERNAL_SERVER_ERROR, NOT_FOUND, UNAUTHORIZED
from json import dumps as json_dumps, loads as json_loads
from urllib.parse import quote

# Django
from django.http import FileResponse, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

# PyYAML
import yaml

# Zato
from zato.common.typing_ import cast_
from zato.common.webapp.auth.auth_type import ConsoleAuthType
from zato.common.webapp.auth.session_tokens import Session_Credentials_Key, decrypt_credentials, encrypt_credentials
from zato.common.webapp.request import client_address
from zato.openapi.console.branding import Branding_Files, get_branding_context, get_branding_file_path, \
    get_logo_content_type, get_logo_file
from zato.openapi.console.client import OpenAPIConsoleClient

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anydict, stranydict
    anydict = anydict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# The message shown on the sign-in page when the credentials are rejected
_invalid_credentials_message = 'Invalid credentials'

# The auth types of the sign-in form, in the order they are offered
_auth_types = [
    (ConsoleAuthType.Basic_Auth, 'Basic Auth'),
    (ConsoleAuthType.API_Key, 'API Key'),
    (ConsoleAuthType.Bearer_Token, 'Bearer token'),
]

# What the header shows for a caller signed in with a secret that has no username next to it
_secret_only_identities = {
    ConsoleAuthType.API_Key: 'API key',
    ConsoleAuthType.Bearer_Token: 'Bearer token',
}

# The message shown when no server replied in time
_no_server_message = 'No server is available, please try again'

# The one message returned to any caller without a valid session - always the same
# so that anonymous callers cannot tell apart missing, expired and rejected sessions.
_unauthorized_message = 'Unauthorized'

# The message returned for a branding file that was not provided
_no_such_file_message = 'No such file'

# The base URL under which try-it requests are relayed to the servers - the document's servers
# entry points here, so the browser only ever talks to the console, never to the servers.
_relay_url_base = '/openapi/console/relay'

# The response header in which the browser receives the headers that the endpoint's REST channel would respond with,
# as URL-encoded JSON, apart from the headers of the console's own response
_relay_response_headers_name = 'X-Zato-Console-Response-Headers'

# Maps rejection statuses from the reply stream to the HTTP status and message the browser receives
_relay_rejections = {
    'unauthorized': (UNAUTHORIZED, _unauthorized_message),
    'not_found': (NOT_FOUND, 'Not found'),
    'error': (INTERNAL_SERVER_ERROR, 'The invocation could not be completed'),
    'dropped': (BAD_GATEWAY, _no_server_message),
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

def _text_response(message:'str', status:'int') -> 'HttpResponse':
    """ Returns a response whose body is the given message.
    """
    content = message.encode('utf8')

    out = HttpResponse(content, status=status)
    return out

# ################################################################################################################################

def _is_signed_in(req:'any_') -> 'bool':
    """ Whether the session already has the caller's credentials.
    """
    out = Session_Credentials_Key in req.session
    return out

# ################################################################################################################################

def login_view(req:'any_') -> 'any_':
    """ Renders the sign-in page and handles sign-in attempts. Credentials are validated by a Zato server
    and, once accepted, stored encrypted in the session cookie.
    """
    # Someone whose session already has credentials has nothing to do on the sign-in page
    if _is_signed_in(req):
        return redirect('console')

    context = get_branding_context()
    context['auth_type'] = ConsoleAuthType.Basic_Auth
    context['auth_types'] = _auth_types
    context['basic_auth_type'] = ConsoleAuthType.Basic_Auth
    context['api_key_type'] = ConsoleAuthType.API_Key
    context['bearer_token_type'] = ConsoleAuthType.Bearer_Token

    if req.method == 'POST':
        auth_type = req.POST['auth_type']
        context['auth_type'] = auth_type

        # Each auth type reads its own fields from the form ..
        if build_credentials := _credential_builders.get(auth_type):
            credentials = build_credentials(req.POST)

            # .. a server validates them by building the caller's document ..
            client = _get_client()
            spec = client.get_spec(credentials)

            # .. and a document means the credentials are valid and the session can be established ..
            if spec is not None:
                req.session[Session_Credentials_Key] = encrypt_credentials(credentials)
                return redirect('console')

        # .. otherwise, show the sign-in page again with an error message.
        context['error'] = _invalid_credentials_message

    return render(req, 'login.html', context)

# ################################################################################################################################

def _build_basic_auth_credentials(form:'any_') -> 'stranydict':
    """ Returns the credentials of a username and password sign-in.
    """
    out = {
        'auth_type': ConsoleAuthType.Basic_Auth,
        'username': form['username'],
        'password': form['password'],
    }

    return out

# ################################################################################################################################

def _build_api_key_credentials(form:'any_') -> 'stranydict':
    """ Returns the credentials of an API key sign-in - the key is the only secret and there is no username.
    """
    out = {
        'auth_type': ConsoleAuthType.API_Key,
        'username': '',
        'password': form['key'],
    }

    return out

# ################################################################################################################################

def _build_bearer_token_credentials(form:'any_') -> 'stranydict':
    """ Returns the credentials of a bearer token sign-in - the token is the only secret and there is no username.
    """
    out = {
        'auth_type': ConsoleAuthType.Bearer_Token,
        'username': '',
        'password': form['token'],
    }

    return out

# ################################################################################################################################

# Maps each auth type of the sign-in form to the function that reads its fields
_credential_builders = {
    ConsoleAuthType.Basic_Auth: _build_basic_auth_credentials,
    ConsoleAuthType.API_Key: _build_api_key_credentials,
    ConsoleAuthType.Bearer_Token: _build_bearer_token_credentials,
}

# ################################################################################################################################

def logout_view(req:'any_') -> 'any_':
    """ Ends the session and returns to the sign-in page.
    """
    req.session.flush()

    out = redirect('login')

    return out

# ################################################################################################################################

def console_view(req:'any_') -> 'any_':
    """ Renders the console page - the actual document is loaded by the browser from the spec endpoint.
    """
    # A session without credentials that can be read signs in again ..
    auth, error = _get_auth_or_error(req)
    if error:
        return redirect('login')

    # No error means the auth details are there, hence the cast
    auth = cast_('anydict', auth)

    # .. and the header shows who is signed in, which for an API key or a token is the kind of credentials only.
    context = get_branding_context()
    auth_type = auth['auth_type']

    if auth_type in _secret_only_identities:
        context['identity'] = _secret_only_identities[auth_type]
    else:
        context['identity'] = auth['username']

    out = render(req, 'console.html', context)

    return out

# ################################################################################################################################

def _get_auth_or_error(req:'any_') -> 'any_':
    """ Returns the signed-in caller's auth details and no error, or no details and an error response
    when there is no valid session. The details are the credentials the person signed in with.
    """
    # No session at all is unauthorized ..
    if not (token := req.session.get(Session_Credentials_Key)):
        return None, _text_response(_unauthorized_message, UNAUTHORIZED)

    # .. the token becomes invalid when the console is restarted, in which case the user signs in again ..
    auth = decrypt_credentials(token)
    if not auth:
        req.session.flush()
        return None, _text_response(_unauthorized_message, UNAUTHORIZED)

    # .. and the session has what the person typed at the sign-in form.
    return auth, None

# ################################################################################################################################

def _get_spec_or_error(req:'any_') -> 'any_':
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
        return None, _text_response(_unauthorized_message, UNAUTHORIZED)

    # Try-it requests go through the console's relay, never directly to the servers
    spec['servers'] = [{'url': _relay_url_base}]

    return spec, None

# ################################################################################################################################

def spec_view(req:'any_') -> 'any_':
    """ Serves the OpenAPI document filtered down to what the signed-in user's credentials give access to.
    The filtering happens on Zato servers - the document never contains endpoints the caller cannot invoke.
    """
    spec, error = _get_spec_or_error(req)
    if error:
        return error

    out = JsonResponse(spec)

    return out

# ################################################################################################################################

def spec_yaml_view(req:'any_') -> 'any_':
    """ Serves the same per-caller filtered OpenAPI document as the JSON view, rendered as YAML.
    """
    spec, error = _get_spec_or_error(req)
    if error:
        return error

    document = yaml.dump(spec, sort_keys=False, allow_unicode=True)
    content = document.encode('utf8')

    out = HttpResponse(content, content_type='application/yaml')

    return out

# ################################################################################################################################

@csrf_exempt
@require_POST
def relay_view(req:'any_', relay_path:'str') -> 'any_':
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

    # The browser sends the request as one JSON document, the caller's own headers apart from those it adds itself ..
    envelope = json_loads(req.body)

    # .. and a request with no body has none in the document either.
    body = envelope['body']

    if body is None:
        body = ''

    headers = json_dumps(envelope['headers'])
    remote_addr = client_address(req)

    client = _get_client()
    reply = client.invoke(auth, envelope['method'], url_path, envelope['query'], headers, body, remote_addr)

    # No reply means no server was available in time
    if reply is None:
        return _text_response(_no_server_message, BAD_GATEWAY)

    status = reply['status']

    # A successful invocation passes the service's response through, with the headers its REST channel would send ..
    if status == 'ok':
        http_status = int(reply['http_status'])
        content = reply['data'].encode('utf8')
        out = HttpResponse(content, status=http_status, content_type=reply['content_type'])
        out[_relay_response_headers_name] = quote(reply['headers'])

    # .. anything else maps to one of the known rejections.
    else:
        http_status, message = _relay_rejections[status]
        out = _text_response(message, http_status)

    return out

# ################################################################################################################################

def favicon_view(req:'any_') -> 'any_':
    """ Answers the icon request browsers make at the root path on their own, with whichever
    icon the console is branded with.
    """
    branding = get_branding_context()
    out = redirect(branding['favicon_url'])
    return out

# ################################################################################################################################

def branding_view(req:'any_', file_name:'str') -> 'any_':
    """ Serves a user-provided branding file from the well-known branding directory.
    """
    full_path = get_branding_file_path(file_name)

    if not full_path:
        return _text_response(_no_such_file_message, NOT_FOUND)

    content_type = Branding_Files[file_name]

    out = FileResponse(open(full_path, 'rb'), content_type=content_type)

    return out

# ################################################################################################################################

def logo_view(req:'any_') -> 'any_':
    """ Serves the custom logo file that the environment points to.
    """
    if not (logo_path := get_logo_file()):
        return _text_response(_no_such_file_message, NOT_FOUND)

    content_type = get_logo_content_type(logo_path)

    out = FileResponse(open(logo_path, 'rb'), content_type=content_type)

    return out

# ################################################################################################################################
# ################################################################################################################################
