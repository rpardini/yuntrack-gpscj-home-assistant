from datetime import datetime

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, SIGNAL_STRENGTH_DECIBELS, UnitOfSpeed
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, CONF_DEVICE_ID

SENSOR_TYPES = {
    "battery": {"name": "Battery Level", "unit": PERCENTAGE, "device_class": SensorDeviceClass.BATTERY},
    "signal_gps": {"name": "GPS Signal Level", "unit": SIGNAL_STRENGTH_DECIBELS,
                   "device_class": SensorDeviceClass.SIGNAL_STRENGTH},
    "signal_4g": {"name": "4G Signal Level", "unit": SIGNAL_STRENGTH_DECIBELS,
                  "device_class": SensorDeviceClass.SIGNAL_STRENGTH},
    "server_utc_date": {"name": "Connection Time", "device_class": SensorDeviceClass.TIMESTAMP},
    "device_utc_date": {"name": "Location Time", "device_class": SensorDeviceClass.TIMESTAMP},
    "stop_time": {"name": "Stoppage Time", "device_class": SensorDeviceClass.TIMESTAMP},
    "stop_time_minute": {"name": "Stop Time (minutes)", "unit": "min"},
    "device_name_sn": {"name": "Device Name/#"},
    "speed": {"name": "Speed", "unit": UnitOfSpeed.KILOMETERS_PER_HOUR},
    "status": {"name": "Status"},
    "course": {"name": "Course"},
    "latitude": {"name": "Latitude", "entity_category": EntityCategory.DIAGNOSTIC},
    "longitude": {"name": "Longitude", "entity_category": EntityCategory.DIAGNOSTIC},
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
        self._attr_name = f"{entry.data[CONF_DEVICE_ID]} {sensor_info['name']}"
        self._attr_unique_id = f"{entry.entry_id}_{sensor_key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": f"YunTracker/GPSCJ {entry.data[CONF_DEVICE_ID]}",
            "manufacturer": "Some chinese manufacturer",
            "model": "Chinese stuff",
            "sw_version": "1.0",
        }
        self._attr_native_unit_of_measurement = sensor_info.get("unit")
        self._attr_device_class = sensor_info.get("device_class")
        self._attr_entity_category = sensor_info.get("entity_category")
        self._attr_translation_key = sensor_key  # Updated translation_key

    @property
    def native_value(self):
        """Return the sensor value."""
        value = self.coordinator.data.get(self._sensor_key)
        if self._sensor_key == "device_name_sn":
            return f"{self.coordinator.data.get('modelName')} {self.coordinator.data.get('model')} {self.coordinator.data.get('sn')}"
        if self._sensor_key == "speed":
            return float(value)
        if self._attr_device_class == SensorDeviceClass.TIMESTAMP:
            return datetime.fromisoformat(value)
        return value
