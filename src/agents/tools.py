from typing import Dict

from langchain_core.tools import tool
from loguru import logger

from api import CMRQueryParam, cmr_api_hook
from api.opencage_api import extract_bounding_box, opencage_geocoder_api_hook


def geocode_location(address: str) -> str:
    """
    This takes a location string and return its spatial boundaries as a bounding box.

    Args:
        location (str): A free-form address or location name to be geocoded

    Returns:
        Optional[str]: A bounding box string if geocoding is successful; otherwise, None.
    """
    result = opencage_geocoder_api_hook(address)
    bounding_box = extract_bounding_box(result)
    logger.info(f"Tool [geocode_location] called | address: {address} | bounding box: {bounding_box}")
    return bounding_box


@tool
def search_collections(
    keyword: str | None = None,
    temporal: str | None = None,
    address: str | None = None,
) -> Dict:
    """
    Search collections based on keyword, temporal, and spatial parameters.

    Arguments:

    keyword : str | None, optional
        Text search parameter to filter collections by specific terms
        Example: "precipitation"

    temporal : str | None, optional
        Time-based filter in ISO 8601 format with start and end dates separated by comma
        Format: "YYYY-MM-DDThh:mm:ssZ,YYYY-MM-DDThh:mm:ssZ"
        Example: "2020-01-01T00:00:00Z,2020-12-31T23:59:59Z"

    address : str | None, optional
        Address or location mentioned in the user query
    """
    bounding_box = geocode_location(address) if address else ""
    logger.info(
        f"Tool [search_collections] called | keyword: {keyword}, temporal: {temporal}, spatial: {address} [{bounding_box}]"
    )

    query_param = CMRQueryParam(
        keyword=keyword,
        spatial=bounding_box,
        temporal=temporal.split(",") if temporal else None,
    )

    result = cmr_api_hook.fetch_collection(query_params=query_param)
    response = {}
    response["collections"] = []
    for col_entry in result.entry:
        col = {
            "id": col_entry.id,
            "title": col_entry.title,
            "summary": col_entry.summary,
            "time_start": col_entry.time_start,
            "time_end": col_entry.time_end,
            "organizations": col_entry.organizations,
            "bbox": col_entry.boxes,
        }
        response["collections"].append(col)
    return response


@tool
def search_granules(collection_id: str):
    """
    Fetches file-level details (granules) for a given collection

     Args:
        collection_id (str): The unique identifier for the collection whose granules are to be retrieved.
    """
    logger.info(f"Tool [search_granules] called | collection_id: {collection_id}")
    result = cmr_api_hook.fetch_granules(collection_id=collection_id)
    response = {}
    response["granules"] = []
    for granule in result.entry:
        g = {
            "title": granule.title,
            "time_start": granule.time_start,
            "time_end": granule.time_end,
            "id": granule.id,
            "links": granule.links,
        }
        response["granules"].append(g)
    return response
