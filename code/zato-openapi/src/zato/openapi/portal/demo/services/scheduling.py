# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

This file is a proprietary product, not an open-source one.
"""

# stdlib
from dataclasses import dataclass
from typing import NamedTuple

# Zato
from zato.common.typing_ import list_, optional
from zato.server.service import Model, Service

# ################################################################################################################################
# ################################################################################################################################

class WardRow(NamedTuple):
    ward_code:     str
    ward_name:     str
    total_beds:    int
    occupied_beds: int

# ################################################################################################################################
# ################################################################################################################################

# The clinics, practitioners and wards the mock schedule is built from
_clinics = {
    'CL-OUT-01': 'Outpatient Clinic North',
    'CL-OUT-02': 'Outpatient Clinic South',
    'CL-DAY-01': 'Day Treatment Center',
}

_practitioners = ['PR-2001', 'PR-2002', 'PR-2003']

_wards = [
    WardRow('W-ACUTE-1', 'Acute Care Ward 1',   24, 21),
    WardRow('W-ACUTE-2', 'Acute Care Ward 2',   20, 15),
    WardRow('W-REHAB-1', 'Rehabilitation Ward', 16, 9),
]

_slot_times = ['09:00', '09:45', '10:30', '13:00', '14:30']

_default_clinic_code = 'CL-OUT-01'
_default_date = '2026-10-19'
_timestamp = '2026-10-16T09:30:00+00:00'

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class Appointment(Model):
    appointment_id:   str
    patient_id:       str
    clinic_code:      str
    clinic_name:      str
    practitioner_id:  str
    start_time:       str
    duration_minutes: int
    status:           str

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class ListAppointmentsRequest(Model):
    clinic_code: optional[str] = None
    date:        optional[str] = None
    status:      optional[str] = None

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class AppointmentListResponse(Model):
    appointments: list_[Appointment]

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class BookAppointmentRequest(Model):
    patient_id:       str
    clinic_code:      str
    practitioner_id:  str
    start_time:       str
    duration_minutes: int
    reason:           optional[str] = None

# ################################################################################################################################
# ################################################################################################################################

@dataclass
class RescheduleAppointmentRequest(Model):
    appointment_id: str
    start_time:     str
    notify_patient: bool = True

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class Slot(Model):
    start_time:      str
    practitioner_id: str
    is_available:    bool

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class AvailabilityResponse(Model):
    clinic_code: str
    date:        str
    slots:       list_[Slot]

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class WardOccupancy(Model):
    ward_code:      str
    ward_name:      str
    total_beds:     int
    occupied_beds:  int
    occupancy_rate: float

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class OccupancyResponse(Model):
    generated_at: str
    wards:        list_[WardOccupancy]

# ################################################################################################################################
# ################################################################################################################################

def _build_appointment(appointment_id:'str', clinic_code:'str', start_time:'str', status:'str') -> 'Appointment':
    """ Builds one appointment of the mock schedule.
    """
    out = Appointment()
    out.appointment_id = appointment_id
    out.patient_id = 'PT-100231'
    out.clinic_code = clinic_code
    out.clinic_name = _clinics[clinic_code]
    out.practitioner_id = _practitioners[0]
    out.start_time = start_time
    out.duration_minutes = 45
    out.status = status

    return out

# ################################################################################################################################
# ################################################################################################################################

class ListAppointments(Service):
    """ Returns the appointments of a clinic on a given day.
    """
    name   = 'healthcare.appointments.list-appointments'
    input  = ListAppointmentsRequest
    output = AppointmentListResponse

    def handle(self) -> 'None':

        clinic_code = self.request.input.clinic_code or _default_clinic_code
        date = self.request.input.date or _default_date
        status = self.request.input.status

        appointments = []

        for index, slot_time in enumerate(_slot_times):

            appointment_status = 'no-show' if index == 2 else 'booked'

            if status:
                if appointment_status != status:
                    continue

            start_time = f'{date}T{slot_time}:00+00:00'
            appointment = _build_appointment(f'AP-50{index + 10}', clinic_code, start_time, appointment_status)
            appointments.append(appointment)

        out = AppointmentListResponse()
        out.appointments = appointments

        self.response.payload = out

# ################################################################################################################################
# ################################################################################################################################

class BookAppointment(Service):
    """ Books an appointment for a patient with a practitioner of a clinic.
    """
    name   = 'healthcare.appointments.book-appointment'
    input  = BookAppointmentRequest
    output = Appointment

    def handle(self) -> 'None':

        request = self.request.input

        out = _build_appointment('AP-5020', request.clinic_code, request.start_time, 'booked')
        out.patient_id = request.patient_id
        out.practitioner_id = request.practitioner_id
        out.duration_minutes = request.duration_minutes

        self.response.payload = out

# ################################################################################################################################
# ################################################################################################################################

class RescheduleAppointment(Service):
    """ Moves an appointment to a new start time.
    """
    name   = 'healthcare.appointments.reschedule-appointment'
    input  = RescheduleAppointmentRequest
    output = Appointment

    def handle(self) -> 'None':

        request = self.request.input

        out = _build_appointment(request.appointment_id, _default_clinic_code, request.start_time, 'rescheduled')
        self.response.payload = out

# ################################################################################################################################
# ################################################################################################################################

class CancelAppointment(Service):
    """ Cancels an appointment, optionally with a reason.
    """
    name   = 'healthcare.appointments.cancel-appointment'
    input  = 'appointment_id', '-reason'
    output = 'appointment_id', 'status', 'cancelled_at'

    def handle(self) -> 'None':
        self.response.payload.appointment_id = self.request.input.appointment_id
        self.response.payload.status = 'cancelled'
        self.response.payload.cancelled_at = _timestamp

# ################################################################################################################################
# ################################################################################################################################

class ReportNoShows(Service):
    """ Accepts a batch of appointments the patients did not attend and schedules follow-up calls for them.
    """
    name = 'healthcare.appointments.report-no-shows'

    def handle(self) -> 'None':

        if not (appointment_ids := self.request.input.get('appointment_ids')):
            appointment_ids = []

        follow_up_tasks = []

        for index, appointment_id in enumerate(appointment_ids):
            task = {'appointment_id': appointment_id, 'task_id': f'TK-{7000 + index}', 'action': 'phone-call'}
            follow_up_tasks.append(task)

        self.response.payload = {
            'received': len(appointment_ids),
            'follow_up_tasks': follow_up_tasks,
        }

# ################################################################################################################################
# ################################################################################################################################

class GetAvailability(Service):
    """ Returns the free and taken appointment slots of a clinic on a given day.
    """
    name   = 'healthcare.appointments.get-availability'
    input  = 'clinic_code', '-date'
    output = AvailabilityResponse

    def handle(self) -> 'None':

        date = self.request.input.date or _default_date

        slots = []

        for index, slot_time in enumerate(_slot_times):
            slot = Slot()
            slot.start_time = f'{date}T{slot_time}:00+00:00'
            slot.practitioner_id = _practitioners[index % len(_practitioners)]
            slot.is_available = index % 2 == 0
            slots.append(slot)

        out = AvailabilityResponse()
        out.clinic_code = self.request.input.clinic_code
        out.date = date
        out.slots = slots

        self.response.payload = out

# ################################################################################################################################
# ################################################################################################################################

class GetOccupancy(Service):
    """ Returns the current bed occupancy of every ward.
    """
    name   = 'healthcare.wards.get-occupancy'
    output = OccupancyResponse

    def handle(self) -> 'None':

        wards = []

        for item in _wards:
            occupancy_rate = item.occupied_beds / item.total_beds

            ward = WardOccupancy()
            ward.ward_code = item.ward_code
            ward.ward_name = item.ward_name
            ward.total_beds = item.total_beds
            ward.occupied_beds = item.occupied_beds
            ward.occupancy_rate = round(occupancy_rate, 3)
            wards.append(ward)

        out = OccupancyResponse()
        out.generated_at = _timestamp
        out.wards = wards

        self.response.payload = out

# ################################################################################################################################
# ################################################################################################################################

class WardBeds(Service):
    """ Lists the beds of a ward on GET and assigns a bed to a patient on POST.
    """
    name = 'healthcare.wards.beds'

    def handle_GET(self) -> 'None':

        ward_code = self.request.input.ward_code

        beds = []

        for index in range(1, 7):
            status = 'occupied' if index % 3 else 'available'
            bed = {'bed_code': f'{ward_code}-B{index:02}', 'status': status}
            beds.append(bed)

        self.response.payload = {'ward_code': ward_code, 'beds': beds}

    def handle_POST(self) -> 'None':

        if not (bed_code := self.request.input.get('bed_code')):
            bed_code = f'{self.request.input.ward_code}-B03'

        self.response.payload = {
            'ward_code': self.request.input.ward_code,
            'bed_code': bed_code,
            'patient_id': self.request.input.get('patient_id'),
            'assigned_at': _timestamp,
        }

# ################################################################################################################################
# ################################################################################################################################
