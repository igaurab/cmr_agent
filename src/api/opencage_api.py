from opencage.geocoder import OpenCageGeocode

from config import settings


def extract_bounding_box(results):
    bounds = results[0]["bounds"]
    southwest = bounds["southwest"]
    northeast = bounds["northeast"]

    return f"{southwest['lng']},{southwest['lat']},{northeast['lng']},{northeast['lat']}"


def opencage_geocoder_api_hook(address: str) -> str:
    geocoder = OpenCageGeocode(settings.OPENCAGE_GEOCODE_API)
    results = geocoder.geocode(address)
    return results
