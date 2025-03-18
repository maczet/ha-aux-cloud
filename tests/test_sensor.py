import pytest
from homeassistant import setup
# from homeassistant.components import aux_cloud

@pytest.mark.asyncio
async def test_sensor_state(hass):
    """Test the sensor state."""
    await setup.async_setup_component(hass, 'aux_cloud', {})
    assert hass.states.get('aux_cloud.device_id').state == 'on'