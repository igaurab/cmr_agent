from typing import Dict

from langchain_core.tools import tool
from loguru import logger

from api import CMRQueryParam, cmr_api_hook


@tool
def search_collections(
    keyword: str | None = None,
    temporal: str | None = None,
    spatial: str | None = None,
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

    spatial : str | None, optional
        Geographic bounds specified as bounding box coordinates
        Format: "min_lon,min_lat,max_lon,max_lat"
        Example: "-180,0,180,90"
        Constraints:
        - Longitude: -180 to 180
        - Latitude: -90 to 90
    """
    logger.info(f"LLM Called | keyword: {keyword}, temporal: {temporal}, spatial: {spatial}")
    query_param = CMRQueryParam(
        keyword=keyword,
        spatial=spatial.split(",") if spatial else None,
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
        }
        response["collections"].append(col)
    return response


@tool
def search_granules(collection_id: str):
    """
    Search for file level details. This needs a collection_id
    """
    logger.info(f"LLM Called | collection_id: {collection_id}")
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
