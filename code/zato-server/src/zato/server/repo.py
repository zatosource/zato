# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at gefira.pl>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging

# PyYAML
from yaml import dump, Loader, Dumper

# Bazaar
import bzrlib
from bzrlib.bzrdir import BzrDir
from bzrlib.workingtree import WorkingTree

# Zato
from zato.common.util import pprint

class RepoManager(object):
    def __init__(self, repo_location=None, sql_pool_list_location=None,
                 job_list_location=None):
        self.repo_location = repo_location
        self.sql_pool_list_location = sql_pool_list_location
        self.job_list_location = job_list_location
        self.logger = logging.getLogger("%s.%s" % (__name__, self.__class__.__name__))

    def ensure_repo_consistency(self):
        """ Makes sure the self.repo_location directory is a Bazaar branch.
        The repo and Bazaar branch will be created if they don't already exist.
        Any unknown or modified files will be commited to the branch.
        """
        try:
            BzrDir.open(self.repo_location)
        except bzrlib.errors.NotBranchError, e:
            self.logger.info("Location [%s] is not a Bazaar branch. Will turn it into one." % self.repo_location)
            BzrDir.create_branch_convenience(self.repo_location)

        self.tree = WorkingTree.open(self.repo_location)
        delta = self.tree.changes_from(self.tree.basis_tree(), want_unversioned=True)

        self.logger.debug("tree [%s]" % self.tree)
        self.logger.debug("delta [%s]" % delta)

        for file_info in delta.unversioned:
            self.logger.debug("unversioned [%s]" % (file_info,))
            file_name = file_info[0]
            self.tree.add(file_name)

        if delta.unversioned:
            self.tree.commit("Added new unversioned files.")
        else:
            self.logger.debug("No unversioned files found.")

        if delta.modified:
            self.tree.commit("Committed modified files.")
        else:
            self.logger.debug("No modified files found.")

    def _update(self, top_level_elem, elems, location, before_commit_msg, commit_msg,
                after_commit_msg):
        """ A common utility method for updating a YAML file in the server's
        Bazaar repo.
        """

        # TODO: Commit message could be a tad smarter and might include some
        # hints as to what gets committed to repo.

        # TODO: Move it elsewhere, to a separate 'init' method (or investigage
        # why creating the 'tree' object in 'ensure_repo_consistency is not
        # enough - possibly because we're using subprocesses and our own process
        # is not the same that ensure_repo_consistency has been called in).
        if not hasattr(self, "tree"):
            self.tree = WorkingTree.open(self.repo_location)

        data = {}
        data[top_level_elem] = elems

        data_pprinted = pprint(data)
        output = dump(data, Dumper=Dumper, default_flow_style=False)

        self.logger.debug(before_commit_msg)
        self.logger.debug("data_pprinted=[%s], output=[%s], location=[%s]" % (data_pprinted, output, location))

        open(location, "w").write(output)
        self.tree.commit(commit_msg)

        self.logger.debug(after_commit_msg)

    def update_sql_pool_list(self, pool_list):
        self._update("sql_pool_list", pool_list, self.sql_pool_list_location,
                     "About to update an SQL pool list", "Updated SQL pool list",
                     "Changes to the SQL pool list committed.")

    def update_job_list(self, job_list):
        self._update("job_list", job_list, self.job_list_location,
                     "About to update a job list.", "Updated job list.",
                     "Changes to the job list committed.")

    def update_service_store_config(self, service_store_config):
        self._update("services", service_store_config, self.service_store_config_location,
                     "About to update a list of services available.",
                     "Updated a list of services available.",
                     "Changes to the list of services committed.")