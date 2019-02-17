# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing
from copy import deepcopy
from logging import getLogger

# Bunch
from bunch import bunchify

# nose
from nose.tools import eq_

# Python 2/3 compatibility
from future.utils import iteritems

# Zato
from zato.common.odb.model import Cluster, Service as ServiceModel
from zato.server.service import AsIs, CSV, Dict, Float, ForceType, Integer, List, ListOfDicts, Service, Unicode, UTC

logger = getLogger(__name__)

# ################################################################################################################################

class _TestBase(Service):

    test_data = bunchify({
        'should_as_is': 'True',
        'is_boolean': 'True',
        'should_boolean': 'False',
        'csv1': '1,2,3,4',
        'dict': {'a':'b', 'c':'d'},
        'float': '2.3',
        'integer': '190',
        'integer2': '0',
        'list': ['1', '2', '3'],
        'list_of_dicts': [{'1':'11', '2':'22'}, {'3':'33'}, {'4':'44', '5':'55', '3':'33', '2':'22', '1':'11'}],
        'unicode1': 'zzzä',
        'unicode2': 'zä',
        'utc': '2012-01-12T03:12:19+00:00'
    })

    class SimpleIO:
        input_required = (AsIs('should_as_is'), 'is_boolean', 'should_boolean', CSV('csv1'), Dict('dict'), Float('float'),
            Integer('integer'), Integer('integer2'), List('list'), ListOfDicts('list_of_dicts'), Unicode('unicode1'),
            Unicode('unicode2'), UTC('utc'))

        output_required = (AsIs('should_as_is'), 'is_boolean', 'should_boolean', CSV('csv1'), CSV('csv2'), CSV('csv3'),
            Dict('dict'), Float('float'), Integer('integer'), Integer('integer2'), List('list'), ListOfDicts('list_of_dicts'),
            Unicode('unicode1'), Unicode('unicode2'), UTC('utc'))

    @staticmethod
    def check_json(data, testing_request):

        eq_(data.should_as_is, 'True')
        eq_(data.is_boolean, True)
        eq_(data.should_boolean, False)

        if testing_request:
            eq_(data.csv1, ['1', '2', '3', '4'])
        else:
            eq_(data.csv1, '1,2,3,4')
            eq_(data.csv2, '5,6,7,8')
            eq_(data.csv3, '9,10,11,12')

        eq_(sorted(data.dict.items()), [('a', 'b'), ('c', 'd')])
        eq_(data.float, 2.3)
        eq_(data.integer, 190)
        eq_(data.integer2, 0)
        eq_(data.list, ['1', '2', '3'])

        # Note that in list_of_dicts all the keys will be automatically stringified, as required by JSON

        lod = data.list_of_dicts
        eq_(len(lod), 3)
        eq_(sorted(iteritems(lod[0])), [('1', '11'), ('2', '22')])
        eq_(sorted(iteritems(lod[1])), [('3', '33')])
        eq_(sorted(iteritems(lod[2])), [('1', '11'), ('2', '22'), ('3', '33'), ('4', '44'), ('5', '55')])

        eq_(data.unicode1, 'zzzä')
        eq_(data.unicode2, 'zä')
        eq_(data.utc, '2012-01-12T03:12:19')

    def set_payload_csv(self):
        self.response.payload.csv2 = ['5', '6', '7', '8']
        self.response.payload.csv3 = ('9', '10', '11', '12')

# ################################################################################################################################

class Roundtrip(_TestBase):
    """ Assigns to response all the data received on input.
    """
    def handle(self):
        self.__class__.check_json(self.request.input, True)
        for name in self.SimpleIO.input_required:
            if isinstance(name, ForceType):
                name = name.name
            setattr(self.response.payload, name, self.__class__.test_data[name])
        self.set_payload_csv()

# ################################################################################################################################

class FromDict(_TestBase):
    """ Returns response based on a dictionary.
    """
    def handle(self):
        self.__class__.check_json(self.request.input, True)
        self.response.payload = deepcopy(self.test_data.toDict())
        self.set_payload_csv()

# ################################################################################################################################

class FromSQLAlchemy(Service):
    """ Creates response from an SQLAlchemy model.
    """
    class SimpleIO:
        output_required = ('name', 'is_active', 'impl_name', 'is_internal', Integer('slow_threshold'))

    def handle(self):
        with closing(self.odb.session()) as session:
            self.response.payload = session.query(ServiceModel.name, ServiceModel.is_active,
                ServiceModel.impl_name, ServiceModel.is_internal, ServiceModel.slow_threshold).\
                filter(Cluster.id==ServiceModel.cluster_id).\
                filter(Cluster.id==self.server.cluster_id).\
                filter(ServiceModel.name=='zato.ping').\
                one()
