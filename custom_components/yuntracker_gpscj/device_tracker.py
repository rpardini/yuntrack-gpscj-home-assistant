import logging
from datetime import timedelta

from homeassistant.components.device_tracker.config_entry import TrackerEntity
from homeassistant.config_entries import ConfigEntry, ConfigEntryState
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import CONF_USER_ID, CONF_DEVICE_ID
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=30)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up GPSCJ tracker based on a config entry."""

    async def async_update_data():
        """Fetch data from API."""
        try:
            from custom_components.yuntracker_gpscj.api import gpscj_login_and_get_device_position
            data = await hass.async_add_executor_job(
                gpscj_login_and_get_device_position,
                entry.data[CONF_USERNAME],
                entry.data[CONF_PASSWORD],
                entry.data[CONF_USER_ID],
                entry.data[CONF_DEVICE_ID],
            )
            return data  # This should include all fields, not just GPS
        except Exception as err:
            raise UpdateFailed(f"Error fetching data: {err}")

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="GPSCJ Tracker",
        update_method=async_update_data,
        update_interval=SCAN_INTERVAL,
    )

    if entry.state == ConfigEntryState.SETUP_IN_PROGRESS:
        await coordinator.async_config_entry_first_refresh()

    device_tracker = GPSCJTracker(coordinator, entry)
    async_add_entities([device_tracker])

    # Forward to sensors
    await hass.config_entries.async_forward_entry_setups(entry, [Platform.SENSOR])


class GPSCJTracker(TrackerEntity):
    """Representation of a GPSCJ tracked device."""

    def __init__(self, coordinator: DataUpdateCoordinator, entry: ConfigEntry):
        self.coordinator = coordinator
        self._entry = entry
        self._attr_unique_id = entry.entry_id
        self._attr_name = f"GPSCJ Tracker {entry.data[CONF_DEVICE_ID]}"

    @property
    def latitude(self):
        """Return latitude from API data."""
        return self.coordinator.data.get("latitude")

    @property
    def longitude(self):
        """Return longitude from API data."""
        return self.coordinator.data.get("longitude")

    @property
    def device_info(self):
        """Return device info to group sensors under the same device."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            name=f"GPSCJ Device {self._entry.data['device_id']}",
            manufacturer="GPSCJ",
            model="Tracker",
            sw_version="1.0",
        )

    async def async_update(self):
        """Manually trigger an update."""
        await self.coordinator.async_request_refresh()
