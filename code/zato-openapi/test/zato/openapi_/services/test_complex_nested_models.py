# -*- coding: utf-8 -*-

# stdlib
from dataclasses import dataclass

# Zato
from zato.common.typing_ import list_
from zato.server.service import Model, Service

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class Continent(Model):
    name: str
    code: str

@dataclass(init=False)
class Land(Model):
    name: str
    iso_code: str
    continent: Continent

@dataclass(init=False)
class City(Model):
    name: str
    icao_code: str
    land: Land

@dataclass(init=False)
class Airport(Model):
    name: str
    iata_code: str
    icao_code: str
    city: City

@dataclass(init=False)
class Terminal(Model):
    terminal_id: str
    name: str
    airport: Airport

@dataclass(init=False)
class Gate(Model):
    gate_number: str
    terminal: Terminal
    is_international: bool

@dataclass(init=False)
class AircraftManufacturer(Model):
    name: str
    land: Land

@dataclass(init=False)
class AircraftType(Model):
    model: str
    manufacturer: AircraftManufacturer
    seat_capacity: int
    max_range_km: int

@dataclass(init=False)
class Aircraft(Model):
    registration: str
    aircraft_type: AircraftType
    airline_code: str

@dataclass(init=False)
class Flight(Model):
    flight_number: str
    aircraft: Aircraft
    departure_gate: Gate
    arrival_gate: Gate

# ################################################################################################################################

@dataclass(init=False)
class GetFlightRequest(Model):
    flight_number: str

@dataclass(init=False)
class GetFlightResponse(Model):
    flight: Flight
    request_id: str

# ################################################################################################################################

class GetFlightDetails(Service):

    name = 'test.complex.flight.get-details'
    input = GetFlightRequest
    output = GetFlightResponse

    def handle(self):
        pass

# ################################################################################################################################
# ################################################################################################################################
