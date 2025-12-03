"""Coordinator for Purevent2HA"""

import logging
from datetime import timedelta
from typing import Any

import aiohttp
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=30)


class Purevent2HACoordinator(DataUpdateCoordinator):
    """Coordinator for Purevent2HA"""
    
    def __init__(self, hass: HomeAssistant, host: str = 'localhost', port: int = 5000):
        """Initialize coordinator"""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
        )
        self.host = host
        self.port = port
        self.url = f'http://{host}:{port}'
        
    async def _async_update_data(self) -> dict:
        """Fetch data from API"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f'{self.url}/api/devices') as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._process_devices(data.get('devices', []))
                    else:
                        raise UpdateFailed(f"API returned {response.status}")
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"API Error: {err}")
    
    def _process_devices(self, devices: list) -> dict:
        """Process device data"""
        processed = {
            'temperature': None,
            'humidity': None,
            'co2': None,
            'status': 'Unknown',
            'filter_state': 'Unknown',
            'power': False,
            'heating': False,
            'cooling': False,
            'fan_speed': 0,
        }
        
        for device in devices:
            device_data = device.get('data', {})
            
            if 'co2_ppm' in device_data:
                processed['co2'] = device_data['co2_ppm']
            
            if 'temperature' in device_data:
                processed['temperature'] = device_data['temperature']
            
            if 'humidity' in device_data:
                processed['humidity'] = device_data['humidity']
            
            if 'status' in device_data:
                processed['status'] = device_data['status']
            
            if 'filter_state' in device_data:
                processed['filter_state'] = device_data['filter_state']
            
            if 'power' in device_data:
                processed['power'] = device_data['power']
            
            if 'heating' in device_data:
                processed['heating'] = device_data['heating']
            
            if 'cooling' in device_data:
                processed['cooling'] = device_data['cooling']
            
            if 'fan_speed' in device_data:
                processed['fan_speed'] = device_data['fan_speed']
        
        return processed
    
    async def async_send_command(self, command: str, parameters: Any = None) -> bool:
        """Send command to device"""
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    'device_id': 'purevent_vmi',
                    'command': command,
                    'parameters': parameters
                }
                
                async with session.post(
                    f'{self.url}/api/commands',
                    json=payload
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('success', False)
                    else:
                        _LOGGER.error(f"Failed to send command: {response.status}")
                        return False
        except aiohttp.ClientError as err:
            _LOGGER.error(f"API Error: {err}")
            return False
