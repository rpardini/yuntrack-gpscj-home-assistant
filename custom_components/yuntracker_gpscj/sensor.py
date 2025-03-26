from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, SIGNAL_STRENGTH_DECIBELS
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from datetime import datetime

from .const import DOMAIN

SENSOR_TYPES = {
    "battery": {"name": "Battery Level", "unit": PERCENTAGE, "device_class": SensorDeviceClass.BATTERY},
    "gps_signal": {"name": "GPS Signal Level", "unit": SIGNAL_STRENGTH_DECIBELS,
                   "device_class": SensorDeviceClass.SIGNAL_STRENGTH},
    "lte_signal": {"name": "4G Signal Level", "unit": SIGNAL_STRENGTH_DECIBELS,
                   "device_class": SensorDeviceClass.SIGNAL_STRENGTH},
    "connection_time": {"name": "Connection Time", "device_class": SensorDeviceClass.TIMESTAMP},
    "location_time": {"name": "Location Time", "device_class": SensorDeviceClass.TIMESTAMP},
    "stoppage_time": {"name": "Stoppage Time", "device_class": SensorDeviceClass.TIMESTAMP},
    "stop_minutes": {"name": "Stop Time (minutes)", "unit": "min"},
}


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up sensors based on a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []
    for sensor_key, sensor_info in SENSOR_TYPES.items():
        entities.append(GPSCJSensor(coordinator, entry, sensor_key, sensor_info))

    async_add_entities(entities)


class GPSCJSensor(CoordinatorEntity, SensorEntity):
    """Representation of additional GPSCJ sensor data."""

    def __init__(self, coordinator, entry, sensor_key, sensor_info):
        super().__init__(coordinator)
        self._entry = entry
        self._sensor_key = sensor_key
        self._attr_name = f"{entry.data['device_id']} {sensor_info['name']}"
        self._attr_unique_id = f"{entry.entry_id}_{sensor_key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": f"GPSCJ Device {entry.data['device_id']}",
            "manufacturer": "GPSCJ",
            "model": "Tracker",
            "sw_version": "1.0",
        }
        self._attr_native_unit_of_measurement = sensor_info.get("unit")
        self._attr_device_class = sensor_info.get("device_class")

    @property
    def native_value(self):
        """Return the sensor value."""
        value = self.coordinator.data.get(self._sensor_key)
        if self._attr_device_class == SensorDeviceClass.TIMESTAMP:
            return datetime.fromisoformat(value)
        return value

