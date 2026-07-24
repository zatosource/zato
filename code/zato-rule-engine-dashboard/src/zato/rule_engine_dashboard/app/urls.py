# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Django
from django.contrib.staticfiles.views import serve as serve_static
from django.urls import path, re_path

# Zato
from zato.rule_engine_dashboard.app.views import auth, decisions, editor, events, notifications, rulesets, screens, tables, \
    test_sets, users, versions, vocabulary

# ################################################################################################################################
# ################################################################################################################################

urlpatterns = [

    # Sign-in and sign-out
    path('login/', auth.login, name='login'),
    path('login/callback/', auth.login_callback, name='login-callback'),
    path('logout/', auth.logout, name='logout'),

    # Static files come through the staticfiles finders, straight from the installed apps
    re_path(r'^static/(?P<path>.*)$', serve_static, {'insecure': True}, name='static'),

    # The screens, one route each
    path('rulesets/', screens.rulesets, name='screen-rulesets'),
    path('editor/', screens.editor, name='screen-editor'),
    path('tables/', screens.tables, name='screen-tables'),
    path('tests/', screens.tests, name='screen-tests'),
    path('versions/', screens.versions, name='screen-versions'),
    path('log/', screens.log, name='screen-log'),
    path('vocabulary/', screens.vocabulary, name='screen-vocabulary'),

    # User management
    path('users/', users.users_list, name='users'),
    path('users/create', users.user_create, name='user-create'),
    path('users/<str:username>/edit', users.user_edit, name='user-edit'),
    path('users/<str:username>/change-password', users.user_change_password, name='user-change-password'),
    path('users/<str:username>/enable', users.user_set_active, {'is_active': True}, name='user-enable'),
    path('users/<str:username>/disable', users.user_set_active, {'is_active': False}, name='user-disable'),
    path('users/<str:username>/delete', users.user_delete, name='user-delete'),

    # One's own account
    path('profile/', users.profile, name='profile'),

    # The event trail
    path('events/', events.events_list, name='events'),

    # Rulesets home
    path('rules/rulesets/', rulesets.ruleset_list, name='rules-ruleset-list'),
    path('rules/search/', rulesets.ruleset_search, name='rules-search'),
    path('rules/feed/', rulesets.ruleset_feed, name='rules-feed'),
    path('rules/rulesets/<int:definition_id>/preview/', rulesets.ruleset_preview, name='rules-ruleset-preview'),
    path('rules/rulesets/<int:definition_id>/publish/', rulesets.ruleset_publish, name='rules-ruleset-publish'),
    path('rules/rulesets/<int:definition_id>/follow/', rulesets.ruleset_follow, name='rules-ruleset-follow'),
    path('rules/rulesets/<int:definition_id>/unfollow/', rulesets.ruleset_unfollow, name='rules-ruleset-unfollow'),
    path('rules/rulesets/<int:definition_id>/seen/', rulesets.ruleset_mark_seen, name='rules-ruleset-seen'),

    # Saved views and recents
    path('rules/views/', rulesets.view_list, name='rules-view-list'),
    path('rules/views/save/', rulesets.view_save, name='rules-view-save'),
    path('rules/views/delete/', rulesets.view_delete, name='rules-view-delete'),
    path('rules/recents/', rulesets.recent_list, name='rules-recent-list'),

    # Vocabulary
    path('rules/vocabulary/bootstrap/', vocabulary.vocabulary_bootstrap, name='rules-vocabulary-bootstrap'),
    path('rules/vocabulary/rename/', vocabulary.term_rename, name='rules-vocabulary-rename'),
    path('rules/vocabulary/where-used/', vocabulary.term_where_used, name='rules-vocabulary-where-used'),
    path('rules/vocabulary/<int:definition_id>/', vocabulary.vocabulary_get, name='rules-vocabulary-get'),
    path('rules/vocabulary/<int:definition_id>/infer/', vocabulary.vocabulary_infer, name='rules-vocabulary-infer'),

    # Editor
    path('rules/editor/validate/', editor.editor_validate, name='rules-editor-validate'),
    path('rules/editor/render/', editor.editor_render, name='rules-editor-render'),
    path('rules/editor/completion/<int:definition_id>/', editor.editor_completion, name='rules-editor-completion'),
    path('rules/editor/save/', editor.editor_save, name='rules-editor-save'),
    path('rules/editor/outcomes/', editor.editor_outcomes, name='rules-editor-outcomes'),

    # Decision tables
    path('rules/tables/validate/', tables.table_validate, name='rules-table-validate'),
    path('rules/tables/compile/', tables.table_compile, name='rules-table-compile'),
    path('rules/tables/checks/', tables.table_checks, name='rules-table-checks'),
    path('rules/tables/expand/', tables.table_expand, name='rules-table-expand'),
    path('rules/tables/compress/', tables.table_compress, name='rules-table-compress'),

    # Versions
    path('rules/rulesets/<int:definition_id>/timeline/', versions.version_timeline, name='rules-version-timeline'),
    path('rules/rulesets/<int:definition_id>/versions/<int:version>/', versions.version_get, name='rules-version-get'),
    path('rules/rulesets/<int:definition_id>/diff/', versions.version_diff, name='rules-version-diff'),
    path('rules/rulesets/<int:definition_id>/rollback/', versions.version_rollback, name='rules-version-rollback'),
    path(
        'rules/rulesets/<int:definition_id>/compare-outcomes/',
        versions.version_compare_outcomes,
        name='rules-version-compare-outcomes',
    ),

    # The decision log
    path('rules/decisions/', decisions.decision_list, name='rules-decision-list'),
    path('rules/decisions/aggregates/', decisions.decision_aggregates, name='rules-decision-aggregates'),
    path('rules/rulesets/<int:definition_id>/rule-counts/', decisions.decision_rule_counts, name='rules-rule-counts'),
    path('rules/decisions/<str:decision_id>/', decisions.decision_detail, name='rules-decision-detail'),
    path(
        'rules/decisions/<str:decision_id>/to-scenario/',
        decisions.decision_to_scenario,
        name='rules-decision-to-scenario',
    ),
    path('rules/decisions/<str:decision_id>/replay/', decisions.decision_replay, name='rules-decision-replay'),

    # Test suites, simulation and champion versus challenger
    path('rules/test-sets/', test_sets.test_set_list, name='rules-test-set-list'),
    path('rules/test-sets/validate/', test_sets.test_set_validate, name='rules-test-set-validate'),
    path('rules/test-sets/<int:test_set_id>/run/', test_sets.test_set_run, name='rules-test-set-run'),
    path('rules/test-sets/<int:test_set_id>/promote/', test_sets.test_set_promote, name='rules-test-set-promote'),
    path('rules/simulation/', test_sets.simulation_run, name='rules-simulation'),
    path('rules/champion-challenger/', test_sets.champion_challenger_run, name='rules-champion-challenger'),

    # Notifications - chat credentials, destinations, the live picker and the event matrix
    path('rules/notifications/chat-config/', notifications.chat_config_status, name='rules-chat-config'),
    path('rules/notifications/chat-config/save/', notifications.chat_config_save, name='rules-chat-config-save'),
    path('rules/notifications/chat-config/test/', notifications.chat_config_test, name='rules-chat-config-test'),
    path('rules/notifications/targets/', notifications.target_list, name='rules-notification-targets'),
    path('rules/notifications/matrix/', notifications.event_matrix, name='rules-notification-matrix'),
    path(
        'rules/rulesets/<int:definition_id>/destinations/',
        notifications.destination_list,
        name='rules-destination-list',
    ),
    path(
        'rules/rulesets/<int:definition_id>/destinations/add/',
        notifications.destination_add,
        name='rules-destination-add',
    ),
    path(
        'rules/notifications/destinations/<int:destination_id>/delete/',
        notifications.destination_delete,
        name='rules-destination-delete',
    ),
]

# ################################################################################################################################
# ################################################################################################################################
