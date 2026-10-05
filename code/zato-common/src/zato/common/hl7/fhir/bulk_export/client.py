# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from http.client import ACCEPTED, OK, TOO_MANY_REQUESTS, INTERNAL_SERVER_ERROR
from logging import getLogger
from time import sleep

# requests
from requests import Session

# Zato
from zato.common.api import HL7
from zato.common.bearer_token import BearerTokenManager
from zato.common.model.security import BearerTokenConfig
from zato.common.typing_ import cast_

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from requests import Response
    from zato.common.hl7.fhir.bulk_export.spec import JobSpec
    from zato.common.typing_ import any_, callable_, stranydict, strdict

    JobSpec    = JobSpec
    Response   = Response
    any_       = any_
    callable_  = callable_
    stranydict = stranydict
    strdict    = strdict

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

_bulk = HL7.BulkExport
_oauth = HL7.Const.FHIR_Auth_Type.OAuth.id

# ################################################################################################################################
# ################################################################################################################################

# The headers a bulk export exchange uses
Header_Accept           = 'Accept'
Header_Prefer           = 'Prefer'
Header_Authorization    = 'Authorization'
Header_Content_Location = 'Content-Location'
Header_Retry_After      = 'Retry-After'
Header_Progress         = 'X-Progress'

Accept_FHIR_JSON   = 'application/fhir+json'
Prefer_Async       = 'respond-async'

# The query parameters of a kick-off request
Param_Type        = '_type'
Param_Since       = '_since'
Param_Type_Filter = '_typeFilter'
Param_Patient     = 'patient'

# A cached token is replaced this long before it would expire
Token_Refresh_Margin = timedelta(minutes=1)

# How long to wait before a 429 or 5xx is tried again, doubled on each attempt
Backoff_Base_Seconds = 2

# How large a piece of a file is read at a time
Download_Chunk_Size = 64 * 1024

# ################################################################################################################################
# ################################################################################################################################

class BulkExportError(Exception):
    """ Raised when the FHIR server answers in a way the export cannot carry on from.
    """
    def __init__(self, message:'str', status:'int'=0) -> 'None':
        super().__init__(message)
        self.message = message
        self.status = status

# ################################################################################################################################
# ################################################################################################################################

class _TokenServer:
    """ What BearerTokenManager needs of a server when it talks to the auth server only - no cache,
    no security facade and a decrypt that returns its input because the spec's secrets are already clear.
    """
    def __init__(self) -> 'None':
        self.security_facade = None
        self.config_manager = _TokenConfigManager()

    def decrypt(self, data:'any_') -> 'any_':
        return data

class _TokenConfigManager:
    cache_api = None

# ################################################################################################################################
# ################################################################################################################################

class TokenProvider:
    """ Hands out the bearer token of a job, fetching a new one when none is cached or the cached one is about to expire.
    """
    def __init__(self, spec:'JobSpec') -> 'None':
        self.spec = spec
        token_server = cast_('any_', _TokenServer())
        self.manager = BearerTokenManager(token_server)
        self.config = self._build_config(spec.bearer)
        self.token = ''
        self.expiration_time:'datetime | None' = None

# ################################################################################################################################

    def _build_config(self, bearer:'stranydict') -> 'BearerTokenConfig':
        out = BearerTokenConfig()
        for name, value in bearer.items():
            setattr(out, name, value)

        return out

# ################################################################################################################################

    def _needs_refresh(self) -> 'bool':

        # No token at all means one is needed ..
        if not self.token:
            return True

        # .. a token with no expiry is reused until the job ends ..
        if self.expiration_time is None:
            return False

        # .. and one that is about to expire is replaced ahead of time.
        now = datetime.now(tz=timezone.utc)
        out = now + Token_Refresh_Margin >= self.expiration_time

        return out

# ################################################################################################################################

    def get_header(self) -> 'str':
        if self._needs_refresh():
            info = self.manager._get_bearer_token_from_auth_server(self.config, self.spec.scopes, self.spec.bearer_data_format)
            self.token = info.token
            self.expiration_time = info.expiration_time

        out = f'Bearer {self.token}'
        return out

# ################################################################################################################################
# ################################################################################################################################

def get_retry_after(response:'Response') -> 'int':
    """ Reads how long the server asks us to wait - a number of seconds or an HTTP date - defaulting
    to the spec's suggestion when the header is absent.
    """
    value = response.headers.get(Header_Retry_After)

    if not value:
        return _bulk.Default_Retry_After

    if value.isdigit():
        return int(value)

    # The header is an HTTP date - the wait is whatever is left until then, never negative
    when = parsedate_to_datetime(value)
    now = datetime.now(tz=timezone.utc)
    seconds = (when - now).total_seconds()

    out = max(int(seconds), 0)
    return out

# ################################################################################################################################

def is_retriable(status:'int') -> 'bool':
    out = status == TOO_MANY_REQUESTS or status >= INTERNAL_SERVER_ERROR
    return out

# ################################################################################################################################
# ################################################################################################################################

class BulkExportClient:
    """ The HTTP side of one export - kick-off, status polling, file downloads and the final delete.
    """
    def __init__(self, spec:'JobSpec', on_progress:'callable_') -> 'None':
        self.spec = spec
        self.session = Session()
        self.on_progress = on_progress

        # Bearer tokens are fetched on demand, a Basic Auth header is ready from the start
        if spec.auth_type == _oauth:
            self.token_provider:'TokenProvider | None' = TokenProvider(spec)
        else:
            self.token_provider = None

# ################################################################################################################################

    def _get_auth_header(self) -> 'str':
        if self.token_provider:
            out = self.token_provider.get_header()
        else:
            out = self.spec.basic_auth_header

        return out

# ################################################################################################################################

    def _get_headers(self, accept:'str', *, needs_auth:'bool'=True) -> 'strdict':
        out = {Header_Accept: accept}

        if needs_auth:
            auth_header = self._get_auth_header()
            if auth_header:
                out[Header_Authorization] = auth_header

        return out

# ################################################################################################################################

    def _request_with_retry(self, method:'str', url:'str', **kwargs:'any_') -> 'Response':
        """ Sends one request, trying again after a wait when the server is overloaded or failing.
        """
        attempt = 0

        while True:
            response = self.session.request(method, url, **kwargs)

            # Anything that is not a transient server-side condition is for the caller to judge ..
            if not is_retriable(response.status_code):
                return response

            # .. the attempts are exhausted so this is what the caller gets ..
            attempt += 1
            if attempt > _bulk.Download_Retries:
                return response

            # .. a 429 says how long to wait, a 5xx does not so the wait grows with each attempt ..
            if response.status_code == TOO_MANY_REQUESTS:
                wait = get_retry_after(response)
            else:
                wait = Backoff_Base_Seconds ** attempt

            logger.info('Bulk export %s -> %s returned %s, attempt %s, waiting %ss',
                method, url, response.status_code, attempt, wait)

            # .. a streamed response holds its connection until it is closed.
            response.close()
            sleep(wait)

# ################################################################################################################################

    def build_kickoff_url(self) -> 'str':
        path = _bulk.Kickoff_Path[self.spec.level]
        path = path.format(group_id=self.spec.group_id)

        out = self.spec.address.rstrip('/') + path
        return out

# ################################################################################################################################

    def build_kickoff_params(self) -> 'strdict':
        out = {}

        if self.spec.types:
            out[Param_Type] = ','.join(self.spec.types)

        if self.spec.since:
            out[Param_Since] = self.spec.since

        if self.spec.type_filter:
            out[Param_Type_Filter] = ','.join(self.spec.type_filter)

        if self.spec.patient_ids:
            out[Param_Patient] = ','.join(self.spec.patient_ids)

        return out

# ################################################################################################################################

    def kickoff(self) -> 'tuple[str, int]':
        """ Starts the export and returns the URL its status is polled at along with the HTTP status received.
        """
        url = self.build_kickoff_url()
        params = self.build_kickoff_params()

        headers = self._get_headers(Accept_FHIR_JSON)
        headers[Header_Prefer] = Prefer_Async

        response = self._request_with_retry('GET', url, params=params, headers=headers)

        if response.status_code != ACCEPTED:
            raise BulkExportError(f'Kick-off of `{url}` was not accepted -> {response.status_code} -> {response.text}',
                response.status_code)

        status_url = response.headers.get(Header_Content_Location)
        if not status_url:
            raise BulkExportError(f'Kick-off of `{url}` was accepted without a {Header_Content_Location} header',
                response.status_code)

        return status_url, response.status_code

# ################################################################################################################################

    def poll(self, status_url:'str') -> 'stranydict':
        """ Polls the status URL until the manifest is ready, waiting as long as the server asks between polls.
        """
        while True:
            headers = self._get_headers(Accept_FHIR_JSON)
            response = self._request_with_retry('GET', status_url, headers=headers)

            # The export is complete and this is its manifest ..
            if response.status_code == OK:
                out = response.json()
                return out

            # .. anything other than "still running" means the export failed on the server ..
            if response.status_code != ACCEPTED:
                raise BulkExportError(f'Polling `{status_url}` failed -> {response.status_code} -> {response.text}',
                    response.status_code)

            # .. otherwise, the server says how far along it is and how long to wait.
            progress = response.headers.get(Header_Progress, '')
            wait = get_retry_after(response)

            self.on_progress(progress, wait)
            sleep(wait)

# ################################################################################################################################

    def download(self, url:'str', path:'str', *, needs_auth:'bool') -> 'int':
        """ Streams one file to disk and returns how many non-empty lines it has.
        """
        headers = self._get_headers(_bulk.Content_Type, needs_auth=needs_auth)
        response = self._request_with_retry('GET', url, headers=headers, stream=True)

        if response.status_code != OK:
            response.close()
            raise BulkExportError(f'Download of `{url}` failed -> {response.status_code} -> {response.text}',
                response.status_code)

        # Written piece by piece so a file of any size fits in memory, with a gzip body unpacked on the way
        with open(path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=Download_Chunk_Size):
                _ = file.write(chunk)

        out = count_lines(path)
        return out

# ################################################################################################################################

    def delete(self, status_url:'str') -> 'int':
        """ Tells the server the export's files can go and returns the HTTP status received.
        """
        headers = self._get_headers(Accept_FHIR_JSON)
        response = self._request_with_retry('DELETE', status_url, headers=headers)

        out = response.status_code
        return out

# ################################################################################################################################
# ################################################################################################################################

def count_lines(path:'str') -> 'int':
    """ Counts the non-empty lines of a file without reading it whole.
    """
    out = 0

    with open(path, 'rb') as file:
        for line in file:
            if line.strip():
                out += 1

    return out

# ################################################################################################################################
# ################################################################################################################################
