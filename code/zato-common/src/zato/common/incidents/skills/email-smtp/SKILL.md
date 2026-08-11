---
name: email-smtp-diagnostics
description: Diagnoses failures of SMTP connections from their configuration and audit trail
---

# SMTP connection diagnostics

You are diagnosing a failing SMTP connection in a Zato environment. You receive an evidence
pack with three parts - the alert that fired, the connection's configuration with secrets masked,
and the connection's recent audit trail, newest events first.

## How to read the evidence

The alert names the rule that fired, the kind of the finding and a human-readable message,
e.g. an error rate over a time window or repeated authentication failures.

The configuration shows the connection's name, the username it authenticates with and
whether it is active. The host, port and mode - plain, STARTTLS or SSL - are part of
the connection's definition but may not travel in the pack.

The audit trail records message sends. An event with the outcome of error is a failed send -
its data field carries the SMTP reply or the error text. Authentication failures are their
own event type, so a burst of them is visible even between successful sends.

## Failure modes to consider

Authentication failures - the data mentions authentication failed, or the trail holds
auth-failed events. The password was rotated, the account was locked, or the provider now
requires an app password or OAuth where a plain password used to work. The remedy is
credentials, not resubmission.

Connection errors - the data mentions connection refused, timeouts or name resolution.
The server is down, a firewall closed the port, or the host in the definition is wrong.
Unsent messages are safe to send again once the server is reachable.

TLS errors - the data mentions certificates, handshakes or protocol versions. The server's
certificate changed or the connection's mode no longer matches what the server expects.

Rejected recipients or senders - SMTP 550 and its neighbors, or the data mentions relay
denied, sender rejected or mailbox unavailable. The server accepted the connection and
refused the message - repeating it unchanged will fail again. Say whether the rejections
are about one recipient or all of them.

Rate limits - the data mentions too many messages or temporary deferrals (SMTP 4xx).
These are transient by definition - sending again later is the standard remedy.

## What to produce

Reply with a single JSON object and nothing else - no markdown fences, no prose around it:

{
  "diagnosis": "What failed, why, and what the evidence for it is - a few sentences of plain prose.",
  "confidence": "low | medium | high",
  "remediation": {"action": "resubmit"}
}

The only remediation you may propose is resubmit - it sends the failed messages again through
the same connection. Propose it only when the evidence says the sends are safe to repeat,
e.g. the server was briefly unreachable or deferred with a 4xx. For credentials, TLS
and rejected addresses, set remediation to null and say in the diagnosis what a person
should change instead.
