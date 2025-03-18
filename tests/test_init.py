"""Test component setup."""
import pytest
from homeassistant import setup
from homeassistant.setup import async_setup_component

from custom_components.aux_cloud.const import DOMAIN

async def test_async_setup(hass):
    """Test the component gets setup."""
    assert await async_setup_component(hass, DOMAIN, {}) is True

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

@pytest.mark.asyncio
async def test_async_setup(hass):
    """Test the component gets setup."""
    await setup.async_setup_component(hass, 'aux_cloud', {})
    assert hass.states.get('aux_cloud.device_id').state == 'on'

@pytest.mark.asyncio
async def test_async_setup_with_config(hass):
    """Test the component gets setup with config."""
    config = {'device_id': '12345'}
    await setup.async_setup_component(hass, 'aux_cloud', config)
    assert hass.states.get('aux_cloud.device_id').state == 'on'

@pytest.mark.asyncio
async def test_async_setup_without_config(hass):
    """Test the component gets setup without config."""
    await setup.async_setup_component(hass, 'aux_cloud', {})
    assert hass.states.get('aux_cloud.device_id').state == 'off'

@pytest.mark.asyncio
async def test_turn_on(hass):
    """Test turning on the device."""
    await setup.async_setup_component(hass, 'aux_cloud', {})
    await hass.services.async_call('aux_cloud', 'turn_on', {'device_id': '12345'})
    assert hass.states.get('aux_cloud.device_id').state == 'on'

@pytest.mark.asyncio
async def test_turn_off(hass):
    """Test turning off the device."""
    await setup.async_setup_component(hass, 'aux_cloud', {})
    await hass.services.async_call('aux_cloud', 'turn_off', {'device_id': '12345'})
    assert hass.states.get('aux_cloud.device_id').state == 'off'