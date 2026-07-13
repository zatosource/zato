# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import logging

# Django
from django.http import HttpResponse
from django.template.response import TemplateResponse

# Zato
from zato.admin.web.views import method_allowed
from zato.common.defaults import default_cluster_id

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

_highlight_open = '<span class="how-it-works-posture-highlight">'
_highlight_close = '</span>'

_toggle_html = (
    '<div class="how-it-works-posture-toggle">'
        '<span class="how-it-works-posture-toggle-label">Toggle</span>'
        '<input type="checkbox" class="how-it-works-posture-toggle-input">'
    '</div>'
)

# ################################################################################################################################
# ################################################################################################################################

def _highlight(text:'str') -> 'str':
    return f'{_highlight_open}{text}{_highlight_close}'

# ################################################################################################################################
# ################################################################################################################################

def _make_description(title:'str', body:'str') -> 'str':
    return (
        '<div class="how-it-works-posture-explanation">'
            f'<div class="how-it-works-posture-title">{title}</div>'
            f'<div class="how-it-works-posture-body">{body}</div>'
            f'{_toggle_html}'
        '</div>'
    )

# ################################################################################################################################
# ################################################################################################################################

def _build_field_descriptions() -> 'dict':

    out = {

        # .. authentication tab ..

        'posture-toggle-auth-no-credentials': _make_description('Channels without credentials',
            'Every REST channel can be protected by assigning a security definition, such as Basic Auth or API keys.'
            '<br><br>'
            'This check ' + _highlight('flags any REST channels that do not have a security definition assigned') + '.'
            '<br><br>'
            'A channel without credentials means anyone who knows the URL can call it freely.'
            '<br><br>'
            'Often fine during development, but in production it can be a serious exposure.'
            '<br><br>'
            'The check helps you spot these channels so you can secure them or mark them as intentionally public.'
        ),

        'posture-toggle-auth-weak-credentials': _make_description('Weak passwords',
            'Security definitions in Zato store the credentials that clients use to authenticate.'
            '<br><br>'
            'This check ' + _highlight('measures the strength of every password in your security definitions') + '.'
            '<br><br>'
            'Strength is scored from 0 to 4:'
            '<br>0 or 1 - cracked almost instantly'
            '<br>2 - guessable with some effort'
            '<br>3 - safe'
            '<br>4 - very hard to crack'
            '<br><br>'
            'The scoring considers length, character variety, common patterns, and known breach lists.'
        ),

        'posture-toggle-rate-limiting': _make_description('Missing rate limiting',
            'Rate limiting controls how many requests a client can make in a given time window.'
            '<br><br>'
            'This check ' + _highlight('finds REST channels and services that do not have any rate limiting configured') + '.'
            '<br><br>'
            'Without it, a single client can flood your server with requests.'
            '<br><br>'
            'Even a simple limit like 1,000 requests per minute protects against runaway loops and denial-of-service attempts.'
        ),

        'posture-toggle-admin-services-exposed': _make_description('Admin services exposed',
            'Zato has built-in admin services used by the dashboard and CLI.'
            '<br><br>'
            'They can create users, change passwords, deploy code, and read configuration.'
            '<br><br>'
            'This check ' + _highlight('finds admin services mounted on channels reachable from outside the cluster') + '.'
        ),

        'posture-toggle-internal-no-auth': _make_description('Internal services without auth',
            'Some services are meant only for internal use - called by other services, scheduled jobs, or internal tooling.'
            '<br><br>'
            'This check ' + _highlight('flags internal services that have a channel but no security definition protecting it') + '.'
            '<br><br>'
            'Without authentication, any process that can reach the channel URL can invoke the service.'
        ),

        # .. incoming channels tab ..

        'posture-toggle-request-forgery': _make_description('Request forgery risks',
            'If a service accepts a URL from a caller and uses it to make an outgoing request, '
            'an attacker can supply an internal URL instead.'
            '<br><br>'
            'This check ' + _highlight('scans service code for patterns where user-supplied URLs are passed to outgoing connections') + '.'
            '<br><br>'
            'This lets the attacker reach internal systems that should not be accessible from outside.'
        ),

        'posture-toggle-unused-channels': _make_description('Unused channels',
            'Channels that receive no traffic are easy to forget about.'
            '<br><br>'
            'This check ' + _highlight('finds channels with no requests in the configured time window') + '.'
            '<br><br>'
            'Unused channels still accept connections, so removing or disabling them reduces the number of entry points into your system.'
        ),

        'posture-toggle-orphaned-services': _make_description('Unattached services',
            'A service with no channel and no scheduled job cannot be invoked by external clients.'
            '<br><br>'
            'This check ' + _highlight('detects services that have no channel or scheduled job attached') + '.'
            '<br><br>'
            'Unattached services may be leftover from earlier development or a sign of incomplete configuration.'
        ),

        'posture-toggle-pii-detection': _make_description('Personal data in responses',
            'API responses can accidentally include credit card numbers, national IDs, or other personal data.'
            '<br><br>'
            'This check ' + _highlight('scans outgoing payloads for common PII patterns') + '.'
            '<br><br>'
            'Catching PII in responses helps prevent data leaks before they reach external consumers.'
        ),

        'posture-toggle-connection-string-leaks': _make_description('Connection string leaks',
            'Database and broker connection strings contain hostnames, ports, and sometimes credentials.'
            '<br><br>'
            'This check ' + _highlight('detects connection strings appearing in API responses') + '.'
            '<br><br>'
            'Leaking a connection string gives attackers a direct path to your internal infrastructure.'
        ),

        'posture-toggle-cumulative-data': _make_description('Cumulative data exposure',
            'A single response may look harmless, but many small responses can add up to a full data set.'
            '<br><br>'
            'This check ' + _highlight('tracks the total volume of sensitive fields returned per consumer over time') + '.'
            '<br><br>'
            'Monitoring cumulative exposure catches slow, distributed data exfiltration.'
        ),

        # .. configuration tab ..

        'posture-toggle-debug-mode': _make_description('Debug mode enabled',
            'Debug mode exposes detailed error messages, stack traces, and internal state to callers.'
            '<br><br>'
            'This check ' + _highlight('warns if the server is running with debug or development settings') + '.'
            '<br><br>'
            'In production, debug output can reveal file paths, database queries, and internal logic to attackers.'
        ),

        'posture-toggle-plaintext-secrets': _make_description('Plaintext secrets in config',
            'Configuration files can contain passwords, API tokens, and database credentials.'
            '<br><br>'
            'This check ' + _highlight('scans configuration files for passwords and tokens stored in clear text') + '.'
            '<br><br>'
            'Secrets in plain text can be read by anyone with file system access or by accident through version control.'
        ),

        'posture-toggle-known-vulnerabilities': _make_description('Known vulnerabilities',
            'Python packages can have publicly disclosed security flaws.'
            '<br><br>'
            'This check ' + _highlight('compares installed packages against known CVE databases') + '.'
        ),

        'posture-toggle-tls-certificates': _make_description('TLS certificates',
            'TLS certificates encrypt traffic and prove server identity.'
            '<br><br>'
            'This check ' + _highlight('validates certificate chains and warns about upcoming expirations') + '.'
            '<br><br>'
            'An expired or misconfigured certificate causes outages and can expose traffic to interception.'
        ),

        # .. outgoing connections tab ..

        'posture-toggle-unencrypted-traffic': _make_description('Unencrypted traffic',
            'Outgoing connections using plain HTTP send data without encryption.'
            '<br><br>'
            'This check ' + _highlight('finds outgoing connections using HTTP instead of HTTPS') + '.'
            '<br><br>'
            'Unencrypted traffic can be intercepted by anyone on the network path between your server and the remote system.'
        ),

        'posture-toggle-missing-timeouts': _make_description('Missing timeouts',
            'An outgoing connection without a timeout will wait indefinitely if the remote system stops responding.'
            '<br><br>'
            'This check ' + _highlight('detects outgoing connections without timeout values set') + '.'
            '<br><br>'
            'Hanging connections consume resources and can eventually make the server unresponsive.'
        ),

        'posture-toggle-outgoing-cert-issues': _make_description('Certificate issues',
            'Outgoing TLS connections rely on valid certificates to ensure traffic goes to the right destination.'
            '<br><br>'
            'This check ' + _highlight('looks for expired, self-signed, or weak certificates on outgoing connections') + '.'
            '<br><br>'
            'A bad certificate means traffic may not be going where you think it is.'
        ),

        'posture-toggle-backend-no-auth': _make_description('Backend connections without auth',
            'Outgoing connections to backend systems can be configured with authentication.'
            '<br><br>'
            'This check ' + _highlight('finds outgoing connections with no authentication configured') + '.'
            '<br><br>'
            'Without credentials, anyone who can reach the same backend endpoint can use it.'
        ),

        'posture-toggle-backend-tls-version': _make_description('Outdated TLS versions',
            'TLS 1.0 and 1.1 have known vulnerabilities and are deprecated.'
            '<br><br>'
            'This check ' + _highlight('flags outgoing connections that allow TLS 1.0 or 1.1') + '.'
            '<br><br>'
            'All connections should use TLS 1.2 or newer.'
        ),

        'posture-toggle-backend-tls-ciphers': _make_description('Weak TLS ciphers',
            'Some older cipher suites can be broken with modern hardware.'
            '<br><br>'
            'This check ' + _highlight('detects outgoing connections using deprecated cipher suites') + '.'
            '<br><br>'
            'Weak ciphers make encrypted traffic vulnerable to decryption.'
        ),

        # .. runtime and data tab ..

        'posture-toggle-bulk-extraction': _make_description('Bulk data extraction',
            'A single request that returns an unusually large response may indicate data scraping.'
            '<br><br>'
            'This check ' + _highlight('detects responses with abnormally large payloads') + '.'
            '<br><br>'
            'Monitoring response sizes helps catch unauthorized bulk downloads early.'
        ),

        'posture-toggle-enumeration': _make_description('Enumeration attempts',
            'Attackers probe APIs by trying sequential IDs to discover valid resources.'
            '<br><br>'
            'This check ' + _highlight('watches for sequential ID probing and resource enumeration patterns') + '.'
            '<br><br>'
            'A burst of requests with incrementing IDs is a strong signal of enumeration.'
        ),

        'posture-toggle-credential-anomaly': _make_description('Credential anomalies',
            'Repeated authentication failures from the same IP address suggest a brute-force attack.'
            '<br><br>'
            'This check ' + _highlight('tracks per-IP authentication failure rates') + '.'
            '<br><br>'
            'Flagging IPs with high failure rates lets you block them before they succeed.'
        ),

        'posture-toggle-pagination-abuse': _make_description('Pagination abuse',
            'Some APIs accept offset and page-size parameters.'
            '<br><br>'
            'This check ' + _highlight('detects requests with extreme offset or page-size values') + '.'
            '<br><br>'
            'Very large values can cause excessive memory use or expose more data than intended.'
        ),

        'posture-toggle-request-rate-anomaly': _make_description('Request rate anomalies',
            'A sudden spike in requests to a single endpoint may indicate an attack or a misbehaving client.'
            '<br><br>'
            'This check ' + _highlight('uses sliding window counters to flag unusual traffic spikes per endpoint') + '.'
            '<br><br>'
            'Rate anomalies are detected even when individual requests stay within normal rate limits.'
        ),

        'posture-toggle-call-pattern-anomaly': _make_description('Call pattern anomalies',
            'Normal API consumers follow predictable sequences of calls.'
            '<br><br>'
            'This check ' + _highlight('uses ML-based detection to find abnormal API call sequences and timing') + '.'
            '<br><br>'
            'Unusual patterns can reveal automated attacks, credential stuffing, or compromised accounts.'
        ),
    }

    return out

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def index(req:'object') -> 'TemplateResponse':

    active_tab = req.GET['tab']

    scan_data = {
        'check_states': {},
    }

    try:
        response = req.zato.client.invoke('zato.security.posture.get-check-states', {})
        if response.ok:
            scan_data['check_states'] = response.data
    except Exception as e:
        logger.warning('Security posture dashboard error: %s', e)

    return TemplateResponse(req, 'zato/security/posture.html', {
        'cluster_id': default_cluster_id,
        'scan_data': json.dumps(scan_data),
        'active_tab': active_tab,
        'field_descriptions': json.dumps(_build_field_descriptions()),
        'zato_clusters': True,
        'zato_template_name': 'zato/security/posture.html',
    })

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def run_scan(req:'object') -> 'HttpResponse':

    try:
        body = json.loads(req.body)
        response = req.zato.client.invoke('zato.security.posture.run-scan', body)
        if response.ok:
            return HttpResponse(json.dumps(response.data), content_type='application/json')
        else:
            return HttpResponse(
                json.dumps({'error': response.details}),
                content_type='application/json',
                status=500,
            )
    except Exception as e:
        logger.error('Security posture scan error: %s', e)
        return HttpResponse(
            json.dumps({'error': str(e)}),
            content_type='application/json',
            status=500,
        )

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def save(req:'object') -> 'HttpResponse':

    try:
        body = json.loads(req.body)
        response = req.zato.client.invoke('zato.security.posture.save-check-states', body)
        if response.ok:
            return HttpResponse(json.dumps({'status': 'ok'}), content_type='application/json')
        else:
            return HttpResponse(
                json.dumps({'error': response.details}),
                content_type='application/json',
                status=500,
            )
    except Exception as e:
        logger.error('Security posture save error: %s', e)
        return HttpResponse(
            json.dumps({'error': str(e)}),
            content_type='application/json',
            status=500,
        )

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def poll(req:'object') -> 'HttpResponse':

    try:
        response = req.zato.client.invoke('zato.security.posture.get-results', {})
        if response.ok:
            return HttpResponse(json.dumps(response.data), content_type='application/json')
        else:
            return HttpResponse(
                json.dumps({'error': response.details}),
                content_type='application/json',
                status=500,
            )
    except Exception as e:
        logger.error('Security posture poll error: %s', e)
        return HttpResponse(
            json.dumps({'error': str(e)}),
            content_type='application/json',
            status=500,
        )

# ################################################################################################################################
# ################################################################################################################################
