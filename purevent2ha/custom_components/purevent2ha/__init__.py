"""Purevent2HA integration with Home Assistant"""

import logging
import asyncio
from typing import Final

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN

_LOGGER: Final = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.SWITCH,
    Platform.CLIMATE,
    Platform.NUMBER,
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Purevent2HA from a config entry."""
    
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {}
    
    # Setup platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    # Setup options listener
    entry.async_on_unload(entry.add_update_listener(async_options_update_listener))
    
    _LOGGER.info("Purevent2HA setup complete")
    return True


async def async_options_update_listener(
    hass: HomeAssistant, config_entry: ConfigEntry
) -> None:
    """Handle options update"""
    await hass.config_entries.async_reload(config_entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry"""
    
    if hass.data[DOMAIN]:
        hass.data.pop(DOMAIN, None)
    
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
