# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# Zato
from zato.common.db_env.common import get_env_value

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The environment variables overriding how long fully delivered messages are kept.
    Env_Delivered_Max_Messages = 'Zato_PubSub_Delivered_Max_Messages'
    Env_Delivered_Max_Days     = 'Zato_PubSub_Delivered_Max_Days'

    # The environment variable overriding for how many days a message ID is recognized as a repeat.
    Env_Dedup_Window_Days = 'Zato_PubSub_Dedup_Window_Days'

    # The environment variable overriding how many rows one bulk statement may touch.
    Env_Batch_Size = 'Zato_PubSub_Batch_Size'

    # The names under which the same variable is read, in this order, when it is not set.
    Env_Batch_Size_Aliases = ('Zato_PubSub_DB_Batch_Size',)

    # The environment variable overriding how many messages the publications and acknowledgements
    # of one group commit refer to at most.
    Env_Commit_Max_Messages = 'Zato_PubSub_Commit_Max_Messages'

    # The environment variable overriding how many group commits may be in progress at once.
    Env_Commits_In_Flight = 'Zato_PubSub_Commits_In_Flight'

    # The environment variable with how long the messages of a pull wait for their acknowledgement, in seconds,
    # before the next pull hands them out again.
    Env_Pull_Lease_Seconds = 'Zato_PubSub_Pull_Lease_Seconds'

# ################################################################################################################################

# How long the messages of a pull wait for their acknowledgement, in seconds.
Default_Pull_Lease_Seconds = 30

# How many fully delivered messages one topic may retain for browsing and statistics.
Default_Delivered_Max_Messages = 1_000_000

# How many days a fully delivered message is retained for browsing and statistics.
Default_Delivered_Max_Days = 7

# For how many days a message ID is recognized as a repeat, independently of whether its message is still retained.
Default_Dedup_Window_Days = 7

# How many rows one bulk delete or update statement may touch.
_default_batch_size = 5_000

# How many messages the publications and acknowledgements of one group commit refer to at most.
Default_Commit_Max_Messages = 500

# How many group commits may be in progress at once.
Default_Commits_In_Flight = 2

# How many group commits of publications may be in progress in addition to the ones above,
# so that a publication does not wait for a commit of acknowledgements.
Urgent_Commits_In_Flight = 1

# ################################################################################################################################
# ################################################################################################################################

def get_delivered_max_messages() -> 'int':
    """ Returns how many fully delivered messages one topic may retain.
    """
    if value := os.environ.get(ModuleCtx.Env_Delivered_Max_Messages, ''):
        out = int(value)
    else:
        out = Default_Delivered_Max_Messages

    return out

# ################################################################################################################################

def get_delivered_max_days() -> 'int':
    """ Returns how many days a fully delivered message is retained.
    """
    if value := os.environ.get(ModuleCtx.Env_Delivered_Max_Days, ''):
        out = int(value)
    else:
        out = Default_Delivered_Max_Days

    return out

# ################################################################################################################################

def get_dedup_window_days() -> 'int':
    """ Returns for how many days a message ID is recognized as a repeat.
    """
    if value := os.environ.get(ModuleCtx.Env_Dedup_Window_Days, ''):
        out = int(value)
    else:
        out = Default_Dedup_Window_Days

    return out

# ################################################################################################################################

def get_batch_size() -> 'int':
    """ Returns how many rows one bulk delete or update statement may touch.
    """
    if value := get_env_value(ModuleCtx.Env_Batch_Size, ModuleCtx.Env_Batch_Size_Aliases):
        out = int(value)
    else:
        out = _default_batch_size

    return out

# ################################################################################################################################

def get_commit_max_messages() -> 'int':
    """ Returns how many messages the publications and acknowledgements of one group commit refer to at most.
    """
    if value := os.environ.get(ModuleCtx.Env_Commit_Max_Messages, ''):
        out = int(value)
    else:
        out = Default_Commit_Max_Messages

    return out

# ################################################################################################################################

def get_pull_lease_seconds() -> 'int':
    """ Returns how long the messages of a pull wait for their acknowledgement before they are handed out again.
    """
    if value := os.environ.get(ModuleCtx.Env_Pull_Lease_Seconds, ''):
        out = int(value)
    else:
        out = Default_Pull_Lease_Seconds

    return out

# ################################################################################################################################

def get_commits_in_flight() -> 'int':
    """ Returns how many group commits may be in progress at once.
    """
    if value := os.environ.get(ModuleCtx.Env_Commits_In_Flight, ''):
        out = int(value)
    else:
        out = Default_Commits_In_Flight

    return out

# ################################################################################################################################
# ################################################################################################################################
