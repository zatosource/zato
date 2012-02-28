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

"""
from __future__ import absolute_import, division, print_function, unicode_literals

# Django
from django.db import models

# Zato
from zato.common.util import make_repr

class Cluster(models.Model):

    repr_to_avoid = ["objects"]

    class Meta:
        db_table = "cluster"

    id = models.AutoField(primary_key=True)
    name = models.CharField(unique=True, max_length=200)
    description = models.CharField(max_length=1000, null=True)
    odb_type = models.CharField(max_length=30)
    odb_host = models.CharField(max_length=200)
    odb_port = models.IntegerField()
    odb_user = models.CharField(max_length=200)
    odb_db_name = models.CharField(max_length=200)
    odb_schema = models.CharField(max_length=200, null=True)
    amqp_host = models.CharField(max_length=200)
    amqp_port = models.IntegerField()
    amqp_user = models.CharField(max_length=200)
    lb_host = models.CharField(max_length=200)
    lb_agent_port = models.IntegerField()

    # Fields below don't need any persistent backend. They are created on-demand
    # in various views and are used in templates. Adding them here makes IDEs
    # happy when it comes to auto-completing names and makes things more obvious
    # when one encounters them in templates, so that someone doesn't need to
    # chase them all over the views.

    # The load-balancer's URI (in fact only the path part) under which its
    # statistics are available, e.g. /zato-lb-stats
    stats_uri = None

    # Port on which the load-balancer's statistics are available. It's equal
    # to the port part in the bind directive of the 'front_http_plain' frontend
    # in zato.config file.
    stats_port = None

    # Flag indicating that load-balancers sees all the backend servers being DOWN.
    all_down = None

    # Flag indicating that load-balancers see some (i.e. at least one of two or more)
    # of the backend servers being DOWN.
    some_down = None

    # Flag indicating that load-balancers see some (i.e. at least one of two or more)
    # of the backend servers being in the MAINT mode.
    some_maint = None

    # A dictionary holding the load-balancer's configuration.
    lb_config = None

    def __repr__(self):
        return make_repr(self)

class Server(models.Model):

    class Meta:
        db_table = "server"
        unique_together = ("id", "name")

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    #host = models.CharField(max_length=200)
    #port = models.IntegerField()
    cluster = models.ForeignKey(Cluster, null=True)
"""