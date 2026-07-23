# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime

# Local
from zato.common.rule_engine.sql import DecisionWrite, RuleSQLBackend
from zato.common.rule_engine.sql.constants import Definition_Type_Ruleset

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.rule_engine.sql.data import anydict, strlist

    anydict = anydict
    strlist = strlist

# ################################################################################################################################
# ################################################################################################################################

# The administrative half of what healthcare rule engines decide - claims, eligibility, enrollment, scheduling.
Admin_Rule_Ids = [
    'in-network-provider',
    'benefit-covered',
    'copay-tier-applied',
    'prior-authorization-on-file',
    'referral-verified',
    'member-enrollment-active',
    'appointment-slot-confirmed',
    'coverage-tier-selected',
]

# The clinical decision-support half - care plans, protocols, order sets, dosing, screenings, follow-ups.
Clinical_Rule_Ids = [
    'care-plan-selected',
    'protocol-step-confirmed',
    'order-set-selected',
    'medication-compatible',
    'dosing-tier-assigned',
    'screening-due',
    'follow-up-scheduled',
    'care-gap-closed',
]

# The outcomes healthy traffic cycles through.
Outcomes = ['approved', 'adjusted', 'routed-for-review']

# The outcome of a failed evaluation.
Error_Outcome = 'error'

# Every this many decisions one is an error, roughly two percent of the traffic.
Error_Every = 50

# How many rules one decision fires.
Fired_Rules_Per_Decision = 3

# The offsets that pick this decision's fired rules from its catalog - pairwise distinct modulo the catalog size.
Fired_Rule_Offsets = [0, 3, 5]

# Neutral administrative story fields the decisions carry.
Plan_Codes  = ['plan-standard', 'plan-plus', 'plan-complete']
Visit_Types = ['telehealth', 'clinic-visit', 'annual-checkup']

# How many rules-version values the traffic spreads over.
Version_Count = 3

# The bounds of the reported per-decision evaluation time.
Duration_Base_Ms   = 2
Duration_Spread_Ms = 40

# Who authored the perf definitions.
Author = 'perf.harness'

# ################################################################################################################################
# ################################################################################################################################

def create_rulesets(backend:'RuleSQLBackend') -> 'tuple[int, int]':
    """ Creates the two rulesets all generated decisions belong to and returns their identities.
    """
    # The administrative ruleset - claims, eligibility, enrollment and scheduling ..
    admin_document = {'rules': Admin_Rule_Ids}
    admin = backend.definitions.create(
        name='Coverage and scheduling',
        object_type=Definition_Type_Ruleset,
        document=admin_document,
        author=Author,
        comment='Create the coverage and scheduling ruleset',
    )

    # .. and the clinical decision-support ruleset - care plans, protocols and screenings.
    clinical_document = {'rules': Clinical_Rule_Ids}
    clinical = backend.definitions.create(
        name='Care plan selection',
        object_type=Definition_Type_Ruleset,
        document=clinical_document,
        author=Author,
        comment='Create the care plan selection ruleset',
    )

    out = admin.id, clinical.id
    return out

# ################################################################################################################################

def catalog_for(index:'int') -> 'strlist':
    """ Returns the rule catalog of this decision - even traffic is administrative, odd is clinical.
    """
    if index % 2 == 0:
        out = Admin_Rule_Ids
    else:
        out = Clinical_Rule_Ids

    return out

# ################################################################################################################################

def business_key_for(index:'int') -> 'str':
    """ Returns the business key of this decision - claims on the administrative side, encounters on the clinical one.
    """
    if index % 2 == 0:
        out = f'claim-{index:07d}'
    else:
        out = f'encounter-{index:07d}'

    return out

# ################################################################################################################################

def fired_rules_for(index:'int') -> 'strlist':
    """ Returns the rules this decision fired - three distinct catalog entries picked deterministically.
    """
    catalog = catalog_for(index)
    catalog_size = len(catalog)

    out:'strlist' = []

    for offset in Fired_Rule_Offsets:
        rule_index = (index + offset) % catalog_size
        out.append(catalog[rule_index])

    return out

# ################################################################################################################################

def outcome_for(index:'int') -> 'tuple[str, bool]':
    """ Returns this decision's outcome and whether it is an error.
    """
    if index % Error_Every == 0:
        out = Error_Outcome, True
    else:
        outcome_index = index % len(Outcomes)
        out = Outcomes[outcome_index], False

    return out

# ################################################################################################################################

def duration_for(index:'int') -> 'int':
    """ Returns this decision's reported evaluation time in milliseconds.
    """
    out = Duration_Base_Ms + index % Duration_Spread_Ms
    return out

# ################################################################################################################################

def version_for(index:'int') -> 'int':
    """ Returns this decision's rules version.
    """
    out = 1 + index % Version_Count
    return out

# ################################################################################################################################

def story_for(index:'int', outcome:'str', fired_rule_ids:'strlist') -> 'anydict':
    """ Returns the complete neutral story of one decision.
    """
    plan_index = index % len(Plan_Codes)
    visit_index = index % len(Visit_Types)

    out:'anydict' = {
        'input': {
            'member.plan': Plan_Codes[plan_index],
            'visit.type': Visit_Types[visit_index],
            'provider.network_flag': 'in-network',
            'coverage.tier': 1 + index % 3,
        },
        'output': {
            'decision.outcome': outcome,
            'protocol.identifier': f'protocol-{index % 20:03d}',
        },
        'fired_rule_ids': fired_rule_ids,
        'messages': ['The evaluation completed.'],
    }
    return out

# ################################################################################################################################

def build_decision(index:'int', ruleset_ids:'tuple[int, int]', occurred_at:'datetime', prefix:'str') -> 'DecisionWrite':
    """ Builds one complete generated decision for the given traffic index.
    """
    # Even traffic goes to the administrative ruleset, odd to the clinical one ..
    if index % 2 == 0:
        ruleset_id = ruleset_ids[0]
    else:
        ruleset_id = ruleset_ids[1]

    # .. and every field derives deterministically from the index, so expected totals are exact.
    fired_rule_ids = fired_rules_for(index)
    outcome, is_error = outcome_for(index)
    story = story_for(index, outcome, fired_rule_ids)

    out = DecisionWrite(
        decision_id=f'{prefix}-{index:08d}',
        ruleset_id=ruleset_id,
        rules_version=version_for(index),
        occurred_at=occurred_at,
        business_key=business_key_for(index),
        outcome=outcome,
        is_error=is_error,
        duration_ms=duration_for(index),
        story=story,
        fired_rule_ids=fired_rule_ids,
    )
    return out

# ################################################################################################################################
# ################################################################################################################################
