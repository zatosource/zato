# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

template_scheduler_01 = """

scheduler:

  - name: enmasse.scheduler.one_time.1
    service: demo.ping
    job_type: one_time
    start_date: '2099-06-15 08:00:00'
    is_active: True

  - name: enmasse.scheduler.weeks.1
    service: demo.ping
    job_type: interval_based
    start_date: '2025-01-01 00:00:00'
    weeks: 2

  - name: enmasse.scheduler.repeats.1
    service: demo.ping
    job_type: interval_based
    start_date: '2025-03-10 12:00:00'
    minutes: 30
    repeats: 5

  - name: enmasse.scheduler.extra_list.1
    service: demo.ping
    job_type: interval_based
    start_date: '2025-04-01 06:00:00'
    hours: 1
    extra:
      - key1=value1
      - key2=value2
      - key3=value3

  - name: enmasse.scheduler.extra_string.1
    service: demo.ping
    job_type: interval_based
    start_date: '2025-05-20 18:30:00'
    seconds: 120
    extra: single_extra_value

  - name: enmasse.scheduler.inactive.1
    service: demo.ping
    job_type: interval_based
    start_date: '2025-06-01 00:00:00'
    days: 7
    is_active: false

  - name: enmasse.scheduler.future.1
    service: demo.ping
    job_type: interval_based
    start_date: '2099-12-31 23:59:59'
    minutes: 10

  - name: enmasse.scheduler.no_start_date.1
    service: demo.ping
    job_type: interval_based
    hours: 4

  - name: enmasse.scheduler.callbacks.1
    service: demo.ping
    job_type: interval_based
    start_date: '2026-01-01 00:00:00'
    minutes: 5
    on_success_service: demo.ping
    on_error_service: demo.ping
    on_error_job: enmasse.scheduler.future.1

"""

# ################################################################################################################################
# ################################################################################################################################
