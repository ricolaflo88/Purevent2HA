"""Climate platform for Purevent2HA"""

import logging
from typing import Any, Final

from homeassistant.components.climate import (
    ClimateEntity,
    HVACMode,
    HVACAction,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN

_LOGGER: Final = logging.getLogger(__name__)

HVAC_MODES = [HVACMode.HEAT, HVACMode.COOL, HVACMode.OFF]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up climate platform."""
    
    coordinator = hass.data[DOMAIN][entry.entry_id].get('coordinator')
    
    async_add_entities([
        PureventClimate(coordinator, entry),
    ])


class PureventClimate(ClimateEntity):
    """Purevent Climate entity"""
    
    _attr_name = "VMI Purevent"
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_hvac_modes = HVAC_MODES
    _attr_min_temp = 5
    _attr_max_temp = 35
    _attr_target_temperature_step = 0.5
    
    def __init__(self, coordinator, entry: ConfigEntry):
        """Initialize the climate entity"""
        self.coordinator = coordinator
        self._entry = entry
        self._attr_unique_id = f"{DOMAIN}_{entry.entry_id}_climate"
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
    
    @property
    def current_temperature(self) -> float | None:
        """Return the current temperature"""
        if not self.coordinator or not self.coordinator.data:
            return None
        return self.coordinator.data.get('temperature')
    
    @property
    def target_temperature(self) -> float | None:
        """Return the target temperature"""
        if not self.coordinator or not self.coordinator.data:
            return None
        return self.coordinator.data.get('target_temperature', 20.0)
    
    @property
    def hvac_mode(self) -> HVACMode | None:
        """Return the current HVAC mode"""
        if not self.coordinator or not self.coordinator.data:
            return None
        
        if not self.coordinator.data.get('power', False):
            return HVACMode.OFF
        
        if self.coordinator.data.get('heating', False):
            return HVACMode.HEAT
        elif self.coordinator.data.get('cooling', False):
            return HVACMode.COOL
        
        return HVACMode.OFF
    
    @property
    def hvac_action(self) -> HVACAction | None:
        """Return the current HVAC action"""
        mode = self.hvac_mode
        
        if mode == HVACMode.OFF:
            return HVACAction.OFF
        elif mode == HVACMode.HEAT:
            return HVACAction.HEATING
        elif mode == HVACMode.COOL:
            return HVACAction.COOLING
        
        return None
    
    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set new HVAC mode"""
        _LOGGER.debug(f"Setting HVAC mode to {hvac_mode}")
        
        if hvac_mode == HVACMode.OFF:
            await self.coordinator.async_send_command("POWER", False)
        elif hvac_mode == HVACMode.HEAT:
            await self.coordinator.async_send_command("POWER", True)
            await self.coordinator.async_send_command("HEATING", True)
            await self.coordinator.async_send_command("COOLING", False)
        elif hvac_mode == HVACMode.COOL:
            await self.coordinator.async_send_command("POWER", True)
            await self.coordinator.async_send_command("COOLING", True)
            await self.coordinator.async_send_command("HEATING", False)
    
    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set target temperature"""
        temperature = kwargs.get(ATTR_TEMPERATURE)
        if temperature is not None:
            _LOGGER.debug(f"Setting target temperature to {temperature}")
            await self.coordinator.async_send_command("SET_TEMP", temperature)
