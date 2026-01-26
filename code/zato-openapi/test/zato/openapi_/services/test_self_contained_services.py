# -*- coding: utf-8 -*-

# stdlib
from dataclasses import dataclass

# Zato
from zato.common.typing_ import list_
from zato.server.service import Model, Service

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class Runway(Model):
    designation: str
    length_ft: int
    surface: str

@dataclass(init=False)
class Terminal(Model):
    name: str
    gates: list_[str]

@dataclass(init=False)
class Airport(Model):
    icao_code: str
    name: str
    runways: list_[Runway]
    terminals: list_[Terminal]

@dataclass(init=False)
class Airline(Model):
    iata_code: str
    name: str
    hub: Airport

@dataclass(init=False)
class FlightLeg(Model):
    departure: Airport
    arrival: Airport
    duration_minutes: int

@dataclass(init=False)
class FlightRoute(Model):
    route_id: str
    airline: Airline
    legs: list_[FlightLeg]

# ################################################################################################################################

@dataclass(init=False)
class GetRouteRequest(Model):
    route_id: str

@dataclass(init=False)
class GetRouteResponse(Model):
    route: FlightRoute

@dataclass(init=False)
class CreateRouteRequest(Model):
    airline: Airline
    legs: list_[FlightLeg]

@dataclass(init=False)
class CreateRouteResponse(Model):
    route: FlightRoute
    success: bool

# ################################################################################################################################

class GetRoute(Service):

    name = 'test.route.get'
    input = GetRouteRequest
    output = GetRouteResponse

    def handle(self):
        pass

# ################################################################################################################################

class CreateRoute(Service):

    name = 'test.route.create'
    input = CreateRouteRequest
    output = CreateRouteResponse

    def handle(self):
        pass

# ################################################################################################################################
# ################################################################################################################################
