# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import TestCase, main

# Zato - Rust extension
import zato_scheduler_core

# ################################################################################################################################
# ################################################################################################################################

class TestSchedulerClassExports(TestCase):
    """Verifies that the Rust extension exposes the Scheduler class with all expected methods."""

    def test_scheduler_class_exists(self):
        assert hasattr(zato_scheduler_core, 'Scheduler')

# ################################################################################################################################

    def test_start_is_callable(self):
        assert callable(getattr(zato_scheduler_core.Scheduler, 'start'))

# ################################################################################################################################

    def test_stop_is_callable(self):
        assert callable(getattr(zato_scheduler_core.Scheduler, 'stop'))

# ################################################################################################################################

    def test_create_job_is_callable(self):
        assert callable(getattr(zato_scheduler_core.Scheduler, 'create_job'))

# ################################################################################################################################

    def test_edit_job_is_callable(self):
        assert callable(getattr(zato_scheduler_core.Scheduler, 'edit_job'))

# ################################################################################################################################

    def test_delete_job_is_callable(self):
        assert callable(getattr(zato_scheduler_core.Scheduler, 'delete_job'))

# ################################################################################################################################

    def test_execute_job_is_callable(self):
        assert callable(getattr(zato_scheduler_core.Scheduler, 'execute_job'))

# ################################################################################################################################

    def test_mark_complete_is_callable(self):
        assert callable(getattr(zato_scheduler_core.Scheduler, 'mark_complete'))

# ################################################################################################################################

    def test_reload_is_callable(self):
        assert callable(getattr(zato_scheduler_core.Scheduler, 'reload'))

# ################################################################################################################################

    def test_get_history_page_is_callable(self):
        assert callable(getattr(zato_scheduler_core.Scheduler, 'get_history_page'))

# ################################################################################################################################

    def test_get_history_since_is_callable(self):
        assert callable(getattr(zato_scheduler_core.Scheduler, 'get_history_since'))

# ################################################################################################################################

    def test_get_job_summaries_is_callable(self):
        assert callable(getattr(zato_scheduler_core.Scheduler, 'get_job_summaries'))

# ################################################################################################################################

    def test_get_log_entries_is_callable(self):
        assert callable(getattr(zato_scheduler_core.Scheduler, 'get_log_entries'))

# ################################################################################################################################

    def test_get_run_detail_is_callable(self):
        assert callable(getattr(zato_scheduler_core.Scheduler, 'get_run_detail'))

# ################################################################################################################################

    def test_get_timeline_events_is_callable(self):
        assert callable(getattr(zato_scheduler_core.Scheduler, 'get_timeline_events'))

# ################################################################################################################################

    def test_append_log_entry_is_callable(self):
        assert callable(getattr(zato_scheduler_core.Scheduler, 'append_log_entry'))

# ################################################################################################################################
# ################################################################################################################################

class TestSchedulerInstantiation(TestCase):
    """Verifies that a Scheduler instance can be created without a running loop."""

    def test_scheduler_can_be_instantiated(self):
        s = zato_scheduler_core.Scheduler()
        self.assertIsInstance(s, zato_scheduler_core.Scheduler)

# ################################################################################################################################

    def test_reload_without_config_store_raises(self):
        s = zato_scheduler_core.Scheduler()
        with self.assertRaises(AttributeError):
            s.reload()

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()
