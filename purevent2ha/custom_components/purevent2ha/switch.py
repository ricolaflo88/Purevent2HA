"""Switch platform for Purevent2HA"""

import logging
from typing import Any, Final

from homeassistant.components.switch import SwitchEntity
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
    """Set up switch platform."""
    
    coordinator = hass.data[DOMAIN][entry.entry_id].get('coordinator')
    
    switches = [
        PureventPowerSwitch(coordinator, entry),
        PureventHeatingSwitch(coordinator, entry),
        PureventCoolingSwitch(coordinator, entry),
        PureventIntakeSwitch(coordinator, entry),
    ]
    
    async_add_entities(switches)


class PureventSwitchBase(SwitchEntity):
    """Base class for Purevent switches"""
    
    def __init__(self, coordinator, entry: ConfigEntry):
        """Initialize the switch"""
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
        """Get switch ID"""
        raise NotImplementedError
    
    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the switch"""
        _LOGGER.debug(f"Turning on {self.name}")
        # Send command via coordinator
        await self.coordinator.async_send_command(
            self._get_command_id(), True
        )
    
    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the switch"""
        _LOGGER.debug(f"Turning off {self.name}")
        # Send command via coordinator
        await self.coordinator.async_send_command(
            self._get_command_id(), False
        )
    
    def _get_command_id(self) -> str:
        """Get command ID"""
        raise NotImplementedError


class PureventPowerSwitch(PureventSwitchBase):
    """Power switch"""
    
    _attr_name = "Power"
    
    def _get_id(self) -> str:
        return "power"
    
    def _get_command_id(self) -> str:
        return "POWER"
    
    @property
    def is_on(self) -> bool | None:
        """Return True if the entity is on"""
        if not self.coordinator or not self.coordinator.data:
            return None
        return self.coordinator.data.get('power', False)


class PureventHeatingSwitch(PureventSwitchBase):
    """Heating switch"""
    
    _attr_name = "Heating"
    
    def _get_id(self) -> str:
        return "heating"
    
    def _get_command_id(self) -> str:
        return "HEATING"
    
    @property
    def is_on(self) -> bool | None:
        """Return True if the entity is on"""
        if not self.coordinator or not self.coordinator.data:
            return None
        return self.coordinator.data.get('heating', False)


class PureventCoolingSwitch(PureventSwitchBase):
    """Cooling switch"""
    
    _attr_name = "Cooling"
    
    def _get_id(self) -> str:
        return "cooling"
    
    def _get_command_id(self) -> str:
        return "COOLING"
    
    @property
    def is_on(self) -> bool | None:
        """Return True if the entity is on"""
        if not self.coordinator or not self.coordinator.data:
            return None
        return self.coordinator.data.get('cooling', False)


class PureventIntakeSwitch(PureventSwitchBase):
    """Intake switch"""
    
    _attr_name = "Intake Air"
    
    def _get_id(self) -> str:
        return "intake"
    
    def _get_command_id(self) -> str:
        return "INTAKE"
    
    @property
    def is_on(self) -> bool | None:
        """Return True if the entity is on"""
        if not self.coordinator or not self.coordinator.data:
            return None
        return self.coordinator.data.get('intake', False)
