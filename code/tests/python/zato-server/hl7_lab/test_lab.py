# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Live environment
from live_environment.haproxy import Loopback_Address

# Live HL7
from live_hl7.enmasse import switch
from live_hl7.openelis.system import Analysis_Method_Analyzer, Dispatch_Delivered, Dispatch_Failed, \
    Status_Pending_Registration, accept_results, accession_results, analyzer_named, results_with_accession, \
    seed_order, send_order, stub_name
from live_hl7.sender import send

# Zato - the suite's own parts
from _enmasse import orders_channel
from _messages import Ack_Accepted, Ack_Application_Error, Haemoglobin_LOINC, Haemoglobin_Value, Lab_Facility, \
    Order_Message_Type, Stranger_Application, Stranger_Envelope, build_oru_r01, field, message_type_of, \
    new_control_id, new_patient, recorded_containing, wait_for, with_accept_ack
from _services import Orders_Channel, Raising_Error_Text, Raising_Service

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from conftest import LabEnvironment
    from live_hl7.messages import Patient
    from zato.common.hl7.mllp.ack import AckResult
    from zato.common.typing_ import anylist

# ################################################################################################################################
# ################################################################################################################################

def _send(lab:'LabEnvironment', message:'str') -> 'AckResult':
    out = send(Loopback_Address, lab.middleware_port, message)
    return out

# ################################################################################################################################

def _new_order(lab:'LabEnvironment', patient:'Patient') -> 'str':
    """ A haemoglobin order for a new patient, entered into the LIS - its accession.
    """
    out = seed_order(lab.session, lab.lis, patient, lab.test_id)
    return out

# ################################################################################################################################

def _orders_recorded(lab:'LabEnvironment', accession:'str') -> 'anylist':
    out:'anylist' = []

    for recorded in recorded_containing(lab.messages_file, accession):
        if recorded.channel == Orders_Channel:
            out.append(recorded)

    return out

# ################################################################################################################################

def _wait_for_result(lab:'LabEnvironment', accession:'str') -> 'anylist':
    """ The LIS takes results off the bridge asynchronously - this is them, once they are there.
    """
    def is_listed() -> 'bool':
        out = len(results_with_accession(lab.session, lab.analyzer_id, accession)) == 1
        return out

    wait_for(is_listed, f'the result of {accession} in the LIS')

    out = results_with_accession(lab.session, lab.analyzer_id, accession)
    return out

# ################################################################################################################################
# ################################################################################################################################

def test_results(lab:'LabEnvironment') -> 'None':
    """ Results from the analyzer - a result for an order the LIS placed goes through the middleware to the bridge,
    which acknowledges it, and the LIS lists it under the analyzer, waiting to be validated.
    """
    patient = new_patient('Johnson', 'Emily', '19850312', 'F')
    accession = _new_order(lab, patient)

    # The analyzer reports, the LIS acknowledges through the middleware ..
    control_id = new_control_id()
    result = _send(lab, build_oru_r01(control_id, patient, accession))

    assert result.is_accepted, result.ack_text
    assert result.ack_code == Ack_Accepted, result.ack_text
    assert control_id in result.ack_text, result.ack_text

    # .. and the result waits under the analyzer, with its value and on the test the LIS mapped the code to.
    listed, = _wait_for_result(lab, accession)

    assert listed['result'] == Haemoglobin_Value, listed
    assert listed['testId'] == lab.test_id, listed
    assert not listed['isAccepted'], listed

# ################################################################################################################################

def test_results_from_a_stranger(lab:'LabEnvironment') -> 'None':
    """ A result from an analyzer the LIS never registered - the bridge acknowledges it all the same, nothing of it
    reaches the registered analyzer's results, and the LIS stages it under an analyzer it creates for the sender.
    """
    patient = new_patient('Miller', 'James', '19701124', 'M')
    accession = _new_order(lab, patient)

    control_id = new_control_id()
    result = _send(lab, build_oru_r01(control_id, patient, accession, envelope=Stranger_Envelope))

    # The bridge answers for a message it took, whoever sent it ..
    assert result.ack_code == Ack_Accepted, result.ack_text
    assert control_id in result.ack_text, result.ack_text

    # .. the registered analyzer sees none of it ..
    assert not results_with_accession(lab.session, lab.analyzer_id, accession)

    # .. and the LIS keeps the stranger's result under an analyzer it created for it, one pending registration
    # and so with nothing of its own to map the codes to.
    stranger = analyzer_named(lab.session, stub_name(Stranger_Application, Lab_Facility))
    assert stranger['status'] == Status_Pending_Registration, stranger

# ################################################################################################################################

def test_results_with_accept_ack(lab:'LabEnvironment') -> 'None':
    """ A result whose sender asks for an accept acknowledgment - the bridge acknowledges the way it always does,
    with an application accept rather than the commit accept MSH-15 asked for, and takes the result.
    """
    patient = new_patient('Davis', 'Sarah', '19920805', 'F')
    accession = _new_order(lab, patient)

    control_id = new_control_id()
    result = _send(lab, with_accept_ack(build_oru_r01(control_id, patient, accession)))

    assert result.is_accepted, result.ack_text
    assert result.ack_code == Ack_Accepted, result.ack_text
    assert control_id in result.ack_text, result.ack_text

    _ = _wait_for_result(lab, accession)

# ################################################################################################################################

def test_orders(lab:'LabEnvironment') -> 'None':
    """ Orders to the analyzer - the LIS dispatches an order for an accession, the bridge composes the message
    and delivers it to the middleware, whose service records it and acknowledges it.
    """
    patient = new_patient('Wilson', 'Robert', '19630217', 'M')
    accession = _new_order(lab, patient)

    # The LIS dispatches and hears back that the analyzer took the order ..
    dispatch = send_order(lab.session, lab.analyzer_id, accession)

    assert dispatch['status'] == Dispatch_Delivered, dispatch
    assert dispatch['accessionNumber'] == accession, dispatch
    assert dispatch['loincCodes'] == [Haemoglobin_LOINC], dispatch

    # .. and the order is what the analyzer's side of the middleware recorded - an order message, the accession
    # as the LIS's own number of it, the test as its code.
    recorded, = _orders_recorded(lab, accession)
    message = recorded.message

    assert message_type_of(message).startswith(Order_Message_Type), message
    assert field(message, 'ORC', 2) == accession, message
    assert accession in field(message, 'OBR', 3), message
    assert Haemoglobin_LOINC in field(message, 'OBR', 4), message

# ################################################################################################################################

def test_orders_refused(lab:'LabEnvironment') -> 'None':
    """ The analyzer refuses an order - the middleware answers the bridge with AE and the reason, and the LIS
    reports the dispatch as failed with the code it got, keeping nothing of the reason.
    """
    patient = new_patient('Johnson', 'Emily', '19850312', 'F')
    accession = _new_order(lab, patient)

    with switch(lab.zato, orders_channel(), Raising_Service):

        dispatch = send_order(lab.session, lab.analyzer_id, accession)

        assert dispatch['status'] == Dispatch_Failed, dispatch

        # The LIS keeps the code of the acknowledgment it got and not the reason the ERR segment carried
        error = dispatch['error']

        assert Ack_Application_Error in error, dispatch
        assert Raising_Error_Text not in error, dispatch

    # The refusal went to the raising service, so there is nothing of it on the channel's own service
    assert not _orders_recorded(lab, accession)

    # With its own service back, the channel takes the order again
    dispatch = send_order(lab.session, lab.analyzer_id, accession)
    assert dispatch['status'] == Dispatch_Delivered, dispatch

    recorded, = _orders_recorded(lab, accession)
    assert recorded.channel == Orders_Channel, recorded

# ################################################################################################################################

def test_cycle(lab:'LabEnvironment') -> 'None':
    """ One accession through the cycle - the LIS orders, the analyzer takes the order, reports the result,
    the laboratory validates it and the order carries the analyzer's value.
    """
    patient = new_patient('Miller', 'James', '19701124', 'M')
    accession = _new_order(lab, patient)

    # The order goes out ..
    dispatch = send_order(lab.session, lab.analyzer_id, accession)
    assert dispatch['status'] == Dispatch_Delivered, dispatch

    recorded, = _orders_recorded(lab, accession)
    assert field(recorded.message, 'ORC', 2) == accession, recorded.message

    # .. the result comes back for the same accession ..
    control_id = new_control_id()
    result = _send(lab, build_oru_r01(control_id, patient, accession))
    assert result.is_accepted, result.ack_text

    listed, = _wait_for_result(lab, accession)
    assert listed['result'] == Haemoglobin_Value, listed

    # .. the laboratory validates it ..
    accept_results(lab.session, lab.analyzer_id, accession)
    assert not results_with_accession(lab.session, lab.analyzer_id, accession)

    # .. and the order the LIS dispatched carries the analyzer's value.
    test_result, = accession_results(lab.session, accession)

    assert test_result['resultValue'] == Haemoglobin_Value, test_result
    assert test_result['analysisMethod'] == Analysis_Method_Analyzer, test_result

# ################################################################################################################################
# ################################################################################################################################
