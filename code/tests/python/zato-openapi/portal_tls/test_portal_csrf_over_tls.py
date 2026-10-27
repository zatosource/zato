# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from http.client import FORBIDDEN
from pathlib import Path
from unittest.mock import patch

# Django
from django.conf import settings
from django.http import HttpResponse
from django.middleware.csrf import CsrfViewMiddleware
from django.test import RequestFactory

# Zato
from zato.common.crypto.api import CryptoManager
from zato.common.pubsub import server as pubsub_server
from zato.common.webapp.settings import get_csrf_trusted_origins
from zato.openapi.app.views import relay_view

from portal_tls_origins import Trusted_Origin_First, Trusted_Origin_Second, Trusted_Origins_Env_Key

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, intnone, strlist

# ################################################################################################################################
# ################################################################################################################################

_login_path = '/api-portal/login'

_host_name = 'zato.example.com'
_host_tls = _host_name + ':8186'
_host_plain = _host_name + ':8185'

_origin_tls = 'https://' + _host_tls
_origin_plain = 'http://' + _host_plain

# An address the certificate was not issued for, which the browser can still be pointed at
_host_ip_tls = '10.151.12.1:8186'
_origin_ip_tls = 'https://' + _host_ip_tls

# The scheme header that HAProxy sets on each request in the portal's frontend
_proto_header = 'X-Forwarded-Proto'
_proto_https = f'http-request set-header {_proto_header} https if {{ ssl_fc }}'
_proto_http = f'http-request set-header {_proto_header} http if !{{ ssl_fc }}'

_portal_frontend = 'frontend portal'

# A try-it request as the relay receives it
_relay_path = '/api-portal/relay'
_relay_body = '{"method":"POST","path":"/api/orders","query":"","headers":{},"body":"{}"}'
_relay_content_type = 'text/plain'

# Another port of the portal's host
_origin_same_host = 'http://' + _host_name + ':11223'

_csrf_cookie_name = 'zato-api-portal-csrf'

# A CSRF secret is 32 characters, which is 128 bits in hex
_csrf_secret_bits = 128

# ################################################################################################################################
# ################################################################################################################################

def _view(request:'any_') -> 'HttpResponse':
    return HttpResponse()

# ################################################################################################################################

def _check_csrf(host:'str', origin:'str', proto:'str') -> 'intnone':
    """ Runs the portal's CSRF check against a sign-in form submission with a valid token, as it arrives
    from HAProxy with the given scheme header, and returns the status of the rejection, or None if it is accepted.
    """
    secret = CryptoManager.generate_hex_string(_csrf_secret_bits)

    factory = RequestFactory()
    request:'any_' = factory.post(
        _login_path,
        HTTP_HOST=host,
        HTTP_ORIGIN=origin,
        HTTP_X_CSRFTOKEN=secret,
        HTTP_X_FORWARDED_PROTO=proto,
    )
    request.COOKIES[settings.CSRF_COOKIE_NAME] = secret

    middleware = CsrfViewMiddleware(_view)
    middleware.process_request(request)
    response:'any_' = middleware.process_view(request, _view, (), {})

    if response is None:
        return None

    out = response.status_code
    return out

# ################################################################################################################################

def _check_relay_csrf(origin:'str', has_token:'bool') -> 'intnone':
    """ Runs the portal's CSRF check against a relay request on the plain port, with or without the token header,
    and returns the status of the rejection, or None if it is accepted.
    """
    secret = CryptoManager.generate_hex_string(_csrf_secret_bits)

    factory = RequestFactory()
    request:'any_' = factory.post(
        _relay_path,
        _relay_body,
        content_type=_relay_content_type,
        HTTP_HOST=_host_plain,
        HTTP_ORIGIN=origin,
        HTTP_X_FORWARDED_PROTO='http',
    )
    request.COOKIES[settings.CSRF_COOKIE_NAME] = secret

    if has_token:
        request.META['HTTP_X_CSRFTOKEN'] = secret

    middleware = CsrfViewMiddleware(_view)
    middleware.process_request(request)
    response:'any_' = middleware.process_view(request, relay_view, (), {})

    if response is None:
        return None

    out = response.status_code
    return out

# ################################################################################################################################

def _get_portal_frontend_lines() -> 'strlist':
    """ Returns the stripped lines of the portal's frontend in the HAProxy configuration that Zato ships.
    """
    config_path = Path(pubsub_server.__file__).parent / 'haproxy.cfg'
    lines = config_path.read_text().splitlines()

    start = lines.index(_portal_frontend) + 1
    out:'strlist' = []

    # The frontend's own lines are indented and the next section starts at the first column
    for line in lines[start:]:
        if line and not line[0].isspace():
            break
        out.append(line.strip())

    return out

# ################################################################################################################################
# ################################################################################################################################

class TestPortalCSRFOverTLS:
    """ Sign-in form submissions over HTTPS on port 8186 pass the portal's CSRF check under any host name,
    because HAProxy reports the scheme of the browser's connection and the portal trusts that report.
    """

# ################################################################################################################################

    def test_https_through_haproxy_is_accepted(self:'any_') -> 'None':
        assert _check_csrf(_host_tls, _origin_tls, 'https') is None

# ################################################################################################################################

    def test_https_under_an_ip_address_is_accepted(self:'any_') -> 'None':
        assert _check_csrf(_host_ip_tls, _origin_ip_tls, 'https') is None

# ################################################################################################################################

    def test_plain_http_is_accepted(self:'any_') -> 'None':
        assert _check_csrf(_host_plain, _origin_plain, 'http') is None

# ################################################################################################################################

    def test_an_https_origin_over_plain_http_is_rejected(self:'any_') -> 'None':
        """ HAProxy reports http for a connection without TLS whatever the browser sent,
        and a page from an HTTPS origin cannot submit to it.
        """
        assert _check_csrf(_host_plain, _origin_tls, 'http') == FORBIDDEN

# ################################################################################################################################

    def test_another_origin_is_rejected(self:'any_') -> 'None':
        assert _check_csrf(_host_tls, 'https://attacker.example.com', 'https') == FORBIDDEN

# ################################################################################################################################

    def test_a_trusted_origin_is_accepted(self:'any_') -> 'None':
        """ A reverse proxy of one's own terminates TLS and reaches the portal on its plain port.
        """
        assert _check_csrf(_host_plain, Trusted_Origin_First, 'http') is None
        assert _check_csrf(_host_plain, Trusted_Origin_Second, 'http') is None

# ################################################################################################################################
# ################################################################################################################################

class TestRelayCSRF:
    """ The relay accepts a try-it request only from the portal's own origin and only with the CSRF token.
    """

# ################################################################################################################################

    def test_the_portal_origin_with_the_token_is_accepted(self:'any_') -> 'None':
        assert _check_relay_csrf(_origin_plain, True) is None

# ################################################################################################################################

    def test_the_portal_origin_without_the_token_is_rejected(self:'any_') -> 'None':
        assert _check_relay_csrf(_origin_plain, False) == FORBIDDEN

# ################################################################################################################################

    def test_another_port_of_the_host_is_rejected(self:'any_') -> 'None':
        assert _check_relay_csrf(_origin_same_host, False) == FORBIDDEN

# ################################################################################################################################

    def test_the_portal_has_a_csrf_cookie_of_its_own(self:'any_') -> 'None':
        assert settings.CSRF_COOKIE_NAME == _csrf_cookie_name

# ################################################################################################################################
# ################################################################################################################################

class TestPortalTLSSettings:
    """ The portal's settings and the HAProxy frontend in front of it.
    """

# ################################################################################################################################

    def test_the_portal_trusts_the_scheme_header(self:'any_') -> 'None':
        assert settings.SECURE_PROXY_SSL_HEADER == ('HTTP_X_FORWARDED_PROTO', 'https')

# ################################################################################################################################

    def test_the_trusted_origins_come_from_the_environment(self:'any_') -> 'None':
        assert settings.CSRF_TRUSTED_ORIGINS == [Trusted_Origin_First, Trusted_Origin_Second]

# ################################################################################################################################

    def test_haproxy_sets_the_scheme_on_every_request(self:'any_') -> 'None':
        lines = _get_portal_frontend_lines()

        assert _proto_https in lines, f'Missing `{_proto_https}` in the portal frontend: {lines}'
        assert _proto_http in lines, f'Missing `{_proto_http}` in the portal frontend: {lines}'

# ################################################################################################################################
# ################################################################################################################################

class TestGetCSRFTrustedOrigins:
    """ Trusted origins are read from a comma-separated environment variable.
    """

# ################################################################################################################################

    def test_no_variable_means_no_origins(self:'any_') -> 'None':
        environ = dict(os.environ)
        _ = environ.pop(Trusted_Origins_Env_Key)

        with patch.dict(os.environ, environ, clear=True):
            assert get_csrf_trusted_origins(Trusted_Origins_Env_Key) == []

# ################################################################################################################################

    def test_empty_entries_and_spaces_are_left_out(self:'any_') -> 'None':
        value = f' {Trusted_Origin_First} , ,{Trusted_Origin_Second},'

        with patch.dict(os.environ, {Trusted_Origins_Env_Key: value}):
            assert get_csrf_trusted_origins(Trusted_Origins_Env_Key) == [Trusted_Origin_First, Trusted_Origin_Second]

# ################################################################################################################################
# ################################################################################################################################
