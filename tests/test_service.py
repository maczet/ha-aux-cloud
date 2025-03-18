import pytest
from homeassistant import setup
from custom_components import aux_cloud

@pytest.mark.asyncio
async def test_service_turn_on(hass):
    """Test the turn_on service."""
    await setup.async_setup_component(hass, 'aux_cloud', {})
    await hass.services.async_call('aux_cloud', 'turn_on', {'device_id': '12345'})
    assert hass.states.get('aux_cloud.device_id').state == 'on'

@pytest.mark.asyncio
async def test_service_turn_off(hass):
    """Test the turn_off service."""
    await setup.async_setup_component(hass, 'aux_cloud', {})
    await hass.services.async_call('aux_cloud', 'turn_off', {'device_id': '12345'})
    assert hass.states.get('aux_cloud.device_id').state == 'off'