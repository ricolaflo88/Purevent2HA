"""Sensor platform for Purevent2HA"""

import logging
from typing import Any, Dict, Final

from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    UnitOfTemperature,
    PERCENTAGE,
    UnitOfPressure,
    UnitOfVolumetricFlowRate,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN

_LOGGER: Final = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensor platform."""
    
    coordinator = hass.data[DOMAIN][entry.entry_id].get('coordinator')
    
    sensors = [
        PureventTemperatureSensor(coordinator, entry),
        PureventHumiditySensor(coordinator, entry),
        PureventCO2Sensor(coordinator, entry),
        PureventStatusSensor(coordinator, entry),
        PureventFilterStateSensor(coordinator, entry),
        PureventAirflowSensor(coordinator, entry),
    ]
    
    async_add_entities(sensors)


class PureventSensorBase(SensorEntity):
    """Base class for Purevent sensors"""
    
    def __init__(self, coordinator, entry: ConfigEntry):
        """Initialize the sensor"""
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
        """Get sensor ID"""
        raise NotImplementedError


class PureventTemperatureSensor(PureventSensorBase):
    """Temperature sensor"""
    
    _attr_name = "Temperature"
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_state_class = SensorStateClass.MEASUREMENT
    
    def _get_id(self) -> str:
        return "temperature"
    
    @property
    def native_value(self) -> float | None:
        """Return the sensor value"""
        if not self.coordinator or not self.coordinator.data:
            return None
        return self.coordinator.data.get('temperature')


class PureventHumiditySensor(PureventSensorBase):
    """Humidity sensor"""
    
    _attr_name = "Humidity"
    _attr_device_class = SensorDeviceClass.HUMIDITY
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_state_class = SensorStateClass.MEASUREMENT
    
    def _get_id(self) -> str:
        return "humidity"
    
    @property
    def native_value(self) -> float | None:
        """Return the sensor value"""
        if not self.coordinator or not self.coordinator.data:
            return None
        return self.coordinator.data.get('humidity')


class PureventCO2Sensor(PureventSensorBase):
    """CO2 sensor"""
    
    _attr_name = "CO2"
    _attr_device_class = SensorDeviceClass.CO2
    _attr_native_unit_of_measurement = "ppm"
    _attr_state_class = SensorStateClass.MEASUREMENT
    
    def _get_id(self) -> str:
        return "co2"
    
    @property
    def native_value(self) -> float | None:
        """Return the sensor value"""
        if not self.coordinator or not self.coordinator.data:
            return None
        return self.coordinator.data.get('co2')


class PureventStatusSensor(PureventSensorBase):
    """Status sensor"""
    
    _attr_name = "Status"
    _attr_device_class = SensorDeviceClass.ENUM
    
    def _get_id(self) -> str:
        return "status"
    
    @property
    def native_value(self) -> str | None:
        """Return the sensor value"""
        if not self.coordinator or not self.coordinator.data:
            return None
        return self.coordinator.data.get('status', 'Unknown')


class PureventFilterStateSensor(PureventSensorBase):
    """Filter state sensor"""
    
    _attr_name = "Filter State"
    _attr_device_class = SensorDeviceClass.ENUM
    
    def _get_id(self) -> str:
        return "filter_state"
    
    @property
    def native_value(self) -> str | None:
        """Return the sensor value"""
        if not self.coordinator or not self.coordinator.data:
            return None
        return self.coordinator.data.get('filter_state', 'Unknown')


class PureventAirflowSensor(PureventSensorBase):
    """Airflow sensor"""
    
    _attr_name = "Airflow"
    _attr_device_class = SensorDeviceClass.SPEED
    _attr_native_unit_of_measurement = UnitOfVolumetricFlowRate.CUBIC_METERS_PER_HOUR
    _attr_state_class = SensorStateClass.MEASUREMENT
    
    def _get_id(self) -> str:
        return "airflow"
    
    @property
    def native_value(self) -> float | None:
        """Return the sensor value"""
        if not self.coordinator or not self.coordinator.data:
            return None
        return self.coordinator.data.get('airflow')
