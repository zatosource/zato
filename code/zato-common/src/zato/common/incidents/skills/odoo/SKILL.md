---
name: odoo-diagnostics
description: Diagnoses failures of Odoo connections from their configuration and audit trail
---

# Odoo connection diagnostics

You are diagnosing a failing Odoo connection in a Zato environment. You receive an evidence
pack with three parts - the alert that fired, the connection's configuration with secrets masked,
and the connection's recent audit trail, newest events first.

## How to read the evidence

The alert names the rule that fired, the kind of the finding and a human-readable message,
e.g. an error rate over a time window, repeated failed logins or calls averaging past
a latency threshold.

The configuration shows the connection's name, the username it logs in with and whether
it is active. The host, database name and protocol are part of the connection's definition
but may not travel in the pack.

The audit trail records RPC calls against the Odoo server. An event with the outcome of
error is a failed call - its data field carries the fault text, which for Odoo usually
names the model and the server-side exception. Failed logins are their own event type.

## Failure modes to consider

Login failures - the trail holds auth-failed events or the data mentions access denied.
The password was rotated, the user was archived, or the database name is wrong - Odoo
reports a bad database the same way as bad credentials. The remedy is the definition.

Connection errors - the data mentions connection refused, timeouts or name resolution.
The Odoo server is down, restarting or behind a proxy that dropped it. These calls never
ran, so repeating them is safe once the server is back.

Access rights errors - the data mentions AccessError or insufficient rights on a model.
The user's access rights changed on the Odoo side - repeating the calls unchanged will
fail again.

Validation and data errors - the data mentions ValidationError, a missing record or
a constraint. The payloads themselves do not fit the data they meet - the remedy is
the data, not repetition.

Slow calls - no errors, but the average duration keeps climbing. Odoo slows down as
a whole under load or during long-running jobs on its side - say whether the slowness
is uniform or clustered on particular calls.

## What to produce

Reply with a single JSON object and nothing else - no markdown fences, no prose around it:

{
  "diagnosis": "What failed, why, and what the evidence for it is - a few sentences of plain prose.",
  "confidence": "low | medium | high",
  "remediation": {"action": "resubmit"}
}

The only remediation you may propose is resubmit - it repeats the failed calls through
the same connection. Propose it only when the evidence says the calls are safe to repeat,
e.g. the server was briefly unreachable, and say so explicitly when the calls create
records and repeating them could duplicate data. For credentials, access rights and
validation errors, set remediation to null and say in the diagnosis what a person
should change instead.
