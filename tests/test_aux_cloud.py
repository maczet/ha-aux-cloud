"""Tests for the AuxCloudAPI class."""

import base64
import json

from unittest.mock import MagicMock, AsyncMock

import pytest

from custom_components.aux_cloud.api.aux_cloud import (
    AuxCloudAPI,
    AuxApiFunctionNotSupportedError,
    API_SERVER_URL_EU,
    API_SERVER_URL_USA,
    API_SERVER_URL_CN,
)
from custom_components.aux_cloud.api.const import AuxProducts


@pytest.fixture
def aux_api():
    """Return a new AuxCloudAPI instance."""
    return AuxCloudAPI(region="eu")


@pytest.fixture
def heat_pump_device():
    """Return a minimal heat pump device dict as returned by the cloud API."""
    cookie = base64.b64encode(
        json.dumps({"terminalid": "term1", "aeskey": "key1"}).encode()
    ).decode()
    return {
        "endpointId": "device1",
        "productId": AuxProducts.DeviceType.HEAT_PUMP[0],
        "mac": "aa:bb:cc:dd:ee:ff",
        "devicetypeFlag": 0,
        "cookie": cookie,
        "devSession": "session1",
    }


@pytest.fixture
def mock_response():
    """Return a mock response for API calls."""
    mock = MagicMock()
    mock.status = 200
    mock.text = AsyncMock(return_value='{"status": 0, "data": {}}')
    return mock


class TestAuxCloudAPI:
    """Tests for the AuxCloudAPI class."""

    def test_init(self):
        """Test initialization with different regions."""
        api_eu = AuxCloudAPI(region="eu")
        assert api_eu.url == API_SERVER_URL_EU
        assert api_eu.region == "eu"

        api_usa = AuxCloudAPI(region="usa")
        assert api_usa.url == API_SERVER_URL_USA
        assert api_usa.region == "usa"

        api_cn = AuxCloudAPI(region="cn")
        assert api_cn.url == API_SERVER_URL_CN
        assert api_cn.region == "cn"

        # Test default fallback
        api_unknown = AuxCloudAPI(region="unknown")
        assert api_unknown.url == API_SERVER_URL_EU
        assert api_unknown.region == "unknown"

    def test_get_headers(self, aux_api):
        """Test the headers' generation."""
        # Basic headers
        headers = aux_api._get_headers()
        assert "Content-Type" in headers
        assert headers["loginsession"] == ""
        assert headers["userid"] == ""

        # With login session and user ID
        aux_api.loginsession = "test_session"
        aux_api.userid = "test_user"
        headers = aux_api._get_headers()
        assert headers["loginsession"] == "test_session"
        assert headers["userid"] == "test_user"

        # With additional kwargs
        headers = aux_api._get_headers(custom_header="custom_value")
        assert headers["custom_header"] == "custom_value"

    @pytest.mark.asyncio
    async def test_get_device_params_raises_function_not_supported(
        self, aux_api, heat_pump_device
    ):
        """A FUNCTION_NOT_SUPPORT ErrorResponse should raise the specific error type."""
        aux_api._make_request = AsyncMock(
            return_value={
                "event": {
                    "header": {"name": "ErrorResponse"},
                    "payload": {
                        "type": "FUNCTION_NOT_SUPPORT",
                        "message": "function not support",
                        "status": -49025,
                    },
                }
            }
        )

        with pytest.raises(AuxApiFunctionNotSupportedError):
            await aux_api.get_device_params(heat_pump_device, params=[])

    @pytest.mark.asyncio
    async def test_heat_pump_params_fallback_to_named_params(
        self, aux_api, heat_pump_device
    ):
        """On FUNCTION_NOT_SUPPORT, the heat pump query should retry with named params."""
        not_supported_response = {
            "event": {
                "header": {"name": "ErrorResponse"},
                "payload": {
                    "type": "FUNCTION_NOT_SUPPORT",
                    "message": "function not support",
                    "status": -49025,
                },
            }
        }
        success_response = {
            "event": {
                "header": {"name": "Response"},
                "payload": {
                    "data": json.dumps(
                        {"params": ["hp_pwr"], "vals": [[{"val": 1}]]}
                    )
                },
            }
        }
        aux_api._make_request = AsyncMock(
            side_effect=[not_supported_response, success_response]
        )

        result = await aux_api._get_heat_pump_params_with_fallback(
            heat_pump_device, params=[]
        )

        assert result == {"hp_pwr": 1}
        assert aux_api._make_request.call_count == 2
        second_call_params = aux_api._make_request.call_args_list[1].kwargs["data"][
            "directive"
        ]["payload"]["params"]
        assert second_call_params == AuxProducts.HP_PARAMS
