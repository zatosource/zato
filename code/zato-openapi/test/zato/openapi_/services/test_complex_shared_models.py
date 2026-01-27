# -*- coding: utf-8 -*-

# stdlib
from dataclasses import dataclass

# Zato
from zato.common.typing_ import list_
from zato.server.service import Model, Service

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class Passenger(Model):
    passenger_id: int
    first_name: str
    last_name: str
    passport_number: str
    nationality: str

@dataclass(init=False)
class Airline(Model):
    airline_id: int
    iata_code: str
    icao_code: str
    name: str

@dataclass(init=False)
class BaggageTag(Model):
    tag_number: str
    weight_kg: float
    is_oversized: bool

@dataclass(init=False)
class Baggage(Model):
    baggage_id: int
    passenger: Passenger
    tags: list_[BaggageTag]
    status: str

@dataclass(init=False)
class Seat(Model):
    seat_number: str
    seat_class: str
    is_window: bool
    is_aisle: bool

@dataclass(init=False)
class BoardingPass(Model):
    boarding_pass_id: int
    passenger: Passenger
    flight_number: str
    seat: Seat
    boarding_group: str
    gate: str
    boarding_time: str

@dataclass(init=False)
class CheckInRecord(Model):
    record_id: int
    passenger: Passenger
    airline: Airline
    boarding_pass: BoardingPass
    baggage_list: list_[Baggage]
    check_in_time: str
    agent_id: str

# ################################################################################################################################

@dataclass(init=False)
class CheckInPassengerRequest(Model):
    passenger_id: int
    flight_number: str
    seat_preference: str
    baggage_count: int

@dataclass(init=False)
class CheckInPassengerResponse(Model):
    record: CheckInRecord
    success: bool
    message: str

@dataclass(init=False)
class GetBoardingPassRequest(Model):
    passenger_id: int
    flight_number: str

@dataclass(init=False)
class GetBoardingPassResponse(Model):
    boarding_pass: BoardingPass

@dataclass(init=False)
class GetFlightPassengersRequest(Model):
    flight_number: str
    limit: int
    offset: int

@dataclass(init=False)
class GetFlightPassengersResponse(Model):
    airline: Airline
    passengers: list_[CheckInRecord]
    total_count: int

# ################################################################################################################################

class CheckInPassenger(Service):

    name = 'test.complex.checkin.passenger'
    input = CheckInPassengerRequest
    output = CheckInPassengerResponse

    def handle(self):
        pass

# ################################################################################################################################

class GetBoardingPass(Service):

    name = 'test.complex.checkin.get-boarding-pass'
    input = GetBoardingPassRequest
    output = GetBoardingPassResponse

    def handle(self):
        pass

# ################################################################################################################################

class GetFlightPassengers(Service):

    name = 'test.complex.checkin.get-flight-passengers'
    input = GetFlightPassengersRequest
    output = GetFlightPassengersResponse

    def handle(self):
        pass

# ################################################################################################################################
# ################################################################################################################################
