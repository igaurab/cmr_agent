from enum import Enum
from typing import Any, Dict, Optional

import requests
from loguru import logger
from pydantic import BaseModel
from tenacity import retry, stop_after_attempt, wait_exponential

from api.schema import CMRQueryParam, CollectionResponse, GranulesResponse


class ErrorCode(Enum):
    AUTH_ERROR = "auth_error"
    RATE_LIMIT = "rate_limit"
    SERVER_ERROR = "server_error"
    VALIDATION_ERROR = "validation_error"


class APIError(Exception):
    def __init__(self, code: ErrorCode, message: str, response: Optional[requests.Response] = None):
        self.code = code
        self.message = message
        self.response = response
        super().__init__(message)


class CMRResponse(BaseModel):
    data: Dict[str, Any]
    status_code: int
    headers: Dict[str, str]


def retry_on_specific_status(exception):
    if isinstance(exception, APIError):
        return exception.code in [ErrorCode.RATE_LIMIT, ErrorCode.SERVER_ERROR]
    return False


class CMRAPI:
    _COLLECTION_URL = "https://cmr.earthdata.nasa.gov/search/collections.json"
    _GRANULES_URL = "https://cmr.earthdata.nasa.gov/search/granules.json"

    def __init__(self):
        self.session = requests.Session()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_on_specific_status,
        reraise=True,
    )
    def _handle_response(self, response: requests.Response) -> CMRResponse:
        try:
            response.raise_for_status()
            return CMRResponse(data=response.json(), status_code=response.status_code, headers=dict(response.headers))
        except requests.HTTPError as e:
            logger.error(f"Error from crm_api: {e} | Status code: {e.status_code}")
            if e.response.status_code == 401:
                raise APIError(ErrorCode.AUTH_ERROR, "Invalid authentication token")
            elif e.response.status_code == 429:
                raise APIError(ErrorCode.RATE_LIMIT, "Rate limit exceeded")
            elif e.response.status_code >= 500:
                raise APIError(ErrorCode.SERVER_ERROR, "Server error occurred")
            else:
                raise APIError(ErrorCode.VALIDATION_ERROR, f"Request failed: {e.response.text}", e.response)
        except requests.RequestException as e:
            raise APIError(ErrorCode.SERVER_ERROR, f"Request failed: {str(e)}")

    def fetch_collection(self, query_params: CMRQueryParam = None) -> CollectionResponse:
        query_params = query_params.to_query_params() if query_params else None
        logger.debug(f"query_params: {query_params}")
        response = self.session.get(self._COLLECTION_URL, params=query_params)
        logger.debug(f"request_url: {response.url}")
        response_data: CMRResponse = self._handle_response(response)
        return CollectionResponse(**response_data.data.get("feed"))

    def fetch_granules(self, collection_id: str) -> GranulesResponse:
        params = {"collection_concept_id": collection_id}
        response = self.session.get(self._GRANULES_URL, params=params)
        logger.debug(f"request_url: {response.url}")
        response_data: CMRResponse = self._handle_response(response)
        return GranulesResponse(**response_data.data.get("feed"))

    def __exit__(self, *args):
        self.session.close()


cmr_api_hook = CMRAPI()
