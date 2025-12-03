"""Number platform for Purevent2HA"""

import logging
from typing import Any, Final

from homeassistant.components.number import NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN

_LOGGER: Final = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up number platform."""
    
    coordinator = hass.data[DOMAIN][entry.entry_id].get('coordinator')
    
    async_add_entities([
        PureventFanSpeedNumber(coordinator, entry),
    ])


class PureventNumberBase(NumberEntity):
    """Base class for Purevent numbers"""
    
    def __init__(self, coordinator, entry: ConfigEntry):
        """Initialize the number"""
        self.coordinator = coordinator
        self._entry = entry
        self._attr_unique_id = f"{DOMAIN}_{entry.entry_id}_{self._get_id()}"
        self._attr_device_name = entry.data.get('name', 'Purevent2HA')
        
    @property
    def device_info(self):
        """Return device info"""
        return {
            "identifiers": {(DOMAIN, self._entry.entry_id)},
            "name": self._attr_device_name,
            "manufacturer": "Purevent",
            "model": "VMI Purevent",
        }
    
    @property
    def available(self) -> bool:
        """Return availability"""
        return self.coordinator and self.coordinator.last_update_success
    
    def _get_id(self) -> str:
        """Get number ID"""
        raise NotImplementedError
    
    async def async_set_native_value(self, value: float) -> None:
        """Set the native value"""
        _LOGGER.debug(f"Setting {self.name} to {value}")


class PureventFanSpeedNumber(PureventNumberBase):
    """Fan speed number"""
    
    _attr_name = "Fan Speed"
    _attr_native_min_value = 0
    _attr_native_max_value = 100
    _attr_native_step = 1
    _attr_native_unit_of_measurement = "%"
    
    def _get_id(self) -> str:
        return "fan_speed"
    
    @property
    def native_value(self) -> float | None:
        """Return the current value"""
        if not self.coordinator or not self.coordinator.data:
            return None
        return self.coordinator.data.get('fan_speed', 0)
    
    async def async_set_native_value(self, value: float) -> None:
        """Set the native value"""
        await super().async_set_native_value(value)
        await self.coordinator.async_send_command("SET_FAN_SPEED", int(value))
