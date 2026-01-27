# -*- coding: utf-8 -*-

# stdlib
from dataclasses import dataclass

# Zato
from zato.common.typing_ import list_
from zato.server.service import Model, Service

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class Coordinates(Model):
    latitude: float
    longitude: float
    elevation_ft: int

@dataclass(init=False)
class Runway(Model):
    runway_id: str
    designation: str
    length_ft: int
    width_ft: int
    surface_type: str
    coordinates: Coordinates
    is_active: bool

@dataclass(init=False)
class WeatherCondition(Model):
    condition_code: str
    description: str
    visibility_km: float
    wind_speed_knots: int
    wind_direction: int

@dataclass(init=False)
class METAR(Model):
    raw_text: str
    observation_time: str
    temperature_c: float
    dewpoint_c: float
    conditions: list_[WeatherCondition]
    altimeter_hpa: float

@dataclass(init=False)
class AirportWeather(Model):
    airport_icao: str
    metar: METAR
    runways_in_use: list_[Runway]
    delay_minutes: int

@dataclass(init=False)
class CrewMember(Model):
    crew_id: int
    first_name: str
    last_name: str
    license_number: str
    role: str
    hours_flown: int

@dataclass(init=False)
class CrewAssignment(Model):
    assignment_id: int
    crew_member: CrewMember
    position: str
    duty_start: str
    duty_end: str

@dataclass(init=False)
class FlightCrew(Model):
    captain: CrewMember
    first_officer: CrewMember
    cabin_crew: list_[CrewAssignment]
    total_crew_count: int

@dataclass(init=False)
class FuelLoad(Model):
    planned_kg: float
    actual_kg: float
    burn_rate_kg_hr: float
    reserve_kg: float

@dataclass(init=False)
class RouteWaypoint(Model):
    waypoint_id: str
    name: str
    coordinates: Coordinates
    altitude_ft: int
    speed_knots: int

@dataclass(init=False)
class FlightPlan(Model):
    plan_id: int
    departure_icao: str
    arrival_icao: str
    alternate_icao: str
    waypoints: list_[RouteWaypoint]
    cruise_altitude_ft: int
    estimated_time_enroute: str
    fuel: FuelLoad

@dataclass(init=False)
class FlightStatus(Model):
    status_code: str
    description: str
    updated_at: str
    delay_reason: str

@dataclass(init=False)
class ScheduledFlight(Model):
    flight_id: int
    flight_number: str
    airline_icao: str
    flight_plan: FlightPlan
    crew: FlightCrew
    departure_weather: AirportWeather
    arrival_weather: AirportWeather
    status: FlightStatus
    scheduled_departure: str
    scheduled_arrival: str
    actual_departure: str
    actual_arrival: str

# ################################################################################################################################

@dataclass(init=False)
class FlightSearchFilters(Model):
    airline_codes: list_[str]
    departure_airports: list_[str]
    arrival_airports: list_[str]
    date_from: str
    date_to: str
    status_codes: list_[str]

@dataclass(init=False)
class SortOption(Model):
    field: str
    direction: str

@dataclass(init=False)
class Pagination(Model):
    page: int
    page_size: int

@dataclass(init=False)
class SearchFlightsRequest(Model):
    filters: FlightSearchFilters
    sort: SortOption
    pagination: Pagination

@dataclass(init=False)
class SearchFlightsResponse(Model):
    flights: list_[ScheduledFlight]
    total_count: int
    page: int
    page_size: int

@dataclass(init=False)
class GetFlightPlanRequest(Model):
    flight_id: int
    include_weather: bool

@dataclass(init=False)
class GetFlightPlanResponse(Model):
    flight: ScheduledFlight
    alternate_routes: list_[FlightPlan]

# ################################################################################################################################

class SearchFlights(Service):

    name = 'test.complex.schedule.search-flights'
    input = SearchFlightsRequest
    output = SearchFlightsResponse

    def handle(self):
        pass

# ################################################################################################################################

class GetFlightPlan(Service):

    name = 'test.complex.schedule.get-flight-plan'
    input = GetFlightPlanRequest
    output = GetFlightPlanResponse

    def handle(self):
        pass

# ################################################################################################################################
# ################################################################################################################################
