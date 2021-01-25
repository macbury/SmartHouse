"""
The Yahoo finance component.

https://github.com/iprak/yahoofinance
"""

import asyncio
from datetime import timedelta
import logging

import aiohttp
import async_timeout
from homeassistant.const import CONF_SCAN_INTERVAL
from homeassistant.helpers import discovery
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
import voluptuous as vol

from .const import (
    BASE,
    CONF_DECIMAL_PLACES,
    CONF_SHOW_TRENDING_ICON,
    CONF_SYMBOLS,
    DATA_REGULAR_MARKET_PRICE,
    DEFAULT_CONF_SHOW_TRENDING_ICON,
    DEFAULT_DECIMAL_PLACES,
    DOMAIN,
    HASS_DATA_CONFIG,
    HASS_DATA_COORDINATOR,
    NUMERIC_DATA_KEYS,
    SERVICE_REFRESH,
    STRING_DATA_KEYS,
)

_LOGGER = logging.getLogger(__name__)
DEFAULT_SCAN_INTERVAL = timedelta(hours=6)
WEBSESSION_TIMEOUT = 15

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_SYMBOLS): vol.All(cv.ensure_list, [cv.string]),
                vol.Optional(
                    CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL
                ): cv.time_period,
                vol.Optional(
                    CONF_SHOW_TRENDING_ICON, default=DEFAULT_CONF_SHOW_TRENDING_ICON
                ): cv.boolean,
                vol.Optional(
                    CONF_DECIMAL_PLACES, default=DEFAULT_DECIMAL_PLACES
                ): vol.Coerce(int),
            }
        )
    },
    # The complete HA configuration is passed down to`async_setup`, allow the extra keys.
    extra=vol.ALLOW_EXTRA,
)


async def async_setup(hass, config) -> bool:
    """Set up the Yahoo Finance sensors."""

    domain_config = config.get(DOMAIN, {})
    symbols = domain_config.get(CONF_SYMBOLS, [])

    # Convert all symbols to upper case and save them back
    symbols = [sym.upper() for sym in symbols]
    domain_config[CONF_SYMBOLS] = symbols

    coordinator = YahooSymbolUpdateCoordinator(
        symbols, hass, domain_config.get(CONF_SCAN_INTERVAL)
    )

    # Refresh coordinator to get initial symbol data
    _LOGGER.debug("Requesting initial data from coordinator")
    await coordinator.async_refresh()

    # Pass down the coordinator and config to platforms.
    hass.data[DOMAIN] = {
        HASS_DATA_COORDINATOR: coordinator,
        HASS_DATA_CONFIG: domain_config,
    }

    async def handle_refresh_symbols(_call):
        """Refresh symbol data."""
        _LOGGER.info("Processing refresh_symbols")
        await coordinator.async_request_refresh()

    hass.services.async_register(
        DOMAIN,
        SERVICE_REFRESH,
        handle_refresh_symbols,
    )

    if not coordinator.last_update_success:
        _LOGGER.debug("Coordinator did not report any data, requesting async_refresh")
        hass.async_create_task(coordinator.async_request_refresh())

    hass.async_create_task(
        discovery.async_load_platform(hass, "sensor", DOMAIN, {}, config)
    )

    return True


class YahooSymbolUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage Yahoo finance data update."""

    @staticmethod
    def parse_symbol_data(symbol_data):
        """Return data pieces which we care about, use 0 for missing numeric values."""
        data = {}
        for key in NUMERIC_DATA_KEYS:
            data[key] = symbol_data.get(key, 0)
        for key in STRING_DATA_KEYS:
            data[key] = symbol_data.get(key)
        return data

    def __init__(self, symbols, hass, update_interval) -> None:
        """Initialize."""
        self._symbols = symbols
        self.data = None
        self.loop = hass.loop
        self.websession = async_get_clientsession(hass)

        super().__init__(
            hass,
            _LOGGER,
            name="YahooSymbolUpdateCoordinator",
            update_method=self._update,
            update_interval=update_interval,
        )

    async def get_json(self):
        """Get the JSON data."""
        json = None

        async with async_timeout.timeout(WEBSESSION_TIMEOUT, loop=self.loop):
            response = await self.websession.get(BASE + ",".join(self._symbols))
            json = await response.json()

        _LOGGER.debug("Data = %s", json)
        return json

    async def _update(self):
        """
        Return updated data if new JSON is valid.

        Don't catch any exceptions, they get properly handled in the caller
        (DataUpdateCoordinator.async_refresh) which also updates last_update_success.
        UpdateFailed is raised if JSON is invalid.
        """

        json = await self.get_json()

        if json is None:
            raise UpdateFailed("No data received")

        if not "quoteResponse" in json:
            raise UpdateFailed("Data invalid, 'quoteResponse' not found.")

        quoteResponse = json["quoteResponse"]  # pylint: disable=invalid-name

        if "error" in quoteResponse:
            if quoteResponse["error"] is not None:
                raise UpdateFailed(quoteResponse["error"])

        if not "result" in quoteResponse:
            raise UpdateFailed("Data invalid, no 'result' found")

        result = quoteResponse["result"]
        if result is None:
            raise UpdateFailed("Data invalid, 'result' is None")

        data = {}
        for symbol_data in result:
            symbol = symbol_data["symbol"]
            data[symbol] = self.parse_symbol_data(symbol_data)

            _LOGGER.debug(
                "Updated %s=%s",
                symbol,
                data[symbol][DATA_REGULAR_MARKET_PRICE],
            )

        _LOGGER.info("Data updated")
        return data
