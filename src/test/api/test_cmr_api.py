import json
from unittest.mock import Mock, patch

import httpx
import pytest

from api.cmr_api import CMRAPI, APIError, CollectionResponse, ErrorCode, GranulesResponse
from api.schema import CMRQueryParam

MOCK_COLLECTIONS_RESPONSE = "test/api/collections_response.json"
MOCK_GRANULES_RESPONSE = "test/api/granules_repsonse.json"


@pytest.fixture
def mock_collection_response():
    with open(MOCK_COLLECTIONS_RESPONSE, "r") as f:
        response = json.loads(f.read())
        return response


@pytest.fixture
def mock_granules_response():
    with open(MOCK_GRANULES_RESPONSE, "r") as f:
        response = json.loads(f.read())
        return response


@pytest.fixture
def mock_client():
    with patch("httpx.Client") as mock:
        client = Mock()
        mock.return_value = client
        yield client


@pytest.fixture
def cmr_api(mock_client):
    return CMRAPI(token="test-token")


def test_init():
    api = CMRAPI(token="test-token")
    assert api.token == "test-token"
    assert api.BASE_URL == "https://cmr.earthdata.nasa.gov/search/"


def test_fetch_collection_success(cmr_api, mock_client, mock_collection_response):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_collection_response
    mock_response.headers = {"Content-Type": "application/json"}
    mock_client.get.return_value = mock_response

    result = cmr_api.fetch_collection()

    assert isinstance(result, CollectionResponse)
    mock_client.get.assert_called_once()


def test_fetch_granules_success(cmr_api, mock_client, mock_granules_response):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_granules_response
    mock_response.headers = {"Content-Type": "application/json"}
    mock_client.get.return_value = mock_response

    result = cmr_api.fetch_granules("C2840815089-ORNL_CLOUD")

    assert isinstance(result, GranulesResponse)
    mock_client.get.assert_called_once()


@pytest.mark.parametrize(
    "status_code,error_code,error_msg",
    [
        (401, ErrorCode.AUTH_ERROR, "Invalid authentication token"),
        (429, ErrorCode.RATE_LIMIT, "Rate limit exceeded"),
        (500, ErrorCode.SERVER_ERROR, "Server error occurred"),
        (400, ErrorCode.VALIDATION_ERROR, "Request failed: Bad Request"),
    ],
)
def test_error_handling(cmr_api, mock_client, status_code, error_code, error_msg):
    mock_response = Mock()
    mock_response.status_code = status_code
    mock_response.text = "Bad Request"
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError("Error", request=Mock(), response=mock_response)
    mock_client.get.return_value = mock_response

    with pytest.raises(APIError) as exc_info:
        cmr_api.fetch_collection(CMRQueryParam())

    assert exc_info.value.code == error_code
    assert exc_info.value.message.startswith(error_msg)
