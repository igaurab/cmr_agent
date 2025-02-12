from dataclasses import dataclass
from typing import List, Optional

from config import settings


@dataclass
class LatLng:
    lat: float
    lng: float


@dataclass
class Bounds:
    northeast: LatLng
    southwest: LatLng

    @property
    def as_string(self) -> str:
        """
        https://cmr.earthdata.nasa.gov/search/site/docs/search/api.html
        The Bounding box parameters must be 4 comma-separated numbers: lower left longitude, lower left latitude, upper right longitude, upper right latitude.
        """
        return f"{self.southwest.lng},{self.southwest.lat},{self.northeast.lng},{self.northeast.lat}"


@dataclass
class Geometry:
    location: LatLng
    bounds: Optional[Bounds] = None
    location_type: str = ""
    viewport: Optional[Bounds] = None


@dataclass
class GeocodingResult:
    address_components: List[dict]
    formatted_address: str
    geometry: Geometry
    place_id: str
    types: List[str]

    @property
    def bounding_box(self) -> Optional[str]:
        if self.geometry.bounds:
            return self.geometry.bounds.as_string
        location = self.geometry.location
        return f"{location.lng},{location.lat},0,0"

    @property
    def point(self) -> str:
        if location := self.geometry.location:
            return f"{location.lat},{location.lng}"


@dataclass
class GeocodingResponse:
    results: List[GeocodingResult]
    status: str


def parse_latlng(data: dict) -> LatLng:
    return LatLng(lat=data["lat"], lng=data["lng"])


def parse_bounds(data: dict) -> Bounds:
    northeast = parse_latlng(data["northeast"])
    southwest = parse_latlng(data["southwest"])
    return Bounds(northeast=northeast, southwest=southwest)


def parse_geometry(data: dict) -> Geometry:
    location = parse_latlng(data["location"])
    bounds = parse_bounds(data["bounds"]) if "bounds" in data and data["bounds"] else None
    viewport = parse_bounds(data["viewport"]) if "viewport" in data and data["viewport"] else None
    location_type = data.get("location_type", "")
    return Geometry(location=location, bounds=bounds, location_type=location_type, viewport=viewport)


def parse_result(data: dict) -> GeocodingResult:
    address_components = data.get("address_components", [])
    formatted_address = data.get("formatted_address", "")
    geometry = parse_geometry(data["geometry"]) if "geometry" in data else None
    place_id = data.get("place_id", "")
    types = data.get("types", [])
    return GeocodingResult(
        address_components=address_components,
        formatted_address=formatted_address,
        geometry=geometry,
        place_id=place_id,
        types=types,
    )


def parse_response(json_data: dict) -> GeocodingResponse:
    results = [parse_result(item) for item in json_data.get("results", [])]
    status = json_data.get("status", "")
    return GeocodingResponse(results=results, status=status)


import requests


def geocoding_api_hook(address: str) -> GeocodingResult:
    URL = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={settings.GOOGLE_MAPS_API_KEY}"
    result = requests.get(URL)
    if result.status_code == 200:
        result = parse_response(result.json())
        return result.results[0]
    return None
