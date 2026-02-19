from typing import Any

import os

class TestConfig:
    pubsub_topic_shared: Any
    pubsub_topic_test: Any
    pubsub_topic_name_unique: Any
    pubsub_topic_name_unique_auto_create: Any
    pubsub_topic_name_perf_auto_create: Any
    default_stdout: Any
    current_app: Any
    super_user_name: Any
    super_user_password: Any
    super_user_totp_key: Any
    username_prefix: Any
    random_prefix: Any
    server_address: Any
    server_location: Any
    scheduler_host: Any
    scheduler_port: Any
    scheduler_address: Any
    scheduler_location: Any
    invalid_base_address: Any
