# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from time import monotonic
from uuid import uuid4

# Zato
from zato.common.rule_engine.sql.data import DecisionWrite
from zato.common.rule_engine.sql.time_ import utc_now
from zato.common.rule_engine.testing import evaluate_input

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.rule_engine.sql import DecisionBatchWriter
    from zato.common.rule_engine.testing import LoadedRules
    from zato.common.typing_ import anydict

# ################################################################################################################################
# ################################################################################################################################

class Outcome:
    """ The promoted outcome column of one recorded decision.
    """
    Matched  = 'matched'
    No_Match = 'no-match'
    Error    = 'error'

# ################################################################################################################################

# What decisions carry when no input field is configured to be their business key.
Default_Business_Key_Field = ''

Milliseconds_Per_Second = 1000

# ################################################################################################################################
# ################################################################################################################################

class DecisionRecorder:
    """ Turns rule evaluations into decision-log writes behind one non-blocking writer.

    Every evaluation becomes a complete DecisionWrite - the id, the promoted outcome,
    the duration, the optional business key and the full story with the rules that fired.
    Whether the story is retained is the capture dial's call at write time, never this class's.
    """

    def __init__(
        self,
        writer:'DecisionBatchWriter',
        *,
        ruleset_id:'int',
        rules_version:'int',
        business_key_field:'str' = Default_Business_Key_Field,
        ) -> 'None':

        self.writer = writer
        self.ruleset_id = ruleset_id
        self.rules_version = rules_version
        self.business_key_field = business_key_field

# ################################################################################################################################

    def _business_key(self, data:'anydict') -> 'str | None':
        """ Returns the input value promoted as the decision's business key.
        """
        # Without a configured field no decision carries a business key ..
        if not self.business_key_field:
            out = None

        # .. an input that carries the field promotes its value ..
        elif self.business_key_field in data:
            out = data[self.business_key_field]

        # .. and an input without it is still a valid decision, just an unkeyed one.
        else:
            out = None

        return out

# ################################################################################################################################

    def record(self, loaded:'LoadedRules', data:'anydict') -> 'anydict':
        """ Evaluates one input against the loaded rules, logs the complete decision and returns the outcome.
        """
        # Time the complete evaluation, which never raises - an input a rule
        # cannot evaluate comes back with a readable error instead ..
        started = monotonic()
        evaluated = evaluate_input(loaded, data)
        elapsed = monotonic() - started

        # .. the duration column holds whole milliseconds ..
        duration_ms = int(elapsed * Milliseconds_Per_Second)
        occurred_at = utc_now()

        error = evaluated['error']
        fired = evaluated['fired']
        actual = evaluated['actual']

        # .. the promoted outcome names how the evaluation ended ..
        if error:
            outcome = Outcome.Error
        elif fired:
            outcome = Outcome.Matched
        else:
            outcome = Outcome.No_Match

        is_error = outcome == Outcome.Error

        # .. the canonical fired-rule list holds full rule names, in rule order ..
        fired_rule_ids = []
        for entry in fired:
            fired_rule_ids.append(entry['rule'])

        # .. the story keeps everything an investigation needs - the capture dial
        # .. decides at write time whether it is retained, errors always are ..
        story = {
            'input':      data,
            'outputs':    actual,
            'statements': fired,
            'error':      error,
        }

        decision_id = uuid4().hex
        business_key = self._business_key(data)

        decision = DecisionWrite(
            decision_id=decision_id,
            ruleset_id=self.ruleset_id,
            rules_version=self.rules_version,
            occurred_at=occurred_at,
            business_key=business_key,
            outcome=outcome,
            is_error=is_error,
            duration_ms=duration_ms,
            story=story,
            fired_rule_ids=fired_rule_ids,
        )

        # .. hand the decision to the non-blocking writer ..
        self.writer.submit(decision)

        # .. and return the outcome together with the id the log will carry.
        out = {
            'decision_id': decision_id,
            'outcome':     outcome,
            'actual':      actual,
            'fired':       fired,
            'error':       error,
            'duration_ms': duration_ms,
        }
        return out

# ################################################################################################################################
# ################################################################################################################################
