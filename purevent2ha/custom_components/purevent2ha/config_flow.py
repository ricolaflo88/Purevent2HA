"""Config flow for Purevent2HA"""

import logging
from typing import Any, Dict

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema({
    vol.Required('port', default='/dev/ttyUSB0'): str,
    vol.Required('baudrate', default=57600): int,
    vol.Required('timeout', default=30): int,
    vol.Required('max_retry', default=3): int,
    vol.Required('log_level', default='info'): vol.In(['debug', 'info', 'warning', 'error']),
    vol.Optional('name', default='Purevent2HA'): str,
})


class Purevent2HAConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Purevent2HA"""
    
    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_PUSH
    
    async def async_step_user(
        self, user_input: Dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle user step"""
        errors = {}
        
        if user_input is not None:
            try:
                # Validate config
                await self.hass.async_add_executor_job(
                    self._validate_config, user_input
                )
                
                return self.async_create_entry(
                    title=user_input['name'],
                    data=user_input
                )
            except Exception as e:
                _LOGGER.error(f"Error validating config: {e}")
                errors['base'] = 'invalid_config'
        
        return self.async_show_form(
            step_id='user',
            data_schema=CONFIG_SCHEMA,
            errors=errors
        )
    
    @staticmethod
    def _validate_config(config: Dict[str, Any]) -> None:
        """Validate configuration"""
        port = config.get('port')
        if not port:
            raise ValueError("Port is required")
            
        baudrate = config.get('baudrate')
        if not isinstance(baudrate, int) or baudrate <= 0:
            raise ValueError("Invalid baudrate")
    
    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get options flow"""
        return Purevent2HAOptionsFlow(config_entry)


class Purevent2HAOptionsFlow(config_entries.OptionsFlow):
    """Options flow for Purevent2HA"""
    
    def __init__(self, config_entry):
        """Initialize options flow"""
        self.config_entry = config_entry
    
    async def async_step_init(self, user_input: Dict[str, Any] | None = None) -> FlowResult:
        """Handle options"""
        if user_input is not None:
            return self.async_create_entry(title='', data=user_input)
        
        options_schema = vol.Schema({
            vol.Optional('port', default=self.config_entry.data.get('port')): str,
            vol.Optional('baudrate', default=self.config_entry.data.get('baudrate', 57600)): int,
            vol.Optional('timeout', default=self.config_entry.data.get('timeout', 30)): int,
            vol.Optional('max_retry', default=self.config_entry.data.get('max_retry', 3)): int,
            vol.Optional('log_level', default=self.config_entry.data.get('log_level', 'info')): vol.In(['debug', 'info', 'warning', 'error']),
        })
        
        return self.async_show_form(
            step_id='init',
            data_schema=options_schema
        )
