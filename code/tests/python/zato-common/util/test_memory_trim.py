# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import unittest

# Zato
from zato.common.util.memory_trim import MemoryTrimmer, ModuleCtx, start_memory_trimmer

# ################################################################################################################################
# ################################################################################################################################

# How many blocks the heap receives, how large each is and how many of them stay allocated,
# which leaves free pages between the remaining blocks that the allocator does not return by itself.
_block_count = 100_000
_block_size = 4096
_kept_every = 50

# How much of the freed memory a trim must return to the operating system, in MB.
_min_released_mb = 100

# ################################################################################################################################
# ################################################################################################################################

def _get_anonymous_mb() -> 'float':
    """ Returns the resident anonymous memory of this process in MB.
    """
    with open('/proc/self/status') as status_file:
        for line in status_file:
            if line.startswith('RssAnon:'):
                out = int(line.split()[1]) / 1024
                return out

    raise Exception('RssAnon not found in /proc/self/status')

# ################################################################################################################################
# ################################################################################################################################

class MemoryTrimmerTestCase(unittest.TestCase):
    """ Tests for the release of free heap memory to the operating system.
    """

# ################################################################################################################################

    def test_trim_returns_freed_memory(self) -> 'None':

        blocks:'list[bytearray]' = []

        for _ in range(_block_count):
            blocks.append(bytearray(_block_size))

        kept = blocks[::_kept_every]
        del blocks

        before_trim = _get_anonymous_mb()
        MemoryTrimmer().trim()
        after_trim = _get_anonymous_mb()

        self.assertGreater(before_trim - after_trim, _min_released_mb)
        self.assertEqual(len(kept), _block_count // _kept_every)

# ################################################################################################################################

    def test_trimmer_starts_once_per_process(self) -> 'None':

        start_memory_trimmer()
        first = ModuleCtx.Trimmer

        start_memory_trimmer()
        second = ModuleCtx.Trimmer

        self.assertIsNotNone(first)
        self.assertIs(first, second)

# ################################################################################################################################
# ################################################################################################################################
