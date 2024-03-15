# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os
import socket

# Zato
from zato.common.util.api import get_current_user

# ################################################################################################################################

logger = logging.getLogger(__name__)

logger_bzr = logging.getLogger('bzr')
logger_bzr.setLevel(logging.WARN)

logger_sh = logging.getLogger('sh.command')
logger_sh.setLevel(logging.WARN)

# ################################################################################################################################

# We use Bazaar under Zato 3.0 with Python 2.7. Any newer version of Zato, or Zato 3.0 with Python 3.x, uses git.

# ################################################################################################################################
# ################################################################################################################################

class _BaseRepoManager:
    def __init__(self, repo_location='.'):
        self.repo_location = os.path.abspath(os.path.expanduser(repo_location))

# ################################################################################################################################
# ################################################################################################################################

class PassThroughRepoManager(_BaseRepoManager):
    def ensure_repo_consistency(self):
        pass

# ################################################################################################################################
# ################################################################################################################################

class GitRepoManager(_BaseRepoManager):
    def ensure_repo_consistency(self):

        # Use sh for git commands
        import sh

        # Always work in the same directory as the repository is in
        sh.cd(self.repo_location)

        # (Re-)init the repository
        sh.git.init(self.repo_location)

        # Set user info
        current_user = get_current_user()
        sh.git.config('user.name', current_user)
        sh.git.config('user.email', '{}@{}'.format(current_user, socket.getfqdn()))

        # Default branch is called 'main'
        sh.git.checkout('-B', 'main')

        # Add all files
        sh.git.add('-A', self.repo_location)

        output = sh.git.status('--porcelain') # type: str
        output = output.strip()

        # And commit changes if there are any
        if output:
            sh.git.commit('-m', 'Committing latest changes')

# ################################################################################################################################
# ################################################################################################################################

RepoManager = PassThroughRepoManager

# ################################################################################################################################
# ################################################################################################################################
