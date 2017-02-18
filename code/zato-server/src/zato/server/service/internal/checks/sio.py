# -*- coding: utf-8 -*-

"""
Copyright (C) 2013 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# Nose
from nose.tools import eq_

# Zato
from zato.server.service import AsIs, CSV, Bool, Boolean, Dict, fixed_width as fw, Int, Integer, List, ListOfDicts, Nested, \
     Service, Unicode, UTC
from zato.server.service.internal.checks import CheckService

# ################################################################################################################################

def _test_nested(msg):
    eq_(msg.meta.limit, 111)
    eq_(msg.meta.next, 'abc')
    eq_(msg.meta.offset, 30)
    eq_(msg.meta.previous, 'zxc')
    eq_(msg.meta.total_count, 9090)

    eq_(msg.objects.also_known_as, [1, 22, 333, 444])
    eq_(msg.objects.catchment, 'my-catchment')
    eq_(msg.objects.description, 'my-description')
    eq_(msg.objects.emails, [
        {'comment':'comment', 'confidential':'confidential', 'email':'email'},
        {'comment':'comment2', 'confidential':'confidential2', 'email':'email2'}])
    eq_(msg.objects.id, 123)
    eq_(msg.objects.is_mobile, True)
    eq_(msg.objects.last_updated, '2013-12-15')
    eq_(msg.objects.location.building, 'my-building')
    eq_(msg.objects.location.confidential, True)
    eq_(msg.objects.location.flat_number, '12')
    eq_(msg.objects.location.level, '5')
    eq_(msg.objects.location.point.lat, '90.0')
    eq_(msg.objects.location.point.non, '10.0')
    eq_(msg.objects.location.postcode, '123456')
    eq_(msg.objects.location.state, 'my-state')
    eq_(msg.objects.location.street_name, 'my-street_name')
    eq_(msg.objects.location.street_number, '23')
    eq_(msg.objects.location.street_suffix, 'my-street_suffix')
    eq_(msg.objects.location.street_type, 'my-street_type')
    eq_(msg.objects.location.suburb, 'my-suburb')
    eq_(msg.objects.location.unit, 'my-unit')
    eq_(msg.objects.name, 'my-name')
    eq_(msg.objects.ndis_approved, False)
    eq_(msg.objects.organisation.id, 123)
    eq_(msg.objects.organisation.name, 'my-org-name')
    eq_(msg.objects.parking_info, 'my-parking_info')
    eq_(msg.objects.phones, [
        {'comment': 'comment1', 'confidential': True, 'kind': 'kind1', 'number': 'number1'},
        {'comment': 'comment2', 'confidential': False, 'kind': 'kind2', 'number': 'number2'}])
    eq_(msg.objects.postal_address.confidential, True)
    eq_(msg.objects.postal_address.line1, 'my-line1')
    eq_(msg.objects.postal_address.line2, 'my-line2')
    eq_(msg.objects.postal_address.postcode, 'my-postcode')
    eq_(msg.objects.postal_address.state, 'my-state')
    eq_(msg.objects.postal_address.suburb, 'my-suburb')
    eq_(msg.objects.provider_type, 'my-provider_type')
    eq_(msg.objects.public_transport_info, 'my-public_transport_info')
    eq_(msg.objects.type, 'my-type')
    eq_(msg.objects.web, 'example.org')

def _get_nested_msg():
    return {
        'meta': {
            'limit': 111,
            'next': 'abc',
            'offset': 30,
            'previous': 'zxc',
            'total_count': 9090
        },
        'objects': {
            'also_known_as': [1, 22, 333, 444],
            'catchment': 'my-catchment',
            'description': 'my-description',
            'emails': [{'comment':'comment', 'confidential':'confidential', 'email':'email'},
                       {'comment':'comment2', 'confidential':'confidential2', 'email':'email2'}],
            'id': 123,
            'is_mobile': True,
            'last_updated': '2013-12-15',
            'location': {
                'building': 'my-building',
                'confidential': True,
                'flat_number': '12',
                'level': '5',
                'point': {
                    'lat': '90.0',
                    'non': '10.0',
                },
                'postcode': '123456',
                'state': 'my-state',
                'street_name': 'my-street_name',
                'street_number': '23',
                'street_suffix': 'my-street_suffix',
                'street_type': 'my-street_type',
                'suburb': 'my-suburb',
                'unit': 'my-unit',
            },
            'name': 'my-name',
            'ndis_approved': False,
            'organisation': {
                'id': 123,
                'name': 'my-org-name'
            },
            'parking_info': 'my-parking_info',
            'phones': [{'comment': 'comment1', 'confidential': True, 'kind': 'kind1', 'number': 'number1'},
                       {'comment': 'comment2', 'confidential': False, 'kind': 'kind2', 'number': 'number2'}],
            'postal_address': {
                'confidential': True,
                'line1': 'my-line1',
                'line2': 'my-line2',
                'postcode': 'my-postcode',
                'state': 'my-state',
                'suburb': 'my-suburb'
            },
            'provider_type': 'my-provider_type',
            'public_transport_info': 'my-public_transport_info',
            'type': 'my-type',
            'web': 'example.org',
        }
    }

def _get_sio_msg():

    meta = (Int('limit'), 'next', Int('offset'), 'previous',
            Int('total_count'))

    location = Nested('location', 'building', Bool('confidential'),
        'flat_number', 'level', Dict('point', 'lat', 'non'), 'postcode',
        'state','street_name','street_number', 'street_suffix',
        'street_type', 'suburb', 'unit')

    phones = ListOfDicts('phones', 'comment', Bool('confidential'),
        'kind', 'number')

    postal_address = Dict('postal_address', Bool('confidential'),
        'line1', 'line2', 'postcode', 'state', 'suburb')

    objects = (List('also_known_as'), 'catchment', 'description',
            ListOfDicts('emails'), Int('id'), Bool('is_mobile'),
            'last_updated', location, 'name', Bool('ndis_approved'),
            Dict('organisation', 'id', 'name'), 'parking_info', phones,
            postal_address, 'provider_type', 'public_transport_info',
            'type', 'web')

    return [Nested('meta', meta), Nested('objects', objects)]

# ################################################################################################################################

class CheckTargetService(Service):
    def set_payload(self):
        raise NotImplementedError()

    def after_handle(self):
        self.set_payload()

# ################################################################################################################################

class AsIsService(CheckTargetService):

    class SimpleIO:
        input_required = (AsIs('id'), AsIs('a_id'), AsIs('b_count'), AsIs('c_size'), AsIs('d_timeout'),
                          AsIs('is_e'), AsIs('needs_f'), AsIs('should_g'))
        output_required = (AsIs('id'), AsIs('a_id'), AsIs('b_count'), AsIs('c_size'), AsIs('d_timeout'),
                          AsIs('is_e'), AsIs('needs_f'), AsIs('should_g'))

    def handle(self):
        eq_(self.request.input.id, 'id1')
        eq_(self.request.input.a_id, 'a1')
        eq_(self.request.input.b_count, 'b1')
        eq_(self.request.input.c_size, 'c1')
        eq_(self.request.input.d_timeout, 'd1')
        eq_(self.request.input.is_e, 'e1')
        eq_(self.request.input.needs_f, 'f1')
        eq_(self.request.input.should_g, 'g1')

    def set_payload(self):
        self.response.payload.id = 'id2'
        self.response.payload.a_id = 'a2'
        self.response.payload.b_count = 'b2'
        self.response.payload.c_size = 'c2'
        self.response.payload.d_timeout = 'd2'
        self.response.payload.is_e = 'e2'
        self.response.payload.needs_f = 'f2'
        self.response.payload.should_g = 'g2'

# ################################################################################################################################

class BooleanService(CheckTargetService):

    class SimpleIO:
        input_required = (Boolean('bool1'), Boolean('bool2'))
        output_required = (Boolean('bool1'), Boolean('bool2'))

    def handle(self):
        eq_(self.request.input.bool1, True)
        eq_(self.request.input.bool2, False)

    def set_payload(self):
        self.response.payload.bool1 = False
        self.response.payload.bool2 = True

# ################################################################################################################################

class CSVService(CheckTargetService):

    class SimpleIO:
        input_required = (CSV('csv1'), CSV('csv2'))
        output_required = (CSV('csv3'), CSV('csv4'))

    def handle(self):
        eq_(self.request.input.csv1, ['1', '11', '111', '1111'])
        eq_(self.request.input.csv2, ['2', '22', '222', '2222'])

    def set_payload(self):
        self.response.payload.csv3 = ['3', '33', '333', '3333']
        self.response.payload.csv4 = ['4', '44', '444', '4444']

# ################################################################################################################################

class DictService(CheckTargetService):

    class SimpleIO:
        input_required = (Dict('dict1'), Dict('dict2'))
        output_required = (Dict('dict3'), Dict('dict4'))

    def handle(self):
        eq_(self.request.input.dict1['key1_1'], 'value1_1')
        eq_(self.request.input.dict1['key1_2'], 'value1_2')

        eq_(self.request.input.dict2['key2_1'], 'value2_1')
        eq_(self.request.input.dict2['key2_2'], 'value2_2')

    def set_payload(self):
        self.response.payload.dict3 = {'key3_1': 'value3_1', 'key3_2':'value3_2'}
        self.response.payload.dict4 = {'key4_1': 'value4_1', 'key4_2':'value4_2'}

# ################################################################################################################################

class IntegerService(CheckTargetService):

    class SimpleIO:
        input_required = (Integer('int1'), Integer('int2'))
        output_required = (Integer('int3'), Integer('int4'))

    def handle(self):
        eq_(self.request.input.int1, 1)
        eq_(self.request.input.int2, 2)

    def set_payload(self):
        self.response.payload.int3 = 3
        self.response.payload.int4 = 4

# ################################################################################################################################

class ListService(CheckTargetService):

    class SimpleIO:
        input_required = (List('list1'), List('list2'))
        output_required = (List('list3'), List('list4'))

    def handle(self):
        eq_(self.request.input.list1, ['1', '2', '3'])
        eq_(self.request.input.list2, ['4', '5', '6'])

    def set_payload(self):
        self.response.payload.list3 = ['7', '8', '9']
        self.response.payload.list4 = ['10', '11', '12']

# ################################################################################################################################

class ListOfDictsService(CheckTargetService):

    class SimpleIO:
        input_required = (ListOfDicts('lod1'), ListOfDicts('lod2'))
        output_required = (ListOfDicts('lod3'), ListOfDicts('lod4'))

    def handle(self):
        eq_(self.request.input.lod1[0]['k111'], 'v111')
        eq_(self.request.input.lod1[0]['k112'], 'v112')
        eq_(self.request.input.lod1[1]['k121'], 'v121')
        eq_(self.request.input.lod1[1]['k122'], 'v122')

        eq_(self.request.input.lod2[0]['k211'], 'v211')
        eq_(self.request.input.lod2[0]['k212'], 'v212')
        eq_(self.request.input.lod2[1]['k221'], 'v221')
        eq_(self.request.input.lod2[1]['k222'], 'v222')

    def set_payload(self):
        self.response.payload.lod3 = [{'k311':'v311', 'k312':'v312'}, {'k321':'v321', 'k322':'v322'}]
        self.response.payload.lod4 = [{'k411':'v411', 'k412':'v412'}, {'k421':'v421', 'k422':'v422'}]

# ################################################################################################################################

class NoForceTypeService(CheckTargetService):

    class SimpleIO:
        input_required = ('aa1', 'bb1', 'a_id', 'a_count', 'a_size', 'a_timeout', 'is_b', 'needs_b', 'should_b')
        output_required = ('aa2', 'bb2', 'c_id', 'c_count', 'c_size', 'c_timeout', 'is_d', 'needs_d', 'should_d')

    def handle(self):
        eq_(self.request.input.aa1, 'aa1-value')
        eq_(self.request.input.bb1, 'bb1-value')

        eq_(self.request.input.a_id, 1)
        eq_(self.request.input.a_count, 2)
        eq_(self.request.input.a_size, 3)
        eq_(self.request.input.a_timeout, 4)

        eq_(self.request.input.is_b, True)
        eq_(self.request.input.needs_b, False)
        eq_(self.request.input.should_b, True)

    def set_payload(self):
        self.response.payload.aa2 = 11
        self.response.payload.bb2 = 22

        self.response.payload.c_id = 33
        self.response.payload.c_count = 44
        self.response.payload.c_size = 55
        self.response.payload.c_timeout = 66

        self.response.payload.is_d = False
        self.response.payload.needs_d = True
        self.response.payload.should_d = False

# ################################################################################################################################

class UnicodeService(CheckTargetService):

    class SimpleIO:
        input_required = (Unicode('uni_a'), Unicode('uni_b'))
        output_required = (Unicode('uni_c'), Unicode('uni_d'))

    def handle(self):
        eq_(self.request.input.uni_a, 'a')
        eq_(self.request.input.uni_b, 'b')

    def set_payload(self):
        self.response.payload.uni_c = 'c'
        self.response.payload.uni_d = 'd'

# ################################################################################################################################

class UTCService(CheckTargetService):

    class SimpleIO:
        input_required = (UTC('utc1'), UTC('utc2'))
        output_required = (UTC('utc1'), UTC('utc2'))

    def handle(self):
        eq_(self.request.input.utc1, '2019-01-26T22:33:44')
        eq_(self.request.input.utc2, '2023-12-19T21:31:41')

    def set_payload(self):
        self.response.payload.utc1 = '1234-11-22T01:02:03+00:00'
        self.response.payload.utc2 = '2918-03-19T21:22:23+00:00'

# ################################################################################################################################

class NestedService(CheckTargetService):

    class SimpleIO:
        input_required = _get_sio_msg()
        output_required = _get_sio_msg()

    def handle(self):
        _test_nested(self.request.bunchified())

    def set_payload(self):
        self.response.payload = _get_nested_msg()

# ################################################################################################################################

class CheckSIO(CheckService):

    def json_check_as_is(self):
        response = self.invoke_check_json('zato.checks.sio.as-is-service', {
            'id': 'id1',
            'a_id': 'a1',
            'b_count': 'b1',
            'c_size': 'c1',
            'd_timeout': 'd1',
            'is_e': 'e1',
            'needs_f': 'f1',
            'should_g': 'g1',
        })

        eq_(response.id, 'id2')
        eq_(response.a_id, 'a2')
        eq_(response.b_count, 'b2')
        eq_(response.c_size, 'c2')
        eq_(response.d_timeout, 'd2')
        eq_(response.is_e, 'e2')
        eq_(response.needs_f, 'f2')
        eq_(response.should_g, 'g2')

    def json_check_boolean(self):
        response = self.invoke_check_json('zato.checks.sio.boolean-service', {
            'bool1': True,
            'bool2': False,
        })

        eq_(response.bool1, False)
        eq_(response.bool2, True)

    def json_check_csv(self):
        response = self.invoke_check_json('zato.checks.sio.csv-service', {
            'csv1': '1,11,111,1111',
            'csv2': '2,22,222,2222',
        })

        eq_(response.csv3, '3,33,333,3333')
        eq_(response.csv4, '4,44,444,4444')

    def json_check_dict(self):
        response = self.invoke_check_json('zato.checks.sio.dict-service', {
            'dict1': {'key1_1': 'value1_1', 'key1_2':'value1_2'},
            'dict2': {'key2_1': 'value2_1', 'key2_2':'value2_2'},
        })

        eq_(response.dict3['key3_1'], 'value3_1')
        eq_(response.dict3['key3_2'], 'value3_2')

    def json_check_integer(self):
        response = self.invoke_check_json('zato.checks.sio.integer-service', {
            'int1': 1,
            'int2': 2,
        })

        eq_(response.int3, 3)
        eq_(response.int4, 4)

    def json_check_list(self):
        response = self.invoke_check_json('zato.checks.sio.list-service', {
            'list1': ['1', '2', '3'],
            'list2': ['4', '5', '6'],
        })

        eq_(response.list3, ['7', '8', '9'])
        eq_(response.list4, ['10', '11', '12'])

    def json_check_list_of_dicts(self):
        response = self.invoke_check_json('zato.checks.sio.list-of-dicts-service', {
            'lod1': [{'k111':'v111', 'k112':'v112'}, {'k121':'v121', 'k122':'v122'}],
            'lod2': [{'k211':'v211', 'k212':'v212'}, {'k221':'v221', 'k222':'v222'}],
        })

        eq_(response.lod3[0]['k311'], 'value311')
        eq_(response.lod3[0]['k312'], 'value312')
        eq_(response.lod3[1]['k321'], 'value321')
        eq_(response.lod3[1]['k322'], 'value322')

        eq_(response.lod4[0]['k411'], 'v411')
        eq_(response.lod4[0]['k412'], 'v412')
        eq_(response.lod4[1]['k421'], 'v421')
        eq_(response.lod4[1]['k422'], 'v422')

    def json_check_no_force_type(self):
        response = self.invoke_check_json('zato.checks.sio.no-force-type-service', {
            'aa1': 'aa1-value',
            'bb1': 'bb1-value',
            'a_id': '1',
            'a_count': '2',
            'a_size': '3',
            'a_timeout': '4',
            'is_b': True,
            'needs_b': False,
            'should_b': True,
        })

        eq_(response.aa2, 11)
        eq_(response.bb2, 22)

        eq_(response.c_id, 33)
        eq_(response.c_count, 44)
        eq_(response.c_size, 55)
        eq_(response.c_timeout, 66)

        eq_(response.is_d, False)
        eq_(response.needs_d, True)
        eq_(response.should_d, False)

    def json_check_unicode(self):
        response = self.invoke_check_json('zato.checks.sio.unicode-service', {
            'uni_a': 'a',
            'uni_b': 'b',
        })

        eq_(response.uni_c, 'c')
        eq_(response.uni_d, 'd')

    def json_check_utc(self):
        response = self.invoke_check_json('zato.checks.sio.utc-service', {
            'utc1': '2019-01-26T22:33:44+00:00',
            'utc2': '2023-12-19T21:31:41+00:00',
        })

        eq_(response.utc1, '1234-11-22T01:02:03')
        eq_(response.utc2, '2918-03-19T21:22:23')

    def json_check_nested(self):
        response = self.invoke_check_json('zato.checks.sio.nested-service', _get_nested_msg())
        _test_nested(response)

# ################################################################################################################################

    def xml_check_as_is(self):
        request = """
            <request>
             <id>id1</id>
             <a_id>a1</a_id>
             <b_count>b1</b_count>
             <c_size>c1</c_size>
             <d_timeout>d1</d_timeout>
             <is_e>e1</is_e>
             <needs_f>f1</needs_f>
             <should_g>g1</should_g>
            </request>
            """

        response = self.invoke_check_xml('zato.checks.sio.as-is-service', request)

        eq_(response.item.id, 'id2')
        eq_(response.item.a_id, 'a2')
        eq_(response.item.b_count, 'b2')
        eq_(response.item.c_size, 'c2')
        eq_(response.item.d_timeout, 'd2')
        eq_(response.item.is_e, 'e2')
        eq_(response.item.needs_f, 'f2')
        eq_(response.item.should_g, 'g2')

    def xml_check_boolean(self):

        # Note that booleans are case-insensitive
        request = """
            <request>
             <bool1>true</bool1>
             <bool2>False</bool2>
            </request>
            """

        response = self.invoke_check_xml('zato.checks.sio.boolean-service', request)

        eq_(response.item.bool1, False)
        eq_(response.item.bool2, True)

    def xml_check_csv(self):
        request = """
            <request>
             <csv1>1,11,111,1111</csv1>
             <csv2>2,22,222,2222</csv2>
            </request>
            """

        response = self.invoke_check_xml('zato.checks.sio.csv-service', request)

        eq_(response.item.csv3, '3,33,333,3333')
        eq_(response.item.csv4, '4,44,444,4444')

    def xml_check_dict(self):
        request = """
            <request>
             <dict1>
              <item><key>key1_1</key><value>value1_1</value></item>
              <item><key>key1_2</key><value>value1_2</value></item>
             </dict1>

             <dict2>
              <item><key>key2_1</key><value>value2_1</value></item>
              <item><key>key2_2</key><value>value2_2</value></item>
             </dict2>
            </request>
            """

        response = self.invoke_check_xml('zato.checks.sio.dict-service', request)

        # The order of dict items is unspecified so we cannot assume any concrete indexes

        dict3_key = response.item.dict3.item[0].key

        if dict3_key == 'key3_1':
            eq_(response.item.dict3.item[0].value, 'value3_1')
            eq_(response.item.dict3.item[1].key, 'key3_2')
            eq_(response.item.dict3.item[1].value, 'value3_2')

        elif dict3_key == 'key3_2':
            eq_(response.item.dict3.item[0].value, 'value3_2')
            eq_(response.item.dict3.item[1].key, 'key3_1')
            eq_(response.item.dict3.item[1].value, 'value3_1')
        else:
            raise ValueError('Unexpected key:[{}]'.format(dict3_key))

        dict4_key = response.item.dict4.item[0].key

        if dict4_key == 'key4_1':
            eq_(response.item.dict4.item[0].value, 'value4_1')
            eq_(response.item.dict4.item[1].key, 'key4_2')
            eq_(response.item.dict4.item[1].value, 'value4_2')

        elif dict4_key == 'key4_2':
            eq_(response.item.dict4.item[0].value, 'value4_2')
            eq_(response.item.dict4.item[1].key, 'key4_1')
            eq_(response.item.dict4.item[1].value, 'value4_1')
        else:
            raise ValueError('Unexpected key:[{}]'.format(dict4_key))

    def xml_check_integer(self):
        request = """
            <request>
             <int1>1</int1>
             <int2>2</int2>
            </request>
            """

        response = self.invoke_check_xml('zato.checks.sio.integer-service', request)

        eq_(response.item.int3, 3)
        eq_(response.item.int4, 4)

    def xml_check_list(self):
        request = """
            <request>
             <list1>
              <item>1</item>
              <item>2</item>
              <item>3</item>
             </list1>
             <list2>
              <item>4</item>
              <item>5</item>
              <item>6</item>
             </list2>
            </request>
            """

        response = self.invoke_check_xml('zato.checks.sio.list-service', request)

        eq_(response.item.list3.item[0], 7)
        eq_(response.item.list3.item[1], 8)
        eq_(response.item.list3.item[2], 9)

        eq_(response.item.list4.item[0], 10)
        eq_(response.item.list4.item[1], 11)
        eq_(response.item.list4.item[2], 12)

    def xml_check_list_of_dicts(self):
        request = """
        <request>

         <lod1>
           <dict>
            <item><key>key111</key><value>value111</value></item>
            <item><key>key112</key><value>value112</value></item>
           </dict>
           <dict>
            <item><key>key121</key><value>value121</value></item>
            <item><key>key122</key><value>value122</value></item>
           </dict>
         </lod1>

         <lod2>
           <dict>
            <item><key>key211</key><value>value211</value></item>
            <item><key>key212</key><value>value212</value></item>
           </dict>
           <dict>
            <item><key>key221</key><value>value221</value></item>
            <item><key>key222</key><value>value222</value></item>
           </dict>
         </lod2>

        </request>
        """

        response = self.invoke_check_xml('zato.checks.sio.list-of-dicts-service', request)

        lod_dict = {}

        for name in('lod3', 'lod4'):
            lod_dict[name] = []
            lod = getattr(response.item, name)
            for _dict in lod.dict:
                d = {}
                for item in _dict.item:
                    d[item.key.text] = item.value.text
                lod_dict[name].append(d)

        lod3_0 = sorted(lod_dict['lod3'][0])
        lod3_1 = sorted(lod_dict['lod3'][1])

        lod4_0 = sorted(lod_dict['lod4'][0])
        lod4_1 = sorted(lod_dict['lod4'][1])

        eq_(lod3_0, ['key311', 'key312'])
        eq_(lod3_1, ['key321', 'key322'])

        eq_(lod4_0, ['key411', 'key412'])
        eq_(lod4_1, ['key421', 'key422'])

    def xml_check_no_force_type(self):
        request = """
            <request>
             <aa1>aa1-value</aa1>
             <bb1>bb1-value</bb1>
             <a_id>1</a_id>
             <a_count>2</a_count>
             <a_size>3</a_size>
             <a_timeout>4</a_timeout>
             <is_b>True</is_b>
             <needs_b>false</needs_b>
             <should_b>true</should_b>
            </request>
            """

        response = self.invoke_check_xml('zato.checks.sio.no-force-type-service', request)

        eq_(response.item.aa2, 11)
        eq_(response.item.bb2, 22)

        eq_(response.item.c_id, 33)
        eq_(response.item.c_count, 44)
        eq_(response.item.c_size, 55)
        eq_(response.item.c_timeout, 66)

        eq_(response.item.is_d, False)
        eq_(response.item.needs_d, True)
        eq_(response.item.should_d, False)

    def xml_check_unicode(self):
        request = """
            <request>
             <uni_a>a</uni_a>
             <uni_b>b</uni_b>
            </request>
            """

        response = self.invoke_check_xml('zato.checks.sio.unicode-service', request)

        eq_(response.item.uni_c, 'c')
        eq_(response.item.uni_d, 'd')

    def xml_check_utc(self):
        request = """
            <request>
             <utc1>2019-01-26T22:33:44+00:00</utc1>
             <utc2>2023-12-19T21:31:41+00:00</utc2>
            </request>
            """

        response = self.invoke_check_xml('zato.checks.sio.utc-service', request)

        eq_(response.item.utc1, '1234-11-22T01:02:03')
        eq_(response.item.utc2, '2918-03-19T21:22:23')

# ################################################################################################################################

    def handle(self):

        self.json_check_as_is()
        self.json_check_boolean()
        self.json_check_csv()
        self.json_check_dict()
        self.json_check_integer()
        self.json_check_list()
        self.json_check_list_of_dicts()
        self.json_check_no_force_type()
        self.json_check_unicode()
        self.json_check_utc()
        self.json_check_nested()

        self.xml_check_as_is()
        self.xml_check_boolean()
        self.xml_check_csv()
        self.xml_check_dict()
        self.xml_check_integer()
        self.xml_check_list()
        self.xml_check_list_of_dicts()
        self.xml_check_no_force_type()
        self.xml_check_unicode()
        self.xml_check_utc()

# ################################################################################################################################

class FixedWidthString(Service):

    class SimpleIO:
        input_required = (fw.String(1, 'a'), fw.String(2, 'b'), fw.String(3, 'c'), fw.String(4, 'd'))
        output_required = (fw.String(1, 'aa'), fw.String(2, 'bb'), fw.String(3, 'cc'), fw.String(4, 'dd'))

    def handle(self):

        expected = []

        expected.append({
            'a': 'a',
            'b': 'bb',
            'c': 'ccc',
            'd': 'dddd'
        })

        expected.append({
            'a': 'A',
            'b': 'BB',
            'c': 'CCC',
            'd': 'DDDD'
        })

        for idx, line in enumerate(self.request.input):

            _expected_line = expected[idx]

            for key, expected_value in _expected_line.items():
                given_value = getattr(line, key)
                eq_(given_value, expected_value)

        self.response.payload.aa = 'a'
        self.response.payload.bb = 'b'
        self.response.payload.cc = 'c'
        self.response.payload.dd = 'd'

# ################################################################################################################################

class FixedWidthStringMultiLine(Service):

    class SimpleIO:
        input_required = (fw.String(1, 'a'), fw.String(2, 'b'), fw.String(3, 'c'), fw.String(4, 'd'))
        output_required = (fw.String(1, 'aa'), fw.String(2, 'bb'), fw.String(3, 'cc'), fw.String(4, 'dd'))

    def handle(self):

        expected = []

        expected.append({
            'a': 'a',
            'b': 'b',
            'c': 'c',
            'd': 'd'
        })

        expected.append({
            'a': 'A',
            'b': 'B',
            'c': 'C',
            'd': 'D'
        })

        for idx, line in enumerate(self.request.input):

            _expected_line = expected[idx]

            for key, expected_value in _expected_line.items():
                given_value = getattr(line, key)
                eq_(given_value, expected_value)

        self.response.payload.append(['1', '2', '3', '4'])
        self.response.payload.append(['5', '66', '77', '88'])

# ################################################################################################################################
