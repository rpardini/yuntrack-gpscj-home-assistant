import datetime
import logging

from homeassistant.components.device_tracker.config_entry import TrackerEntity
from homeassistant.config_entries import ConfigEntry, ConfigEntryState
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    CoordinatorEntity,
)

from .const import CONF_USER_ID, CONF_DEVICE_ID
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = datetime.timedelta(seconds=30)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up GPSCJ tracker based on a config entry."""
    session = None
    session_created = None

    async def async_update_data():
        """Fetch data from API."""
        nonlocal session
        nonlocal session_created
        from custom_components.yuntrack_gpscj.api import gpscj_create_session_and_login, \
            gpscj_get_position_from_session

        if session is None or session_created is None:
            _LOGGER.info(f"Creating session for {entry.data[CONF_USERNAME]}")
            session = await hass.async_add_executor_job(
                gpscj_create_session_and_login,
                entry.data[CONF_PASSWORD],
                entry.data[CONF_USERNAME]
            )
            session_created = datetime.datetime.now(datetime.UTC)
        else:
            _LOGGER.info(f"Reusing session for {entry.data[CONF_USERNAME]}")

        try:
            _LOGGER.info(f"Fetching data for {entry.data[CONF_DEVICE_ID]}")
            data = await hass.async_add_executor_job(
                gpscj_get_position_from_session,
                entry.data[CONF_DEVICE_ID],
                entry.data[CONF_USER_ID],
                session
            )
            _LOGGER.info(f"Got data for {entry.data[CONF_DEVICE_ID]}")
            data["session_created"] = session_created.replace(microsecond=0).isoformat()
            return data
        except Exception as err:
            _LOGGER.error(f"Error fetching data: '{err}' - will try to re-login.")
            session = await hass.async_add_executor_job(
                gpscj_create_session_and_login,
                entry.data[CONF_PASSWORD],
                entry.data[CONF_USERNAME]
            )
            session_created = datetime.datetime.now(datetime.UTC)
            _LOGGER.info(f"Re-trying fetching data for {entry.data[CONF_DEVICE_ID]}")
            data = await hass.async_add_executor_job(
                gpscj_get_position_from_session,
                entry.data[CONF_DEVICE_ID],
                entry.data[CONF_USER_ID],
                session
            )
            _LOGGER.info(f"Re-tried fetching data for {entry.data[CONF_DEVICE_ID]} successfully!")
            data["session_created"] = session_created.replace(microsecond=0).isoformat()
            return data

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="GPSCJ Tracker",
        update_method=async_update_data,
        update_interval=SCAN_INTERVAL
    )

    # Store coordinator before forwarding setup
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    _LOGGER.debug(f"In device_tracker async_setup_entry, entry.state: {entry.state}")
    if entry.state == ConfigEntryState.SETUP_IN_PROGRESS:
        _LOGGER.debug(f"ConfigEntryState.SETUP_IN_PROGRESS, running coordinator.async_config_entry_first_refresh()")
        await coordinator.async_config_entry_first_refresh()

    device_tracker = GPSCJTracker(coordinator, entry)
    async_add_entities([device_tracker])

    # Forward to sensors
    await hass.config_entries.async_forward_entry_setups(entry, [Platform.SENSOR])


class GPSCJTracker(CoordinatorEntity, TrackerEntity):
    """Representation of a GPSCJ tracked device."""

    def __init__(self, coordinator: DataUpdateCoordinator, entry: ConfigEntry):
        _LOGGER.debug(f"Initializing GPSCJTracker for {entry.data[CONF_USERNAME]}")
        super().__init__(coordinator)
        self.coordinator = coordinator
        self._entry = entry
        self._attr_unique_id = entry.entry_id
        self._attr_name = f"GPSCJ {entry.data[CONF_USERNAME]}"

    @property
    def latitude(self):
        """Return latitude from API data."""
        _LOGGER.debug(
            f"Getting latitude for {self._entry.data[CONF_USERNAME]}: {self.coordinator.data.get("latitude")}")
        return self.coordinator.data.get("latitude")

    @property
    def longitude(self):
        """Return longitude from API data."""
        _LOGGER.debug(
            f"Getting longitude for {self._entry.data[CONF_USERNAME]}: {self.coordinator.data.get("longitude")}")
        return self.coordinator.data.get("longitude")

    @property
    def location_accuracy(self) -> int:
        """Return GPS accuracy in meters."""
        _LOGGER.debug(
            f"Getting location_accuracy for {self._entry.data[CONF_USERNAME]}: signal_gps: {self.coordinator.data.get('signal_gps')}")
        if self.coordinator.data.get("signal_gps") > 9:
            return 10  # meters
        return 50  # meters

    @property
    def device_info(self):
        """Return device info to group sensors under the same device."""
        _LOGGER.debug(f"Getting device_info for {self._entry.data[CONF_USERNAME]}")
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            name=f"GPSCJ {self._entry.data[CONF_USERNAME]}",
            manufacturer="Some chinese manufacturer (Yuntrack/GPSCJ)",
            model="Chinese stuff",
            sw_version="1.0",
        )

    async def async_update(self):
        """Manually trigger an update."""
        _LOGGER.debug(f"Running async_request_refresh as async_update was called.")
        await self.coordinator.async_request_refresh()
