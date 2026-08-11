# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The probe implementations - what the default probe scheduler jobs run. Each probe
# measures a fact no per-call audit event can produce - certificate expiry, a remote
# service's own health, a canary transfer - and writes ordinary audit events under
# a source of its own, which the probe collectors read like any other source.
# The remote I/O of each probe is injectable, so tests fake the remote side
# and the probe's own bookkeeping is tested for real.

from __future__ import annotations

# stdlib
import socket
import ssl
from datetime import datetime, timezone
from logging import getLogger

# Zato
from zato.common.alerting.collectors import Attr_Days_Left
from zato.common.audit_log.api import AuditEvent, AuditOutcome, AuditSource

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.audit_log.api import AuditLog
    from zato.common.typing_ import any_, anylist, callable_, dictlist
    any_ = any_
    anylist = anylist
    AuditLog = AuditLog
    callable_ = callable_
    dictlist = dictlist

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# The port a TLS handshake goes to when an address names none.
Default_TLS_Port = 443

# How long one handshake may take before it is abandoned, in seconds.
Default_Handshake_Timeout = 10

# How many seconds one day holds - the certificate measure is expressed in days.
Seconds_Per_Day = 24 * 3600

# What the provider-specific health states normalize into - the two the rules speak.
Health_State_Degraded     = 'degraded'
Health_State_Interruption = 'interruption'

# The provider spellings each normalized state covers. Anything unlisted is healthy,
# so an unknown future state never raises a false alert - it shows up in the raw
# event data where a person can see it.
_health_state_map = {
    'servicedegradation': Health_State_Degraded,
    'degraded': Health_State_Degraded,
    'extendedrecovery': Health_State_Degraded,
    'serviceinterruption': Health_State_Interruption,
    'interruption': Health_State_Interruption,
}

# ################################################################################################################################
# ################################################################################################################################

def get_certificate_days_left(
    host:'str',
    port:'int',
    now:'datetime',
    *,
    timeout:'int' = Default_Handshake_Timeout,
    ) -> 'float':
    """ Performs one TLS handshake and returns how many days the peer's certificate has left.

    The handshake skips chain validation on purpose - the probe measures expiry, and a peer
    whose chain the server does not trust still has a notAfter worth reading. The certificate
    arrives in its binary form because the parsed form is only available for validated chains.
    """

    # cryptography is imported here so importing this module never requires it
    from cryptography import x509

    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    with socket.create_connection((host, port), timeout=timeout) as tcp_connection:
        with context.wrap_socket(tcp_connection, server_hostname=host) as tls_connection:
            certificate_bytes = tls_connection.getpeercert(binary_form=True)

    if certificate_bytes is None:
        raise Exception(f'No certificate received from `{host}:{port}`')

    certificate = x509.load_der_x509_certificate(certificate_bytes)
    not_after = certificate.not_valid_after_utc

    # The comparison needs both moments on the same clock
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)

    remaining = not_after - now
    out = remaining.total_seconds() / Seconds_Per_Day

    return out

# ################################################################################################################################

def run_certificate_probe(
    audit_log:'AuditLog',
    targets:'dictlist',
    now:'datetime',
    *,
    cid:'str' = '',
    check:'callable_' = get_certificate_days_left,
    ) -> 'int':
    """ Measures the certificate of every target - one dict with object_name, host and port -
    and writes one audit event per target, with the days left riding in the event's own attr.
    A handshake that fails writes an error event with no attr, so the collector reports
    nothing rather than a false zero. Returns how many targets were checked.
    """

    # Our response to produce
    out = 0

    for target in targets:

        object_name = target['object_name']
        host = target['host']
        port = target['port']

        endpoint = f'{host}:{port}'

        try:
            days_left = check(host, port, now)
        except Exception as e:

            # One target failing never stops the others from being measured
            logger.info('Certificate check of `%s` (%s) failed -> %s', object_name, endpoint, e)

            _ = audit_log.insert(
                AuditSource.Certificate,
                AuditEvent.Cert_Checked,
                object_name,
                cid=cid,
                endpoint=endpoint,
                outcome=AuditOutcome.Error,
                status=str(e),
            )
        else:
            _ = audit_log.insert(
                AuditSource.Certificate,
                AuditEvent.Cert_Checked,
                object_name,
                cid=cid,
                endpoint=endpoint,
                outcome=AuditOutcome.OK,
                attrs={Attr_Days_Left: round(days_left, 2)},
            )

        out += 1

    return out

# ################################################################################################################################
# ################################################################################################################################

def normalize_health_state(value:'str') -> 'str':
    """ Turns one provider-specific health state into the spelling the rules speak -
    degraded or interruption - with anything unlisted meaning healthy, i.e. an empty state.
    """
    key = value.strip().lower()
    out = _health_state_map.get(key, '')

    return out

# ################################################################################################################################

def run_health_probe(
    audit_log:'AuditLog',
    states:'anylist',
    now:'datetime',
    *,
    cid:'str' = '',
    ) -> 'int':
    """ Records the health state of every remote service - one (service name, raw state) pair
    per service - writing one audit event each. The normalized state travels in the event's
    status column, where the health collector reads it, and the raw provider state stays
    in the event's data for a person to see. Returns how many services were recorded.
    """

    # Our response to produce
    out = 0

    for service_name, raw_state in states:

        normalized = normalize_health_state(raw_state)

        _ = audit_log.insert(
            AuditSource.Microsoft_Health,
            AuditEvent.Health_Checked,
            service_name,
            cid=cid,
            outcome=AuditOutcome.OK,
            status=normalized,
            data=raw_state,
        )

        out += 1

    return out

# ################################################################################################################################
# ################################################################################################################################

def run_canary_probe(
    audit_log:'AuditLog',
    object_name:'str',
    transfer:'callable_',
    now:'datetime',
    *,
    cid:'str' = '',
    ) -> 'bool':
    """ Runs one canary transfer - the callable uploads, downloads, compares and deletes
    a small test file, raising on any failure - and writes its outcome as one audit event.
    Returns True when the transfer succeeded.
    """
    try:
        transfer()
    except Exception as e:

        logger.info('Canary transfer of `%s` failed -> %s', object_name, e)

        _ = audit_log.insert(
            AuditSource.Canary,
            AuditEvent.Canary_Executed,
            object_name,
            cid=cid,
            outcome=AuditOutcome.Error,
            status=str(e),
        )
        return False

    _ = audit_log.insert(
        AuditSource.Canary,
        AuditEvent.Canary_Executed,
        object_name,
        cid=cid,
        outcome=AuditOutcome.OK,
    )
    return True

# ################################################################################################################################
# ################################################################################################################################

def parse_tls_target(address:'str') -> 'tuple[str, int] | None':
    """ Returns the (host, port) a TLS handshake should go to for one https address,
    or None when the address does not speak TLS at all.
    """
    prefix = 'https://'

    if not address.lower().startswith(prefix):
        return None

    # The host and port sit between the scheme and the first slash
    location = address[len(prefix):]
    location = location.split('/')[0]

    # Credentials in the address never belong in a handshake
    if '@' in location:
        location = location.rsplit('@', 1)[1]

    if ':' in location:
        host, _, port_text = location.partition(':')
        port = int(port_text)
    else:
        host = location
        port = Default_TLS_Port

    if not host:
        return None

    out = (host, port)
    return out

# ################################################################################################################################
# ################################################################################################################################
