# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Zato
from zato.common.audit_log.api import AuditEvent

# Live environment
from live_environment.audit import events
from live_environment.haproxy import Loopback_Address

# Live HL7
from live_hl7.dcm4chee.system import PatientRecord, Task_Completed, Task_Failed, Task_Warning, change_patient_id, \
    create_patient, disable_adt_notifications, enable_adt_notifications, hl7_tasks, merge_patients, mwl_items, \
    patients, send_adt, update_patient
from live_hl7.enmasse import switch
from live_hl7.http import as_dict
from live_hl7.sender import send
from live_hl7.suite import record_finding

# Zato - the suite's own parts
from _enmasse import ADT_Channel, ADT_TLS_Channel, Orders_Channel, PACS_Channel, pacs_channel
from _environment import Engine_Receiver, Engine_TLS_Receiver, Stranger_Receiver
from _messages import Ack_Accepted, Ack_Application_Error, Order_Control_New, Patient, TLS_Feed_Envelope, \
    build_adt_a04, build_adt_a08, build_adt_a40, build_orm_o01, control_id_of, deliveries_with_control_id, field, \
    message_type_of, new_control_id, new_mrn, new_order, new_patient, read_recorded, recorded_with_control_id, \
    wait_for, with_accept_ack
from _services import PACS_Record_Label, Raising_Error_Text, Raising_Service

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from conftest import RegistrationEnvironment
    from zato.common.hl7.mllp.ack import AckResult
    from zato.common.typing_ import anydict, anylist, callable_, strset

# ################################################################################################################################
# ################################################################################################################################

# What the archive says of a message it could not process - the MSA and ERR fields it answers 409 with
Refused_Status = 409

# Where the mwlitems answer keeps the scheduled step and its status
Tag_SPS_Sequence = '00400100'
Tag_SPS_Status = '00400020'
SPS_Scheduled = 'SCHEDULED'

# Where the patients answer keeps the name and the birth date
Tag_Patient_Name = '00100010'
Tag_Patient_Birth_Date = '00100030'

# How many patients a department creates in one go
Burst_Size = 20

# An order control code no archive has a mapping for
Unknown_Order_Control = 'ZZ'

# The audit attribute a received message carries its sender's address under
Column_Endpoint = 'endpoint'

# ################################################################################################################################
# ################################################################################################################################

def _record_finding(registration:'RegistrationEnvironment', text:'str') -> 'None':
    record_finding(registration.directory, text)

# ################################################################################################################################

def _send_plain(registration:'RegistrationEnvironment', message:'str') -> 'AckResult':
    out = send(Loopback_Address, registration.engine_plain_port, message)
    return out

# ################################################################################################################################

def _assert_accepted(ack:'AckResult', control_id:'str') -> 'None':
    assert ack.is_accepted, ack.ack_text
    assert ack.ack_code == Ack_Accepted, ack.ack_text
    assert field(ack.ack_text, 'MSA', 2) == control_id, ack.ack_text

# ################################################################################################################################

def _wait_for_department(registration:'RegistrationEnvironment', control_id:'str') -> 'anylist':
    """ Until the second department has its copy of the message.
    """
    def has_copy() -> 'bool':
        out = len(deliveries_with_control_id(registration.department.deliveries, control_id)) == 1
        return out

    wait_for(has_copy, f'the department to receive {control_id}')

    out = deliveries_with_control_id(registration.department.deliveries, control_id)
    return out

# ################################################################################################################################

def _wait_for_record(registration:'RegistrationEnvironment', control_id:'str') -> 'str':
    """ Until the recording service behind the PACS's channel saw the message, which is then returned.
    """
    def has_record() -> 'bool':
        out = len(recorded_with_control_id(registration.messages_file, control_id)) == 1
        return out

    wait_for(has_record, f'the engine to record {control_id}')

    recorded, = recorded_with_control_id(registration.messages_file, control_id)
    assert recorded.channel == PACS_Record_Label

    out = recorded.message
    return out

# ################################################################################################################################

def _wait_for_patient(registration:'RegistrationEnvironment', patient_id:'str') -> 'anydict':
    """ Until the PACS lists the patient, whose record is then returned.
    """
    def is_listed() -> 'bool':
        out = len(patients(registration.pacs, patient_id)) == 1
        return out

    wait_for(is_listed, f'the PACS to list patient {patient_id}')

    out, = patients(registration.pacs, patient_id)
    return out

# ################################################################################################################################

def _patient_name(record:'anydict') -> 'str':
    out = record[Tag_Patient_Name]['Value'][0]['Alphabetic']
    return out

# ################################################################################################################################

def _patient_birth_date(record:'anydict') -> 'str':
    out = record[Tag_Patient_Birth_Date]['Value'][0]
    return out

# ################################################################################################################################

def _as_record(patient:'Patient') -> 'PatientRecord':
    """ The same person as the PACS's REST takes them.
    """
    out = PatientRecord(patient.patient_id, patient.family_name, patient.given_name, patient.birth_date, patient.sex)
    return out

# ################################################################################################################################

def _tasks_for(registration:'RegistrationEnvironment', receiver:'str', *, control_id:'str'='') -> 'anylist':
    """ The PACS's send tasks aimed at one receiver, narrowed to one message when a control id is given.
    """
    out:'anylist' = []

    application, facility = receiver.split('|')

    for task in hl7_tasks(registration.pacs):

        if task['ReceivingApplication'] != application:
            continue

        if task['ReceivingFacility'] != facility:
            continue

        if control_id and task['MessageControlID'] != control_id:
            continue

        out.append(task)

    return out

# ################################################################################################################################

def _wait_for_task(registration:'RegistrationEnvironment', receiver:'str', control_id:'str', status:'str') -> 'anydict':
    """ Until the PACS's task for one message has reached the status, which is then returned.
    """
    def has_status() -> 'bool':
        tasks = _tasks_for(registration, receiver, control_id=control_id)
        out = len(tasks) == 1 and tasks[0]['status'] == status
        return out

    wait_for(has_status, f'the PACS task for {control_id} to be {status}')

    out, = _tasks_for(registration, receiver, control_id=control_id)
    return out

# ################################################################################################################################

def _wait_for_any_task(registration:'RegistrationEnvironment', receiver:'str', status:'str', count:'int') -> 'anylist':
    """ Until as many tasks aimed at the receiver as expected have reached the status.
    """
    def has_them() -> 'bool':
        found = 0
        for task in _tasks_for(registration, receiver):
            if task['status'] == status:
                found += 1
        out = found == count
        return out

    wait_for(has_them, f'{count} PACS tasks for {receiver} to be {status}')

    out = _tasks_for(registration, receiver)
    return out

# ################################################################################################################################

def _received_rows(registration:'RegistrationEnvironment', channel:'str', control_id:'str') -> 'anylist':
    out = events(
        registration.zato.audit_db_path,
        event_type=AuditEvent.Message_Received,
        object_name=channel,
        msg_id=control_id,
    )
    return out

# ################################################################################################################################

def _sent_rows(registration:'RegistrationEnvironment', received:'anydict') -> 'anylist':
    """ The deliveries of one received message - they share its correlation id rather than its control id.
    """
    out = events(registration.zato.audit_db_path, event_type=AuditEvent.Request_Sent, cid=received['cid'])
    return out

# ################################################################################################################################

def _ack_sent_rows(registration:'RegistrationEnvironment', control_id:'str') -> 'anylist':
    out = events(registration.zato.audit_db_path, event_type=AuditEvent.Ack_Sent, msg_id=control_id)
    return out

# ################################################################################################################################

def _wait_for_audit(
    registration:'RegistrationEnvironment',
    channel:'str',
    control_id:'str',
    *,
    deliveries:'int',
    ) -> 'None':
    """ Until the trail has the inbound row and as many delivery rows as the channel has destinations.
    """
    def is_written() -> 'bool':
        received = _received_rows(registration, channel, control_id)
        if len(received) != 1:
            return False
        out = len(_sent_rows(registration, received[0])) == deliveries
        return out

    wait_for(is_written, f'the audit trail of {control_id}')

# ################################################################################################################################

def _publish_from_pacs(registration:'RegistrationEnvironment', receiver:'str', action:'callable_') -> 'str':
    """ The PACS publishes one identity change to the receiver - whatever the action makes it publish -
    and the control id of the message it composed is returned once its task is complete.
    """
    before:'strset' = set()

    for task in _tasks_for(registration, receiver):
        before.add(task['MessageControlID'])

    action()

    def has_new_task() -> 'bool':
        for task in _tasks_for(registration, receiver):
            if task['MessageControlID'] not in before and task['status'] == Task_Completed:
                return True
        return False

    wait_for(has_new_task, f'the PACS to publish to {receiver}')

    for task in _tasks_for(registration, receiver):
        if task['MessageControlID'] not in before:
            return task['MessageControlID']

    raise Exception(f'No new task for {receiver}')

# ################################################################################################################################
# ################################################################################################################################

def test_adt_feed(registration:'RegistrationEnvironment') -> 'None':
    """ The registration system admits a patient - both departments have it at the same time, the PACS
    answers for the feed, then the name changes and two records become one.
    """
    patient = new_patient('Anderson', 'Anna', '19850214', 'F')
    admission_id = new_mrn()

    # An admission ..
    control_id = new_control_id()
    ack = _send_plain(registration, build_adt_a04(control_id, patient, admission_id))
    _assert_accepted(ack, control_id)

    # .. the PACS has the patient as PID had them ..
    record = _wait_for_patient(registration, patient.patient_id)
    assert _patient_name(record) == f'{patient.family_name}^{patient.given_name}'
    assert _patient_birth_date(record) == patient.birth_date

    # .. the department has its copy ..
    delivery, = _wait_for_department(registration, control_id)
    assert message_type_of(delivery.text) == 'ADT^A04^ADT_A01'

    # .. and the trail has one inbound row with two deliveries.
    _wait_for_audit(registration, ADT_Channel, control_id, deliveries=2)

    # A change of name ..
    renamed = patient._replace(family_name='Thompson')
    control_id = new_control_id()
    ack = _send_plain(registration, build_adt_a08(control_id, renamed))
    _assert_accepted(ack, control_id)

    # .. reaches the PACS ..
    def is_renamed() -> 'bool':
        record, = patients(registration.pacs, patient.patient_id)
        out = _patient_name(record) == 'Thompson^Anna'
        return out

    wait_for(is_renamed, 'the PACS to rename the patient')
    _ = _wait_for_department(registration, control_id)

    # Two records of one person ..
    prior = new_patient('Thompson', 'Anna', '19850214', 'F')
    control_id = new_control_id()
    ack = _send_plain(registration, build_adt_a04(control_id, prior, new_mrn()))
    _assert_accepted(ack, control_id)
    _ = _wait_for_patient(registration, prior.patient_id)

    # .. become one - the prior identifier is no longer listed on its own ..
    control_id = new_control_id()
    ack = _send_plain(registration, build_adt_a40(control_id, renamed, prior))
    _assert_accepted(ack, control_id)

    def is_merged() -> 'bool':
        out = len(patients(registration.pacs, prior.patient_id)) == 0
        return out

    wait_for(is_merged, 'the PACS to merge the records')
    assert len(patients(registration.pacs, renamed.patient_id)) == 1
    _ = _wait_for_department(registration, control_id)

    # What the PACS makes of a sender asking for an accept acknowledgment is a finding, not a verdict
    control_id = new_control_id()
    ack = _send_plain(registration, with_accept_ack(build_adt_a08(control_id, renamed)))
    msa_1 = field(ack.ack_text, 'MSA', 1)
    _record_finding(registration, f'MSH-15 AL through the PACS answered {ack.ack_code} with MSA {msa_1}')

# ################################################################################################################################

def test_orders(registration:'RegistrationEnvironment') -> 'None':
    """ An imaging order becomes a worklist item, and one the PACS cannot take is refused with the
    PACS's own acknowledgment passed back unchanged.
    """
    patient = new_patient('Martinez', 'Peter', '19701130', 'M')
    order = new_order('CT', 'CT001', 'CT Head')

    # The patient first, the order after ..
    control_id = new_control_id()
    ack = _send_plain(registration, build_adt_a04(control_id, patient, order.admission_id))
    _assert_accepted(ack, control_id)
    _ = _wait_for_patient(registration, patient.patient_id)

    control_id = new_control_id()
    ack = _send_plain(registration, build_orm_o01(control_id, patient, order))
    _assert_accepted(ack, control_id)

    # .. and the PACS has a scheduled step under the accession.
    def is_scheduled() -> 'bool':
        items = mwl_items(registration.pacs, order.accession_number)
        if len(items) != 1:
            return False
        step = items[0][Tag_SPS_Sequence]['Value'][0]
        out = step[Tag_SPS_Status]['Value'][0] == SPS_Scheduled
        return out

    wait_for(is_scheduled, f'a worklist item for {order.accession_number}')
    _wait_for_audit(registration, Orders_Channel, control_id, deliveries=1)

    # An order whose control the PACS has no status for ..
    refused_order = new_order('MR', 'MR001', 'MR Knee')
    control_id = new_control_id()
    message = build_orm_o01(control_id, patient, refused_order)
    message = message.replace(f'ORC|{Order_Control_New}|', f'ORC|{Unknown_Order_Control}|')

    ack = _send_plain(registration, message)

    # .. is refused with the PACS's acknowledgment as it came, its ERR naming the field ..
    assert ack.ack_code == Ack_Application_Error, ack.ack_text
    assert not ack.is_accepted
    assert not ack.should_retry
    assert field(ack.ack_text, 'MSA', 2) == control_id
    assert 'ORC' in field(ack.ack_text, 'ERR', 2), ack.ack_text

    # .. and there is no worklist item for it.
    assert mwl_items(registration.pacs, refused_order.accession_number) == []

# ################################################################################################################################

def test_identity_reconciliation(registration:'RegistrationEnvironment') -> 'None':
    """ The PACS publishes what changes in its records - the engine records it, answers and carries it
    on to the second department, and what the engine refuses the PACS keeps as a failed task.
    """
    patient = new_patient('Garcia', 'Maria', '19920505', 'F')
    record = _as_record(patient)

    create_patient(registration.pacs, record)
    enable_adt_notifications(registration.pacs, Engine_Receiver)

    try:

        # A change of name ..
        renamed = record._replace(family_name='Robinson')
        control_id = _publish_from_pacs(
            registration, Engine_Receiver, lambda: update_patient(registration.pacs, renamed))

        # .. is recorded as the PACS composed it ..
        recorded = _wait_for_record(registration, control_id)
        assert message_type_of(recorded) == 'ADT^A31^ADT_A05'
        assert field(recorded, 'MSH', 3) == 'DCM4CHEE'
        assert field(recorded, 'MSH', 4) == 'DCM4CHEE'
        assert field(recorded, 'PID', 3).startswith(patient.patient_id)
        assert field(recorded, 'PID', 5).startswith('Robinson^Maria')

        # .. the department has its copy ..
        _ = _wait_for_department(registration, control_id)

        # .. and the trail has the message and the acknowledgment.
        _wait_for_audit(registration, PACS_Channel, control_id, deliveries=1)
        assert len(_ack_sent_rows(registration, control_id)) == 1

        # A new identifier ..
        new_id = new_mrn()
        control_id = _publish_from_pacs(
            registration, Engine_Receiver, lambda: change_patient_id(registration.pacs, patient.patient_id, new_id))

        recorded = _wait_for_record(registration, control_id)
        assert message_type_of(recorded) == 'ADT^A47^ADT_A30'
        assert field(recorded, 'MRG', 1).startswith(patient.patient_id)
        _ = _wait_for_department(registration, control_id)

        # .. and a merge.
        other = _as_record(new_patient('Robinson', 'Maria', '19920505', 'F'))
        create_patient(registration.pacs, other)

        control_id = _publish_from_pacs(
            registration, Engine_Receiver, lambda: merge_patients(registration.pacs, new_id, other.patient_id))

        recorded = _wait_for_record(registration, control_id)
        assert message_type_of(recorded) == 'ADT^A40^ADT_A39'
        _ = _wait_for_department(registration, control_id)

        # Sent without the queue, the engine's acknowledgment comes back in the PACS's own response ..
        result = send_adt(registration.pacs, Engine_Receiver, renamed._replace(patient_id=new_id))
        assert result.status == 204, result.body

        # .. and with the engine refusing, the PACS reports the refusal, the ERR included ..
        with switch(registration.zato, pacs_channel(), Raising_Service):

            result = send_adt(registration.pacs, Engine_Receiver, renamed._replace(patient_id=new_id))
            assert result.status == Refused_Status, result.body

            refusal = as_dict(result)
            assert refusal['msa-1'] == Ack_Application_Error, refusal
            assert 'ERR|' in refusal['message'], refusal
            assert Raising_Error_Text in refusal['message'], refusal

            # .. and queued, the task ends with a warning carrying the MSA as its outcome - the PACS keeps
            # a message its receiver answered, whatever the answer, apart from one it could not deliver.
            result = send_adt(registration.pacs, Engine_Receiver, renamed._replace(patient_id=new_id), is_queued=True)
            assert result.status == 202, result.body

            tasks = _wait_for_any_task(registration, Engine_Receiver, Task_Warning, 1)

            refused:'anylist' = []
            for task in tasks:
                if task['status'] == Task_Warning:
                    refused.append(task)

            refused_task, = refused
            assert f'MSA|{Ack_Application_Error}' in refused_task['outcomeMessage'], refused_task

    finally:
        disable_adt_notifications(registration.pacs)

# ################################################################################################################################

def test_department_burst(registration:'RegistrationEnvironment') -> 'None':
    """ Twenty patients created one after another bring twenty messages to the engine, each recorded,
    each answered, each in the trail.
    """
    before = len(read_recorded(registration.messages_file))
    enable_adt_notifications(registration.pacs, Engine_Receiver)

    created:'anylist' = []

    try:
        for index in range(Burst_Size):
            patient = new_patient('Burst', f'Patient{index}', '20000101', 'O')
            create_patient(registration.pacs, _as_record(patient))
            created.append(patient)

        # Every message was recorded ..
        def all_recorded() -> 'bool':
            return len(read_recorded(registration.messages_file)) == before + Burst_Size

        wait_for(all_recorded, f'{Burst_Size} messages to be recorded')

        recorded = read_recorded(registration.messages_file)[before:]

        control_ids:'strset' = set()
        identifiers:'strset' = set()

        for entry in recorded:
            assert message_type_of(entry.message) == 'ADT^A28^ADT_A05'
            control_ids.add(control_id_of(entry.message))
            identifiers.add(field(entry.message, 'PID', 3))

        assert len(control_ids) == Burst_Size
        assert len(identifiers) == Burst_Size

        # .. every task completed ..
        for control_id in control_ids:
            _ = _wait_for_task(registration, Engine_Receiver, control_id, Task_Completed)

        # .. the trail has every inbound row ..
        endpoints:'strset' = set()

        for control_id in control_ids:
            row, = _received_rows(registration, PACS_Channel, control_id)
            endpoints.add(row[Column_Endpoint])

        # .. and how many connections the PACS used for them is a finding.
        _record_finding(registration, f'The PACS sent {Burst_Size} messages over {len(endpoints)} connections')

    finally:
        disable_adt_notifications(registration.pacs)

# ################################################################################################################################

def test_department_over_tls(registration:'RegistrationEnvironment') -> 'None':
    """ Both directions over TLS - the engine reaching the PACS's TLS listener with a certificate the
    PACS verifies, the PACS reaching HAProxy's TLS bind with one the engine verifies, and a receiver
    presenting a certificate from elsewhere getting nowhere.
    """
    patient = new_patient('Clark', 'John', '19640321', 'M')

    # The feed to the PACS over TLS ..
    control_id = new_control_id()
    ack = _send_plain(registration, build_adt_a04(control_id, patient, new_mrn(), envelope=TLS_Feed_Envelope))
    _assert_accepted(ack, control_id)
    _ = _wait_for_patient(registration, patient.patient_id)
    _wait_for_audit(registration, ADT_TLS_Channel, control_id, deliveries=1)

    # .. the PACS to the engine over TLS ..
    enable_adt_notifications(registration.pacs, Engine_TLS_Receiver)

    try:
        other = new_patient('Clark', 'Eva', '19660708', 'F')
        control_id = _publish_from_pacs(
            registration, Engine_TLS_Receiver, lambda: create_patient(registration.pacs, _as_record(other)))

        recorded = _wait_for_record(registration, control_id)
        assert message_type_of(recorded) == 'ADT^A28^ADT_A05'
        assert field(recorded, 'MSH', 5) == 'ZATO_TLS'

    finally:
        disable_adt_notifications(registration.pacs)

    # .. and a receiver the authority never heard of gets a handshake failure, not a message.
    stranger = new_patient('Stranger', 'Nobody', '19000101', 'O')
    result = send_adt(registration.pacs, Stranger_Receiver, _as_record(stranger), is_queued=True)
    assert result.status == 202, result.body

    tasks = _wait_for_any_task(registration, Stranger_Receiver, Task_Failed, 1)
    failed_task, = tasks

    assert 'certif' in failed_task['errorMessage'], failed_task
    assert registration.stranger.deliveries == []

# ################################################################################################################################
# ################################################################################################################################
