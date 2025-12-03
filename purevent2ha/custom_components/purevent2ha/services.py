"""Services for Purevent2HA"""

import logging
from typing import Any

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_services(hass: HomeAssistant) -> None:
    """Set up services for Purevent2HA"""
    
    async def handle_send_command(call: ServiceCall) -> None:
        """Handle send command service"""
        device_id = call.data.get('device_id')
        command = call.data.get('command')
        parameters = call.data.get('parameters', {})
        
        if not device_id or not command:
            raise HomeAssistantError("Missing device_id or command")
        
        entry_id = call.data.get('entry_id')
        if entry_id and entry_id in hass.data[DOMAIN]:
            coordinator = hass.data[DOMAIN][entry_id].get('coordinator')
            if coordinator:
                await coordinator.async_send_command(command, parameters)
            else:
                raise HomeAssistantError("Coordinator not found")
        else:
            raise HomeAssistantError("Entry not found")
    
    hass.services.async_register(
        DOMAIN,
        'send_command',
        handle_send_command,
        description='Send a command to a device'
    )
    
    _LOGGER.info("Services registered")
