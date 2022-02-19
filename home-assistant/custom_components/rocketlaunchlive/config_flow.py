"""Config flow for Rocket Launch Live - Next 5 Launches."""
import logging
import voluptuous as vol

from rocketlaunchlive import RocketLaunchLive

from homeassistant import config_entries
from homeassistant.helpers import config_entry_flow

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Rocket Launch Live."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        config_entry = self.hass.config_entries.async_entries(DOMAIN)
        if config_entry:
            return self.async_abort(reason="single_instance_allowed")

        if user_input is not None:
            if "api_key" in user_input:
                key = user_input["api_key"]
                api_client = RocketLaunchLive(key=key)
            else:
                api_client = RocketLaunchLive()

            try:
                await api_client.get_next_launches()
            except ValueError:
                errors["base"] = "invalid_auth"
            except ConnectionError:
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                if "api_key" in user_input:
                    await self.async_set_unique_id(user_input["api_key"])
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title="Rocket Launch Live", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Optional("api_key"): str,
                }
            ),
            errors=errors,
        )
