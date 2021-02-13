"""
The Yahoo finance component.

https://github.com/iprak/yahoofinance
"""

from datetime import timedelta
import logging
from typing import Union

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
    CONF_TARGET_CURRENCY,
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
MINIMUM_SCAN_INTERVAL = timedelta(seconds=30)
WEBSESSION_TIMEOUT = 15

BASIC_SYMBOL_SCHEMA = vol.All(cv.string, vol.Upper)

COMPLEX_SYMBOL_SCHEMA = vol.All(
    dict,
    vol.Schema(
        {
            vol.Required("symbol"): BASIC_SYMBOL_SCHEMA,
            vol.Optional(CONF_TARGET_CURRENCY): BASIC_SYMBOL_SCHEMA,
        }
    ),
)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_SYMBOLS): vol.All(
                    cv.ensure_list,
                    [vol.Any(BASIC_SYMBOL_SCHEMA, COMPLEX_SYMBOL_SCHEMA)],
                ),
                vol.Optional(
                    CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL
                ): vol.Any("none", "None", cv.positive_time_period),
                vol.Optional(CONF_TARGET_CURRENCY): vol.All(cv.string, vol.Upper),
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


def parse_scan_interval(scan_interval: Union[timedelta, str]) -> timedelta:
    """Parse and validate scan_interval."""
    if isinstance(scan_interval, str):
        if isinstance(scan_interval, str):
            if scan_interval.lower() == "none":
                scan_interval = None
            else:
                raise vol.Invalid(
                    f"Invalid {CONF_SCAN_INTERVAL} specified: {scan_interval}"
                )
    elif scan_interval < MINIMUM_SCAN_INTERVAL:
        raise vol.Invalid("Scan interval should be at least 30 seconds.")

    return scan_interval


def normalize_input(defined_symbols):
    """Normalize input and remove duplicates."""
    symbols = set()
    normalized_symbols = []

    for value in defined_symbols:
        if isinstance(value, str):
            if not (value in symbols):
                symbols.add(value)
                normalized_symbols.append({"symbol": value})
        else:
            if not (value["symbol"] in symbols):
                symbols.add(value["symbol"])
                normalized_symbols.append(value)

    return (list(symbols), normalized_symbols)


async def async_setup(hass, config) -> bool:
    domain_config = config.get(DOMAIN, {})
    defined_symbols = domain_config.get(CONF_SYMBOLS, [])

    symbols, normalized_symbols = normalize_input(defined_symbols)
    domain_config[CONF_SYMBOLS] = normalized_symbols

    scan_interval = parse_scan_interval(domain_config.get(CONF_SCAN_INTERVAL))

    # Populate parsed value into domain_config
    domain_config[CONF_SCAN_INTERVAL] = scan_interval

    coordinator = YahooSymbolUpdateCoordinator(symbols, hass, scan_interval)

    # Refresh coordinator to get initial symbol data
    _LOGGER.info(
        f"Requesting data from coordinator with update interval of {scan_interval}."
    )
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

        # get() ensures that we have an entry in symbol_data.
        for value in NUMERIC_DATA_KEYS:
            key = value[0]
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
            update_method=self._async_update,
            update_interval=update_interval,
        )

    def get_symbols(self):
        """Return symbols tracked by the coordinator."""
        return self._symbols

    def add_symbol(self, symbol):
        """Add symbol to the symbol list."""
        if symbol not in self._symbols:
            self._symbols.append(symbol)

            # Request a refresh to get data for the missing symbol.
            # This would have been called while data for sensor was being parsed.
            self.hass.async_create_task(self.async_request_refresh())

            _LOGGER.info(f"Added symbol {symbol} and requested update")
            return True

        return False

    async def get_json(self):
        """Get the JSON data."""
        json = None

        async with async_timeout.timeout(WEBSESSION_TIMEOUT, loop=self.loop):
            response = await self.websession.get(BASE + ",".join(self._symbols))
            json = await response.json()

        _LOGGER.debug("Data = %s", json)
        return json

    async def _async_update(self):
        """
        Return updated data if new JSON is valid.

        Don't catch any exceptions, they get properly handled in the caller
        (DataUpdateCoordinator.async_refresh) which also updates last_update_success.
        UpdateFailed is raised if JSON is invalid.
        """

        json = await self.get_json()

        if json is None:
            raise UpdateFailed("No data received")

        if "quoteResponse" not in json:
            raise UpdateFailed("Data invalid, 'quoteResponse' not found.")

        quoteResponse = json["quoteResponse"]  # pylint: disable=invalid-name

        if "error" in quoteResponse:
            if quoteResponse["error"] is not None:
                raise UpdateFailed(quoteResponse["error"])

        if "result" not in quoteResponse:
            raise UpdateFailed("Data invalid, no 'result' found")

        result = quoteResponse["result"]
        if result is None:
            raise UpdateFailed("Data invalid, 'result' is None")

        data = {}
        for symbol_data in result:
            symbol = symbol_data["symbol"]
            data[symbol] = self.parse_symbol_data(symbol_data)

            _LOGGER.debug(
                "Updated %s (%s)",
                symbol,
                data[symbol][DATA_REGULAR_MARKET_PRICE],
            )

        _LOGGER.info("Data updated")
        return data
