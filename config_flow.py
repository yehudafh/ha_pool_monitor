import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import config_validation as cv

from . import DOMAIN

class PoolMonitorConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="Pool Monitor", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("pool_volume"): cv.positive_int,
                vol.Required("pool_type"): vol.In(["salt", "chlorine"]),
                vol.Required("ph"): cv.entity_id,
                vol.Required("temp"): cv.entity_id,
                vol.Required("tds"): cv.entity_id,
                vol.Required("ec"): cv.entity_id,
                vol.Required("salinity"): cv.entity_id,
                vol.Required("orp"): cv.entity_id,
            })
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return PoolMonitorOptionsFlowHandler(config_entry)

class PoolMonitorOptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required("pool_volume", default=self.config_entry.data.get("pool_volume")): cv.positive_int,
                vol.Required("pool_type", default=self.config_entry.data.get("pool_type")): vol.In(["salt", "chlorine"]),
                vol.Required("ph", default=self.config_entry.data.get("ph")): cv.entity_id,
                vol.Required("temp", default=self.config_entry.data.get("temp")): cv.entity_id,
                vol.Required("tds", default=self.config_entry.data.get("tds")): cv.entity_id,
                vol.Required("ec", default=self.config_entry.data.get("ec")): cv.entity_id,
                vol.Required("salinity", default=self.config_entry.data.get("salinity")): cv.entity_id,
                vol.Required("orp", default=self.config_entry.data.get("orp")): cv.entity_id,
            })
        )
