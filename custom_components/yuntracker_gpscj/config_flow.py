import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback

from .const import DOMAIN, CONF_USERNAME, CONF_PASSWORD, CONF_USER_ID, CONF_DEVICE_ID


class GPSCJConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for GPSCJ Tracker."""

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            return self.async_create_entry(title=user_input[CONF_DEVICE_ID], data=user_input)

        data_schema = vol.Schema({
            vol.Required(CONF_USERNAME): str,
            vol.Required(CONF_PASSWORD): str,
            vol.Required(CONF_USER_ID): str,
            vol.Required(CONF_DEVICE_ID): str,
        })

        return self.async_show_form(step_id="user", data_schema=data_schema, errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(entry):
        return GPSCJOptionsFlowHandler(entry)


class GPSCJOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options for GPSCJ Tracker."""

    def __init__(self, entry):
        self.entry = entry

    async def async_step_init(self, user_input=None):
        """Manage options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        data_schema = vol.Schema({
            vol.Required(CONF_USERNAME, default=self.entry.data[CONF_USERNAME]): str,
            vol.Required(CONF_PASSWORD, default=self.entry.data[CONF_PASSWORD]): str,
            vol.Required(CONF_USER_ID, default=self.entry.data[CONF_USER_ID]): str,
            vol.Required(CONF_DEVICE_ID, default=self.entry.data[CONF_DEVICE_ID]): str,
        })

        return self.async_show_form(step_id="init", data_schema=data_schema)
