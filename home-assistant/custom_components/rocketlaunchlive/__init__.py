"""The Rocket Launch Live integration."""
import asyncio

import voluptuous as vol
import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.exceptions import ConfigEntryNotReady, PlatformNotReady

from rocketlaunchlive import RocketLaunchLive

from .const import DOMAIN, COORDINATOR, ROCKET_API

CONFIG_SCHEMA = vol.Schema({DOMAIN: vol.Schema({})}, extra=vol.ALLOW_EXTRA)
_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor"]

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the Rocket Launch Live component."""
    hass.data.setdefault(DOMAIN, {})

    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Rocket Launch Live from a config entry."""
    polling_interval = 60

    conf = entry.data

    if "api_key" in conf:
        api = RocketLaunchLive(key=conf["api_key"])
    else:
        api = RocketLaunchLive()

    try:
        await api.get_next_launches()
    except ConnectionError as error:
        _LOGGER.debug(f"Rocket Launch Live API: {error}")
        raise PlatformNotReady from error
        return False
    except ValueError as error:
        _LOGGER.debug(f"Rocket Launch Live API: {error}")
        raise ConfigEntryNotReady from error
        return False

    coordinator = RocketLaunchLiveUpdater(
        hass, 
        api=api, 
        name="RocketLaunchLive", 
        polling_interval=polling_interval,
    )

    await coordinator.async_refresh()
    
    if not coordinator.last_update_success:
        raise ConfigEntryNotReady

    hass.data[DOMAIN][entry.entry_id] = {
        COORDINATOR: coordinator,
        ROCKET_API: api
    }

    for component in PLATFORMS:
        _LOGGER.info("Setting up platform: %s", component)
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, component)
        )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, component)
                for component in PLATFORMS
            ]
        )
    )
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok

class RocketLaunchLiveUpdater(DataUpdateCoordinator):
    """Class to manage fetching update data from the Rocket Launch Live API."""

    def __init__(
        self,
        hass: HomeAssistant,
        api: str,
        name: str,
        polling_interval: int,
    ):
        """Initialize the global Rocket Launch Live data updater."""
        self.api = api

        super().__init__(
            hass = hass,
            logger = _LOGGER,
            name = name,
            update_interval = timedelta(seconds=polling_interval),
        )

    async def _async_update_data(self):
        """Fetch data from Rocket Launch Live API."""

        try:
            rocket_data = await self.api.get_next_launches()
        except ConnectionError as error:
            _LOGGER.info(f"Rocket Launch Live API: {error}")
            raise PlatformNotReady from error
        except ValueError as error:
            _LOGGER.info(f"Rocket Launch Live API: {error}")
            raise UpdateFailed from error

        launches = {}
        launch_id = 0
        for launch in rocket_data["result"]:
            launches[launch_id] = launch
            launch_id += 1
        return launches
