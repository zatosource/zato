# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

Definition_Type_Ruleset    = 'ruleset'
Definition_Type_Vocabulary = 'vocabulary'

Definition_Types = (
    Definition_Type_Ruleset,
    Definition_Type_Vocabulary,
)

# ################################################################################################################################

System_Actor    = 'zato.rule-engine'
Root_Parent_Key = 0

# The key under which a stored ruleset document keeps its canonical rule documents.
Documents_Key = 'documents'

Default_Search_Limit = 100

# ################################################################################################################################
# ################################################################################################################################
