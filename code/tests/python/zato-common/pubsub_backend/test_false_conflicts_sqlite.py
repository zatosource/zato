# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os

# Zato
from common import pubsub_path_env
from false_conflicts import run_concurrent_publication, run_duplicate_first_writer, run_duplicate_with_unrelated_items, \
    run_rejected_value, run_value_error_classes

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import callable_

    callable_ = callable_

# ################################################################################################################################
# ################################################################################################################################

def _run_scenario(tmp_path:'os.PathLike', scenario:'callable_') -> 'None':
    """ Runs one scenario against a SQLite file of its own.
    """
    db_path = os.path.join(str(tmp_path), 'zato.db')

    with pubsub_path_env(db_path):
        scenario()

# ################################################################################################################################

def test_duplicate_with_unrelated_items(tmp_path:'os.PathLike') -> 'None':
    """ A strict duplicate fails its own fenced acknowledgement alone, next to a publication, push attempts and a lease.
    """
    _run_scenario(tmp_path, run_duplicate_with_unrelated_items)

# ################################################################################################################################

def test_duplicate_first_writer(tmp_path:'os.PathLike') -> 'None':
    """ A strict duplicate fails its own fenced acknowledgement alone when that item is the first writer of its batch.
    """
    _run_scenario(tmp_path, run_duplicate_first_writer)

# ################################################################################################################################

def test_concurrent_publication(tmp_path:'os.PathLike') -> 'None':
    """ A publication of another process during the checks of a fenced acknowledgement waits for the batch to commit.
    """
    _run_scenario(tmp_path, run_concurrent_publication)

# ################################################################################################################################

def test_rejected_value(tmp_path:'os.PathLike') -> 'None':
    """ A value that SQLite rejects in one item fails the caller of that item alone.
    """
    _run_scenario(tmp_path, run_rejected_value)

# ################################################################################################################################

def test_value_error_classes() -> 'None':
    """ The errors of SQLite about the values of a statement are recognized as value errors.
    """
    run_value_error_classes()

# ################################################################################################################################
# ################################################################################################################################
