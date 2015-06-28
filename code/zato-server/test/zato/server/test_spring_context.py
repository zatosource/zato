# -*- coding: utf-8 -*-

"""
Copyright (C) 2015 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from unittest import TestCase

# Bunch
from bunch import Bunch, bunchify

# Spring Python
from springpython.context import ApplicationContext

# Zato
from zato.server.spring_context import ZatoContext

# ################################################################################################################################

class ZatoContextTestCase(TestCase):

# ################################################################################################################################

    def test_content_types(self):
        ctx = ApplicationContext(ZatoContext())

        self.assertEquals(ctx.get_object('soap11_content_type'), 'text/xml')
        self.assertEquals(ctx.get_object('soap12_content_type'), 'application/soap+xml; charset=utf-8')
        self.assertEquals(ctx.get_object('plain_xml_content_type'), 'application/xml')
        self.assertEquals(ctx.get_object('json_content_type'), 'application/json')

# ################################################################################################################################

    def test_startup_jobs(self):
        ctx = ApplicationContext(ZatoContext())

        jobs = Bunch()

        for item in bunchify(ctx.get_object('startup_jobs')):
            jobs[item.name] = item

        self.assertEquals(len(jobs), 10)

        self.assertEquals(jobs['zato.outgoing.sql.auto-ping'].minutes, 3)
        self.assertEquals(jobs['zato.outgoing.sql.auto-ping'].service, 'zato.outgoing.sql.auto-ping')

        self.assertEquals(jobs['zato.stats.aggregate-by-day'].minutes, 60)
        self.assertEquals(jobs['zato.stats.aggregate-by-day'].service, 'zato.stats.aggregate-by-day')

        self.assertEquals(jobs['zato.stats.aggregate-by-hour'].minutes, 10)
        self.assertEquals(jobs['zato.stats.aggregate-by-hour'].service, 'zato.stats.aggregate-by-hour')

        self.assertEquals(jobs['zato.stats.aggregate-by-minute'].seconds, 60)
        self.assertEquals(jobs['zato.stats.aggregate-by-minute'].service, 'zato.stats.aggregate-by-minute')

        self.assertEquals(jobs['zato.stats.aggregate-by-month'].minutes, 60)
        self.assertEquals(jobs['zato.stats.aggregate-by-month'].service, 'zato.stats.aggregate-by-month')

        self.assertEquals(jobs['zato.stats.process-raw-times'].seconds, 90)
        self.assertEquals(jobs['zato.stats.process-raw-times'].service, 'zato.stats.process-raw-times')
        self.assertEquals(jobs['zato.stats.process-raw-times'].extra, 'max_batch_size=99999')

        self.assertEquals(jobs['zato.stats.summary.create-summary-by-day'].minutes, 10)
        self.assertEquals(jobs['zato.stats.summary.create-summary-by-day'].service, 'zato.stats.summary.create-summary-by-day')

        self.assertEquals(jobs['zato.stats.summary.create-summary-by-month'].minutes, 60)
        self.assertEquals(jobs['zato.stats.summary.create-summary-by-month'].service, 'zato.stats.summary.create-summary-by-month')

        self.assertEquals(jobs['zato.stats.summary.create-summary-by-week'].minutes, 10)
        self.assertEquals(jobs['zato.stats.summary.create-summary-by-week'].service, 'zato.stats.summary.create-summary-by-week')

        self.assertEquals(jobs['zato.stats.summary.create-summary-by-year'].minutes, 60)
        self.assertEquals(jobs['zato.stats.summary.create-summary-by-year'].service, 'zato.stats.summary.create-summary-by-year')

# ################################################################################################################################
