# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# Zato
from zato.common.audit_log.api import AuditSource, Env_Content_Retention_Days, Env_Content_Retention_Days_Prefix, \
    Env_Retention_Days, Env_Retention_Days_Prefix, get_content_retention_days, get_retention_days, \
    get_source_env_suffix

# ################################################################################################################################
# ################################################################################################################################

# What a source that keeps its evidence for years is expected to come back with.
_evidence_retention_days = 7 * 365

# What everything else comes back with when nothing is configured.
_default_retention_days = 30

# ################################################################################################################################
# ################################################################################################################################

def _env_name(prefix:'str', source:'str') -> 'str':
    """ The environment variable one source's retention is configured through.
    """
    suffix = get_source_env_suffix(source)

    out = f'{prefix}{suffix}'
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestRowRetention:

    def test_a_diagnostic_source_keeps_the_common_default(self) -> 'None':
        assert get_retention_days(AuditSource.PubSub) == _default_retention_days

# ################################################################################################################################

    def test_the_b2b_sources_outlive_it(self) -> 'None':

        # What a partner sent and what it signed for settles a dispute that surfaces years later.
        assert get_retention_days(AuditSource.AS2) == _evidence_retention_days
        assert get_retention_days(AuditSource.X12) == _evidence_retention_days

# ################################################################################################################################

    def test_shortening_retention_across_the_board_leaves_the_evidence_alone(self) -> 'None':
        try:
            os.environ[Env_Retention_Days] = '7'

            # The process-wide setting is about diagnostic history ..
            assert get_retention_days(AuditSource.PubSub) == 7
            assert get_retention_days() == 7

            # .. and deleting evidence is a decision made for the source it concerns by name.
            assert get_retention_days(AuditSource.AS2) == _evidence_retention_days

        finally:
            _ = os.environ.pop(Env_Retention_Days, None)

# ################################################################################################################################

    def test_one_source_says_how_long_it_is_kept_for(self) -> 'None':

        env_name = _env_name(Env_Retention_Days_Prefix, AuditSource.AS2)

        try:
            os.environ[env_name] = '90'

            assert get_retention_days(AuditSource.AS2) == 90

            # No other source is affected by it.
            assert get_retention_days(AuditSource.X12) == _evidence_retention_days
            assert get_retention_days(AuditSource.PubSub) == _default_retention_days

        finally:
            _ = os.environ.pop(env_name, None)

# ################################################################################################################################

    def test_a_dashed_source_name_becomes_an_underscored_variable(self) -> 'None':

        env_name = _env_name(Env_Retention_Days_Prefix, AuditSource.REST_Channel)

        assert env_name == 'Zato_Audit_Log_Retention_Days_REST_CHANNEL'

        try:
            os.environ[env_name] = '3'
            assert get_retention_days(AuditSource.REST_Channel) == 3

        finally:
            _ = os.environ.pop(env_name, None)

# ################################################################################################################################
# ################################################################################################################################

class TestContentRetention:

    def test_content_lives_as_long_as_its_rows_by_default(self) -> 'None':
        assert get_content_retention_days(AuditSource.AS2) == 0
        assert get_content_retention_days() == 0

# ################################################################################################################################

    def test_one_source_says_how_long_its_content_is_kept_for(self) -> 'None':

        env_name = _env_name(Env_Content_Retention_Days_Prefix, AuditSource.AS2)

        try:
            os.environ[Env_Content_Retention_Days] = '7'
            os.environ[env_name] = '400'

            # The payload of an AS2 exchange is evidence too, so it may be kept
            # long after the payloads of everything else are gone.
            assert get_content_retention_days(AuditSource.AS2) == 400
            assert get_content_retention_days(AuditSource.PubSub) == 7

        finally:
            _ = os.environ.pop(Env_Content_Retention_Days, None)
            _ = os.environ.pop(env_name, None)

# ################################################################################################################################
# ################################################################################################################################
