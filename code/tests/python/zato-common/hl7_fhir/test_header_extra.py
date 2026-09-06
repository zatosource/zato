# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Local
from conftest import convert, one_resource, organization_named

# ################################################################################################################################
# ################################################################################################################################

# A minimal PID every header test builds on.
PID = 'PID|1||12345^^^GENHOSP^MR||Smith^John|||M'

# ################################################################################################################################
# ################################################################################################################################

class TestMSHExtraFields:
    """ MSH-17 - the country - MSH-19 - the language - and MSH-21 - the message profiles.
    """

    def test_country_lands_on_the_sending_facility(self) -> 'None':
        msh = 'MSH|^~\\&|EHR|GENHOSP|CARE|RECVFAC|20260315120000||ADT^A01^ADT_A01|MSG00001|P|2.5.1|||||USA'

        bundle = convert(msh, PID)
        sender = organization_named(bundle, 'GENHOSP')

        assert sender['address'] == [{'country': 'USA'}]

        # The receiving facility knows no country.
        receiver = organization_named(bundle, 'RECVFAC')
        assert 'address' not in receiver

# ################################################################################################################################

    def test_country_with_no_facility_is_preserved(self) -> 'None':
        msh = 'MSH|^~\\&|EHR||CARE||20260315120000||ADT^A01^ADT_A01|MSG00001|P|2.5.1|||||USA'

        bundle = convert(msh, PID)
        header = one_resource(bundle, 'MessageHeader')

        assert {
            'url': 'urn:zato:hl7v2:extension/unmapped/MSH-17',
            'valueString': 'USA',
        } in header['extension']

# ################################################################################################################################

    def test_language_is_the_headers_language(self) -> 'None':
        msh = 'MSH|^~\\&|EHR|GENHOSP|CARE|RECVFAC|20260315120000||ADT^A01^ADT_A01|MSG00001|P|2.5.1|||||||en^English^ISO639'

        bundle = convert(msh, PID)
        header = one_resource(bundle, 'MessageHeader')

        assert header['language'] == 'en'

# ################################################################################################################################

    def test_each_message_profile_keeps_its_own_extension(self) -> 'None':
        msh = (
            'MSH|^~\\&|EHR|GENHOSP|CARE|RECVFAC|20260315120000||ADT^A01^ADT_A01|MSG00001|P|2.5.1'
            '|||||||||PROFILE1^HL7~PROFILE2^HL7'
        )

        bundle = convert(msh, PID)
        header = one_resource(bundle, 'MessageHeader')

        extensions = header['extension']

        assert {
            'url': 'urn:zato:hl7v2:extension/message-profile',
            'valueIdentifier': {'value': 'PROFILE1', 'system': 'urn:zato:hl7v2:authority:HL7'},
        } in extensions

        assert {
            'url': 'urn:zato:hl7v2:extension/message-profile',
            'valueIdentifier': {'value': 'PROFILE2', 'system': 'urn:zato:hl7v2:authority:HL7'},
        } in extensions

# ################################################################################################################################
# ################################################################################################################################
