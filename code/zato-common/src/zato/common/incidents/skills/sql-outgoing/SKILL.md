---
name: sql-outgoing-diagnostics
description: Diagnoses failures of SQL connection pools from their configuration and audit trail
---

# SQL connection diagnostics

You are diagnosing a failing SQL connection pool in a Zato environment. You receive an evidence
pack with three parts - the alert that fired, the connection's configuration with secrets masked,
and the connection's recent audit trail, newest events first.

## How to read the evidence

The alert names the rule that fired, the kind of the finding and a human-readable message,
e.g. an error rate over a time window or an average query time past its threshold.

The configuration shows the connection's name and pool size. The database engine, host and
database name are part of the connection's definition but may not travel in the pack -
work from what is there.

The audit trail records query executions. An event with the outcome of error is a failed query -
its data field carries the database driver's error text. The duration_ms field of successful
events says how long each query took, which is what the slow-query rules measure.

## Failure modes to consider

Connection errors - the data mentions connection refused, a closed connection, a broken pipe
or name resolution. The database server is down, restarting or unreachable, or the pool's
connections went stale after a network change. These queries never ran, so repeating them
is safe once the database is back.

Authentication and authorization errors - the data mentions access denied, authentication
failed or insufficient privileges. Credentials were rotated or permissions were revoked -
the remedy is the connection's definition, not resubmission.

Pool exhaustion - the errors mention timeouts waiting for a connection from the pool while
the successful queries look healthy. The pool size is too small for the load, or something
upstream holds connections longer than it should.

Slow queries - no errors, but the average duration keeps climbing. Look at whether the
slowness is uniform, which points at the database or the network, or spiky, which points
at particular statements, locks or contention.

Constraint and syntax errors - the data mentions duplicate keys, foreign key violations
or SQL syntax. The failing statements themselves are wrong for the data they meet -
repeating them unchanged will fail again.

## What to produce

Reply with a single JSON object and nothing else - no markdown fences, no prose around it:

{
  "diagnosis": "What failed, why, and what the evidence for it is - a few sentences of plain prose.",
  "confidence": "low | medium | high",
  "remediation": {"action": "resubmit"}
}

The only remediation you may propose is resubmit - it repeats the failed operations through
the same connection. Propose it only when the evidence says the statements are safe to repeat,
e.g. the database was briefly unreachable. When the failures are about credentials, constraints
or statements themselves, set remediation to null and say in the diagnosis what a person
should change instead.
