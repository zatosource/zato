# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# ################################################################################################################################
# ################################################################################################################################

template_complex_03 = """
pubsub_topic:

# ################################################################################################################################

  - depth_check_freq: 100
    has_gd: false
    hook_service_name: helpers.pubsub.hook
    is_active: true
    is_api_sub_allowed: false
    is_internal: false
    max_depth_gd: 10000
    max_depth_non_gd: 1000
    name: /test/complex-03/001/{test_suffix}
    on_no_subs_pub: drop
    task_delivery_interval: 2000
    task_sync_interval: 500

  - depth_check_freq: 100
    has_gd: false
    hook_service_name: helpers.pubsub.hook
    is_active: true
    is_api_sub_allowed: false
    is_internal: false
    max_depth_gd: 10000
    max_depth_non_gd: 1000
    name: /test/complex-03/002/{test_suffix}
    on_no_subs_pub: accept
    task_delivery_interval: 2000
    task_sync_interval: 500

# ################################################################################################################################

  - depth_check_freq: 100
    has_gd: false
    hook_service_name: helpers.pubsub.hook
    is_active: true
    is_api_sub_allowed: false
    is_internal: false
    max_depth_gd: 10000
    max_depth_non_gd: 1000
    name: /test/complex-03/003/{test_suffix}
    on_no_subs_pub: drop
    task_delivery_interval: 2000
    task_sync_interval: 500

  - depth_check_freq: 100
    has_gd: false
    hook_service_name: helpers.pubsub.hook
    is_active: true
    is_api_sub_allowed: false
    is_internal: false
    max_depth_gd: 10000
    max_depth_non_gd: 1000
    name: /test/complex-03/004/{test_suffix}
    on_no_subs_pub: accept
    task_delivery_interval: 2000
    task_sync_interval: 500

# ################################################################################################################################

"""

# ################################################################################################################################
# ################################################################################################################################
