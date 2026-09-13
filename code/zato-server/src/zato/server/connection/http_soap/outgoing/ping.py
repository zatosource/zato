# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from http.client import OK
from io import StringIO
from logging import getLogger

# Zato
from zato.common.util.api import utcnow
from zato.server.connection.http_soap.outgoing.audit import record_request_sent, record_response_received, \
    record_transport_error

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, stranydict
    from zato.server.connection.http_soap.outgoing import BaseHTTPSOAPWrapper

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# The method a ping goes out with when the connection names none
Default_Ping_Method = 'HEAD'

# The path a ping goes to when the caller names none
Default_Ping_Path = '/'

# The placeholder in a wrapper's address that the ping path replaces
_ping_path_placeholder = r'{_zato_path}'

# ################################################################################################################################
# ################################################################################################################################

def ping(
    wrapper:'BaseHTTPSOAPWrapper',
    cid:'str',
    return_response:'bool'=False,
    log_verbose:'bool'=False,
    *,
    ping_path:'str'=Default_Ping_Path,
    needs_audit:'bool | None'=None,
) -> 'any_':
    """ Pings a given HTTP/SOAP resource. The ping is written to the audit log as the connection's traffic is,
    unless the caller says so itself - a scheduled health check asks for its pings to be written whether
    or not the connection's own audit log is on.
    """
    logger.info('Pinging:`%s`', wrapper.config_no_sensitive)

    if needs_audit is None:
        needs_audit = wrapper.needs_audit
    else:
        needs_audit = needs_audit and wrapper.can_audit

    # Session object will write some info to it ..
    verbose = StringIO()

    start = utcnow()
    ping_method = wrapper.config['ping_method'] or Default_Ping_Method

    def zato_pre_request_hook(hook_data:'stranydict', *args:'any_', **kwargs:'any_') -> 'None':

        entry = '{} (UTC)\n{} {}\n'.format(utcnow().isoformat(),
            ping_method, hook_data['request'].url)
        _ = verbose.write(entry)

    # .. potential wrapper paths must be replaced ..
    ping_path = ping_path or Default_Ping_Path
    address = wrapper.address.replace(_ping_path_placeholder, ping_path)
    endpoint = f'{ping_method} {address}'

    # .. a ping writes the same request/response pair a regular invocation does, sharing one CID,
    # .. but under the connection's health source, so what the check measures stays its own ..
    if needs_audit:
        record_request_sent(wrapper, cid, endpoint, '', ping_method, is_health_check=True)

    # .. invoke the other end ..
    try:
        response = wrapper.invoke_http(cid, ping_method, address, '', wrapper._create_headers(cid, {}),
            {'zato_pre_request':zato_pre_request_hook})
    except Exception as e:

        # .. record the error in the audit log before re-raising ..
        if needs_audit:
            record_transport_error(wrapper, cid, endpoint, e, is_health_check=True)
        raise

    # .. record the received response in the audit log, with the HTTP status it came with ..
    if needs_audit:
        record_response_received(wrapper, cid, endpoint, response, is_health_check=True)

    # .. store additional info, get and close the stream.
    _ = verbose.write('Code: {}'.format(response.status_code))
    _ = verbose.write('\nResponse time: {}'.format(utcnow() - start))
    value = verbose.getvalue()
    verbose.close()

    if log_verbose:
        func = logger.info if response.status_code == OK else logger.warning
        func(value)

    return response if return_response else value

# ################################################################################################################################
# ################################################################################################################################
