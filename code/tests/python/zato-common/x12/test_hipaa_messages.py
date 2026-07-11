# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import unittest

# Zato
from zato.common.typing_ import cast_
from zato.x12.envelope import parse_x12
from zato.x12.hipaa import Claim837I, Claim837P, EligibilityInquiry270, EligibilityResponse271, Remittance835

# ################################################################################################################################
# ################################################################################################################################

# A version 00501 healthcare envelope with the colon component separator the guides use.
_isa = 'ISA*00*          *00*          *ZZ*SUBMITTERID    *ZZ*PAYERID        ' + \
       '*260709*1200*^*00501*000000101*1*P*:~'

_claim_837p = _isa + \
    'GS*HC*SUBMITTERGS*PAYERGS*20260709*1200*101*X*005010X222A1~' + \
    'ST*837*0001*005010X222A1~' + \
    'BHT*0019*00*REF47517*20260709*1200*CH~' + \
    'NM1*41*2*Sunrise Medical Billing*****46*123456789~' + \
    'PER*IC*Amy Turner*TE*5550123456~' + \
    'NM1*40*2*Acme Health Plan*****46*987654321~' + \
    'HL*1**20*1~' + \
    'NM1*85*2*Sunrise Family Practice*****XX*1234567893~' + \
    'N3*200 Care Lane~' + \
    'N4*Denver*CO*80202~' + \
    'REF*EI*745896321~' + \
    'HL*2*1*22*0~' + \
    'SBR*P*18*GRP-7789******CI~' + \
    'NM1*IL*1*Doe*John****MI*MEMBER123~' + \
    'DMG*D8*19800115*M~' + \
    'NM1*PR*2*Acme Health Plan*****PI*66783~' + \
    'CLM*PATIENT-001*150***11:B:1*Y*A*Y*Y~' + \
    'HI*ABK:J039~' + \
    'LX*1~' + \
    'SV1*HC:99213*150*UN*1***1~' + \
    'DTP*472*D8*20260701~' + \
    'SE*21*0001~' + \
    'GE*1*101~' + \
    'IEA*1*000000101~'

_claim_837i = _isa + \
    'GS*HC*SUBMITTERGS*PAYERGS*20260709*1200*101*X*005010X223A2~' + \
    'ST*837*0001*005010X223A2~' + \
    'BHT*0019*00*REF47518*20260709*1200*CH~' + \
    'NM1*41*2*Riverside Hospital Billing*****46*123456789~' + \
    'NM1*40*2*Acme Health Plan*****46*987654321~' + \
    'HL*1**20*1~' + \
    'NM1*85*2*Riverside Hospital*****XX*1093812345~' + \
    'N3*400 Hospital Drive~' + \
    'N4*Austin*TX*78701~' + \
    'HL*2*1*22*0~' + \
    'SBR*P*18*GRP-9911******CI~' + \
    'NM1*IL*1*Doe*Jane****MI*MEMBER456~' + \
    'CLM*PATIENT-002*2400***11:A:1~' + \
    'HI*ABK:A419~' + \
    'LX*1~' + \
    'SV2*0450*HC:99284*2400*UN*1~' + \
    'DTP*472*D8*20260702~' + \
    'SE*17*0001~' + \
    'GE*1*101~' + \
    'IEA*1*000000101~'

_remittance_835 = _isa + \
    'GS*HP*PAYERGS*SUBMITTERGS*20260715*1200*101*X*005010X221A1~' + \
    'ST*835*0001~' + \
    'BPR*I*100*C*ACH*CCP*01*999988880*DA*123456*1512345678**01*999999999*DA*987654*20260715~' + \
    'TRN*1*12345*1512345678~' + \
    'N1*PR*Acme Health Plan~' + \
    'N3*77 Payer Plaza~' + \
    'N4*Chicago*IL*60601~' + \
    'N1*PE*Sunrise Family Practice*XX*1234567893~' + \
    'LX*1~' + \
    'CLP*PATIENT-001*1*150*100**12*CLAIM778899*11~' + \
    'CAS*CO*45*50~' + \
    'SVC*HC:99213*150*100~' + \
    'DTM*472*20260701~' + \
    'PLB*1234567893*20261231*WO:PATIENT-002*25~' + \
    'SE*14*0001~' + \
    'GE*1*101~' + \
    'IEA*1*000000101~'

_inquiry_270 = _isa + \
    'GS*HS*SUBMITTERGS*PAYERGS*20260709*1200*101*X*005010X279A1~' + \
    'ST*270*0001*005010X279A1~' + \
    'BHT*0022*13*INQ-1001*20260709*1200~' + \
    'HL*1**20*1~' + \
    'NM1*PR*2*Acme Health Plan*****PI*66783~' + \
    'HL*2*1*21*1~' + \
    'NM1*1P*2*Sunrise Family Practice*****XX*1234567893~' + \
    'HL*3*2*22*0~' + \
    'NM1*IL*1*Doe*John****MI*MEMBER123~' + \
    'DMG*D8*19800115~' + \
    'DTP*291*D8*20260709~' + \
    'EQ*30~' + \
    'SE*12*0001~' + \
    'GE*1*101~' + \
    'IEA*1*000000101~'

_response_271 = _isa + \
    'GS*HB*PAYERGS*SUBMITTERGS*20260709*1200*101*X*005010X279A1~' + \
    'ST*271*0001*005010X279A1~' + \
    'BHT*0022*11*INQ-1001*20260709*1200~' + \
    'HL*1**20*1~' + \
    'NM1*PR*2*Acme Health Plan*****PI*66783~' + \
    'HL*2*1*21*1~' + \
    'NM1*1P*2*Sunrise Family Practice*****XX*1234567893~' + \
    'HL*3*2*22*0~' + \
    'NM1*IL*1*Doe*John****MI*MEMBER123~' + \
    'EB*1*IND*30**Acme Gold Plan~' + \
    'EB*C*IND*30**Acme Gold Plan*23*250~' + \
    'AAA*Y**72*C~' + \
    'SE*12*0001~' + \
    'GE*1*101~' + \
    'IEA*1*000000101~'

# ################################################################################################################################
# ################################################################################################################################

class TestClaim837P(unittest.TestCase):

    maxDiff = None

    def test_navigate(self) -> 'None':
        message = cast_('Claim837P', parse_x12(_claim_837p).transaction_set)
        self.assertIsInstance(message, Claim837P)

        self.assertEqual(message.bht.reference, 'REF47517')
        self.assertEqual(message.names[0].entity_code, '41')
        self.assertEqual(message.names[0].last_name, 'Sunrise Medical Billing')
        self.assertEqual(message.contacts[0].name, 'Amy Turner')

        # The 2300 claim loop with its diagnosis codes and 2400 service lines.
        self.assertEqual(len(message.claims), 1)

        claim = message.claims[0]
        self.assertEqual(claim.clm.claim_id, 'PATIENT-001')
        self.assertEqual(claim.clm.amount, '150')
        self.assertEqual(claim.clm.facility.place_of_service, '11')
        self.assertEqual(claim.diagnoses[0].code_1.qualifier, 'ABK')
        self.assertEqual(claim.diagnoses[0].code_1.code, 'J039')

        self.assertEqual(len(claim.service_lines), 1)
        service_line = claim.service_lines[0]
        self.assertEqual(service_line.service.procedure.qualifier, 'HC')
        self.assertEqual(service_line.service.procedure.code, '99213')
        self.assertEqual(service_line.service.charge_amount, '150')
        self.assertEqual(service_line.dates[0].date, '20260701')

# ################################################################################################################################

    def test_hierarchy(self) -> 'None':
        message = parse_x12(_claim_837p).transaction_set

        # The 2000A billing provider loop with the 2000B subscriber loop under it.
        roots = message.hierarchy
        self.assertEqual(len(roots), 1)

        billing_provider = roots[0]
        self.assertEqual(billing_provider.level_code, '20')
        self.assertEqual(billing_provider.segments('NM1')[0].e_1, '85')

        self.assertEqual(len(billing_provider.children), 1)
        subscriber = billing_provider.children[0]
        self.assertEqual(subscriber.level_code, '22')
        self.assertEqual(subscriber.segments('SBR')[0].e_1, 'P')

# ################################################################################################################################

    def test_roundtrip(self) -> 'None':
        interchange = parse_x12(_claim_837p)
        serialized = interchange.serialize()

        self.assertEqual(serialized.replace('\n', ''), _claim_837p)

# ################################################################################################################################
# ################################################################################################################################

class TestClaim837I(unittest.TestCase):

    maxDiff = None

    def test_navigate(self) -> 'None':
        message = cast_('Claim837I', parse_x12(_claim_837i).transaction_set)
        self.assertIsInstance(message, Claim837I)

        self.assertEqual(message.bht.reference, 'REF47518')

        claim = message.claims[0]
        self.assertEqual(claim.clm.claim_id, 'PATIENT-002')
        self.assertEqual(claim.diagnoses[0].code_1.code, 'A419')

        # The institutional service line carries a revenue code next to the procedure.
        service_line = claim.service_lines[0]
        self.assertEqual(service_line.service.revenue_code, '0450')
        self.assertEqual(service_line.service.procedure.code, '99284')
        self.assertEqual(service_line.service.charge_amount, '2400')

# ################################################################################################################################

    def test_roundtrip(self) -> 'None':
        interchange = parse_x12(_claim_837i)
        serialized = interchange.serialize()

        self.assertEqual(serialized.replace('\n', ''), _claim_837i)

# ################################################################################################################################
# ################################################################################################################################

class TestRemittance835(unittest.TestCase):

    maxDiff = None

    def test_navigate(self) -> 'None':
        message = cast_('Remittance835', parse_x12(_remittance_835).transaction_set)
        self.assertIsInstance(message, Remittance835)

        self.assertEqual(message.bpr.amount, '100')
        self.assertEqual(message.bpr.payment_method, 'ACH')
        self.assertEqual(message.bpr.date, '20260715')
        self.assertEqual(message.trace.reference, '12345')

        # The payer and payee N1 loops.
        self.assertEqual(len(message.parties), 2)
        self.assertEqual(message.parties[0].n1.entity_code, 'PR')
        self.assertEqual(message.parties[0].location.city, 'Chicago')
        self.assertEqual(message.parties[1].n1.entity_code, 'PE')

        # The CLP claim-payment loop with its adjustments and service lines.
        self.assertEqual(len(message.payments), 1)

        payment = message.payments[0]
        self.assertEqual(payment.clp.claim_id, 'PATIENT-001')
        self.assertEqual(payment.clp.charge_amount, '150')
        self.assertEqual(payment.clp.payment_amount, '100')
        self.assertEqual(payment.adjustments[0].group_code, 'CO')
        self.assertEqual(payment.adjustments[0].reason_code, '45')
        self.assertEqual(payment.adjustments[0].amount, '50')

        service = payment.services[0]
        self.assertEqual(service.svc.procedure.code, '99213')
        self.assertEqual(service.svc.payment_amount, '100')
        self.assertEqual(service.dates[0].date, '20260701')

        # The provider level adjustment with its composite identifier.
        self.assertEqual(len(message.adjustments), 1)
        self.assertEqual(message.adjustments[0].amount, '25')
        self.assertEqual(message.adjustments[0].adjustment_id.reason_code, 'WO')
        self.assertEqual(message.adjustments[0].adjustment_id.reference, 'PATIENT-002')

# ################################################################################################################################

    def test_roundtrip(self) -> 'None':
        interchange = parse_x12(_remittance_835)
        serialized = interchange.serialize()

        self.assertEqual(serialized.replace('\n', ''), _remittance_835)

# ################################################################################################################################
# ################################################################################################################################

class TestEligibility270And271(unittest.TestCase):

    maxDiff = None

    def test_navigate_270(self) -> 'None':
        message = cast_('EligibilityInquiry270', parse_x12(_inquiry_270).transaction_set)
        self.assertIsInstance(message, EligibilityInquiry270)

        self.assertEqual(message.bht.reference, 'INQ-1001')
        self.assertEqual(message.birth.date_of_birth, '19800115')
        self.assertEqual(message.dates[0].qualifier, '291')
        self.assertEqual(message.inquiries[0].service_type, '30')

# ################################################################################################################################

    def test_hierarchy_270(self) -> 'None':
        message = parse_x12(_inquiry_270).transaction_set

        # Information source, receiver and subscriber chain into one branch.
        roots = message.hierarchy
        self.assertEqual(len(roots), 1)

        source = roots[0]
        self.assertEqual(source.level_code, '20')
        self.assertEqual(source.segments('NM1')[0].e_1, 'PR')

        receiver = source.children[0]
        self.assertEqual(receiver.level_code, '21')
        self.assertEqual(receiver.segments('NM1')[0].e_1, '1P')

        subscriber = receiver.children[0]
        self.assertEqual(subscriber.level_code, '22')
        self.assertEqual(subscriber.segments('NM1')[0].e_9, 'MEMBER123')
        self.assertEqual(subscriber.segments('EQ')[0].e_1, '30')

# ################################################################################################################################

    def test_navigate_271(self) -> 'None':
        message = cast_('EligibilityResponse271', parse_x12(_response_271).transaction_set)
        self.assertIsInstance(message, EligibilityResponse271)

        self.assertEqual(len(message.benefits), 2)
        self.assertEqual(message.benefits[0].eligibility_code, '1')
        self.assertEqual(message.benefits[0].plan_description, 'Acme Gold Plan')
        self.assertEqual(message.benefits[1].time_period_qualifier, '23')
        self.assertEqual(message.benefits[1].amount, '250')

        self.assertEqual(message.rejections[0].reject_reason, '72')
        self.assertEqual(message.rejections[0].follow_up_action, 'C')

# ################################################################################################################################

    def test_roundtrip(self) -> 'None':
        for raw in (_inquiry_270, _response_271):
            interchange = parse_x12(raw)
            serialized = interchange.serialize()

            self.assertEqual(serialized.replace('\n', ''), raw)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
