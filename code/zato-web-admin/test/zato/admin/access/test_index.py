# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
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
    from django.core.urlresolvers import RegexURLPattern

# ################################################################################################################################
# ################################################################################################################################

logging.basicConfig(
    level=logging.INFO, format='%(asctime)s - %(levelname)s - %(process)d:%(threadName)s - %(name)s:%(lineno)d - %(message)s')

logger = logging.getLogger(__name__)

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

    run_in_background = False
    needs_auto_login = True

# ################################################################################################################################

    def test_index(self):

        # Zato
        from zato.admin.urls import urlpatterns

        # All the parameters are in the format of a named regex group, e.g. (?P<cluster_id>.*)
        # which is why searching for '?P' will suffice.
        regex_param_marker = '?P'

        # Paths to collect
        url_paths = set() # type: set[URLPath]

        for item in urlpatterns: # type: RegexURLPattern

            # Skip patterns that have parameters, i.e. ones that are not index pages.
            if regex_param_marker in item._regex:
                continue

            if not item.name:
                continue

            url_path = URLPath()
            url_path.name = item.name
            url_path.path = item._regex.replace('^', '/').replace('$', '')
            url_path.pattern = item._regex

            url_paths.add(url_path)

        url_paths = sorted(url_paths)

        for item in url_paths:
            address = self.config.web_admin_address + item.path + '?cluster=1'
            logger.info('Accessing %s', address)
            self.client.get(address)
            self.client

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
