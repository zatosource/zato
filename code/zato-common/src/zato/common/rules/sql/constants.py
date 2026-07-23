# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

Definition_Type_Ruleset        = 'ruleset'
Definition_Type_Sentence_Rule  = 'sentence-rule'
Definition_Type_Decision_Table = 'decision-table'
Definition_Type_Vocabulary     = 'vocabulary'
Definition_Type_Test_Set       = 'test-set'

Definition_Types = (
    Definition_Type_Ruleset,
    Definition_Type_Sentence_Rule,
    Definition_Type_Decision_Table,
    Definition_Type_Vocabulary,
    Definition_Type_Test_Set,
)

# ################################################################################################################################

Event_Type_Definition_Created   = 'definition.created'
Event_Type_Definition_Updated   = 'definition.updated'
Event_Type_Definition_Archived  = 'definition.archived'
Event_Type_Version_Created      = 'version.created'
Event_Type_Version_Published    = 'version.published'
Event_Type_Version_Restored     = 'version.restored'
Event_Type_Review_Commented     = 'review.commented'
Event_Type_State_Changed        = 'state.changed'
Event_Type_Follow_Changed       = 'follow.changed'
Event_Type_Test_Run             = 'test.run'
Event_Type_Rule_Fired_Daily     = 'rule.fired.daily'

# ################################################################################################################################

System_Actor    = 'zato.rule-engine'
Root_Parent_Key = 0

# The key under which a stored ruleset document keeps its canonical rule documents.
Documents_Key = 'documents'

# ################################################################################################################################

Default_Batch_Size              = 200
Default_Buffer_Capacity         = 10_000
Default_Flush_Interval_Seconds  = 0.25
Default_Retention_Chunk_Size    = 500
Default_Success_Capture_Percent = 100

Minimum_Capture_Percent = 0
Maximum_Capture_Percent = 100

Default_Feed_Limit   = 100
Default_Recent_Limit = 20
Default_Search_Limit = 100

# ################################################################################################################################

Hour_Bucket_Format = '%Y-%m-%dT%H'
Day_Bucket_Format  = '%Y-%m-%d'

# ################################################################################################################################
# ################################################################################################################################
