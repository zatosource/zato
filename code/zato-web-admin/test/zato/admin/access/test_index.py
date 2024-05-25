# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from dataclasses import dataclass
from unittest import main

# Zato
from .base import BaseTestCase

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from django.urls.resolvers import URLPattern
    URLPattern = URLPattern

# ################################################################################################################################
# ################################################################################################################################

logging.basicConfig(
    level=logging.INFO, format='%(asctime)s - %(levelname)s - %(process)d:%(threadName)s - %(name)s:%(lineno)d - %(message)s')

logger = logging.getLogger(__name__)

selenium_logger = logging.getLogger('seleniumwire.handler')
selenium_logger.setLevel(logging.WARN)

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False, order=True, unsafe_hash=True)
class URLPath:
    name: 'str'
    path: 'str'
    pattern: 'str'

# ################################################################################################################################
# ################################################################################################################################

class IndexTestCase(BaseTestCase):

    needs_auto_login = True
    run_in_background = True

# ################################################################################################################################

    def test_index(self):

        # stdlib
        import os

        if not os.environ.get('ZATO_TEST_DASHBOARD'):
            return

        # Zato
        from zato.admin.urls import urlpatterns

        # All the parameters are in the format of a named regex group, e.g. (?P<cluster_id>.*)
        # which is why searching for '?P' will suffice.
        regex_param_marker = '?P'

        # Paths to collect
        url_paths = set() # type: set[URLPath]

        for item in urlpatterns: # type: URLPattern

            pattern = str(item.pattern)

            # Skip patterns that have parameters, i.e. ones that are not index pages.
            if regex_param_marker in pattern:
                continue

            if not item.name:
                continue

            url_path = URLPath()
            url_path.name = item.name
            url_path.path = pattern.replace('^', '/').replace('$', '')
            url_path.pattern = pattern

            url_paths.add(url_path)

        # All the index-like URL paths found ..
        url_paths = sorted(url_paths)

        # .. the list of patterns that point to URL paths that need to be skipped,
        # .. e.g. that appear to be index-like but they are not really.
        to_skip = {

            'basic/save/',
            'cache/builtin/clear',
            'favicon.ico',
            'generate-totp-key',
            'outgoing/redis',
            'pubsub/message/publish-action/',
            'pubsub/task/delivery/', # <----------------- ...

            '/accounts/login',
            '/create/',
            '/change-password/',
            '/config-file/',
            '/data-dict/',
            '/edit/',
            '/logout',

            '/zato/cloud/jira/reset-oauth2-scopes/',
            '/zato/security/oauth/outconn/client-credentials/change-secret/',
            '/zato/security/rbac/role/',
            '/zato/service/ide/create-file/',
            '/zato/service/ide/delete-file/',
            '/zato/service/ide/rename-file/',
            '/zato/service/ide/get-file/',
            '/zato/service/ide/get-file-list/',
            '/zato/service/ide/get-service-list/',
            '/zato/service/upload/',
        }

        # Go through all the paths founds ..
        for item in url_paths:

            # .. by default, assume that we can continue ..
            should_continue = True

            # .. check if we should not actually skip this path ..
            for item_to_skip in to_skip:

                # .. if yes, set the flag accordingly ..
                if item_to_skip in item.path:
                    should_continue = False

            # .. if we are here, it means that we can visit the URL
            # .. and confirm that all of its responses were fine.
            if should_continue:
                address = self.config.web_admin_address + item.path
                logger.info('Accessing %s', address)
                self.client.get(address)
                self.check_response_statuses()

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
