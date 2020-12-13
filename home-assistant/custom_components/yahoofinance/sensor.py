"""
A component which presents Yahoo Finance stock quotes.

https://github.com/InduPrakash/yahoofinance
"""

import asyncio
import logging
from datetime import timedelta

import aiohttp
import async_timeout
import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import ATTR_ATTRIBUTION, CONF_SCAN_INTERVAL
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity import Entity, async_generate_entity_id
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    ATTR_CURRENCY_SYMBOL,
    ATTR_SYMBOL,
    ATTRIBUTION,
    BASE,
    CONF_SHOW_TRENDING_ICON,
    CONF_SYMBOLS,
    CURRENCY_CODES,
    DATA_CURRENCY_SYMBOL,
    DATA_FINANCIAL_CURRENCY,
    DATA_REGULAR_MARKET_PREVIOUS_CLOSE,
    DATA_REGULAR_MARKET_PRICE,
    DATA_SHORT_NAME,
    DEFAULT_CURRENCY,
    DEFAULT_CURRENCY_SYMBOL,
    DEFAULT_ICON,
    DOMAIN,
    NUMERIC_DATA_KEYS,
    SERVICE_REFRESH,
    STRING_DATA_KEYS,
)

_LOGGER = logging.getLogger(__name__)
ENTITY_ID_FORMAT = DOMAIN + ".{}"
SCAN_INTERVAL = timedelta(hours=6)
DEFAULT_TIMEOUT = 10
DEFAULT_CONF_SHOW_TRENDING_ICON = False

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_SYMBOLS): vol.All(cv.ensure_list, [cv.string]),
        vol.Optional(CONF_SCAN_INTERVAL, default=SCAN_INTERVAL): cv.time_period,
        vol.Optional(
            CONF_SHOW_TRENDING_ICON, default=DEFAULT_CONF_SHOW_TRENDING_ICON
        ): cv.boolean,
    }
)


async def async_setup_platform(
    hass, config, async_add_entities, discovery_info=None
) -> None:
    """Set up the Yahoo Finance sensors."""
    symbols = config.get(CONF_SYMBOLS, [])

    # Make sure all symbols are in upper case
    symbols = [sym.upper() for sym in symbols]

    show_trending_icon = config.get(
        CONF_SHOW_TRENDING_ICON, DEFAULT_CONF_SHOW_TRENDING_ICON
    )

    coordinator = YahooSymbolUpdateCoordinator(
        symbols, hass, config.get(CONF_SCAN_INTERVAL)
    )
    await coordinator.async_refresh()

    sensors = []
    for symbol in symbols:
        sensors.append(
            YahooFinanceSensor(hass, coordinator, symbol, show_trending_icon)
        )

    # The True param fetches data first time before being written to HA
    async_add_entities(sensors, True)

    async def handle_refresh_symbols(_call):
        """Refresh symbol data."""
        _LOGGER.info("Processing refresh_symbols")
        await coordinator.async_request_refresh()

    hass.services.async_register(
        DOMAIN,
        SERVICE_REFRESH,
        handle_refresh_symbols,
    )

    _LOGGER.info("Added sensors for %s", symbols)


class YahooFinanceSensor(Entity):
    """Defines a Yahoo finance sensor."""

    _currency = DEFAULT_CURRENCY
    _icon = DEFAULT_ICON
    _market_price = None
    _short_name = None

    def __init__(
        self,
        hass,
        coordinator,
        symbol,
        show_trending_icon,
    ) -> None:
        """Initialize the sensor."""
        self._symbol = symbol
        self._coordinator = coordinator
        self.entity_id = async_generate_entity_id(ENTITY_ID_FORMAT, symbol, hass=hass)
        self._show_trending_icon = show_trending_icon

        self._attributes = {
            ATTR_ATTRIBUTION: ATTRIBUTION,
            ATTR_CURRENCY_SYMBOL: DEFAULT_CURRENCY_SYMBOL,
            ATTR_SYMBOL: self._symbol,
        }

        # Initialize all numeric attributes to None
        for key in NUMERIC_DATA_KEYS:
            self._attributes[key] = None

        _LOGGER.debug("Created %s", self.entity_id)

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        if self._short_name is not None:
            return self._short_name

        return self._symbol

    @property
    def should_poll(self) -> bool:
        """No need to poll. Coordinator notifies entity of updates."""
        return False

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._market_price

    @property
    def unit_of_measurement(self) -> str:
        """Return the unit of measurement of this entity, if any."""
        return self._currency

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return self._attributes

    @property
    def icon(self) -> str:
        """Return the icon to use in the frontend, if any."""
        return self._icon

    def fetch_data(self) -> None:
        """Fetch data and populate local fields."""
        data = self._coordinator.data
        if data is None:
            return

        symbol_data = data.get(self._symbol)
        if symbol_data is None:
            return

        self._short_name = symbol_data[DATA_SHORT_NAME]
        self._market_price = symbol_data[DATA_REGULAR_MARKET_PRICE]
        self._previous_close = symbol_data[DATA_REGULAR_MARKET_PREVIOUS_CLOSE]

        for key in NUMERIC_DATA_KEYS:
            self._attributes[key] = symbol_data[key]

        # Prefer currency over financialCurrency, for foreign symbols financialCurrency
        # can represent the remote currency. But financialCurrency can also be None.
        financialCurrency = symbol_data[DATA_FINANCIAL_CURRENCY]
        currency = symbol_data[DATA_CURRENCY_SYMBOL]

        _LOGGER.debug(
            "%s currency=%s financialCurrency=%s",
            self._symbol,
            ("None" if currency is None else currency),
            ("None" if financialCurrency is None else financialCurrency),
        )

        currency = currency or financialCurrency or DEFAULT_CURRENCY

        self._currency = currency.upper()
        lower_currency = self._currency.lower()

        # Fall back to currency based icon if there is no _previous_close value
        if self._show_trending_icon and not (self._previous_close is None):
            if self._market_price > self._previous_close:
                self._icon = "mdi:trending-up"
            elif self._market_price < self._previous_close:
                self._icon = "mdi:trending-down"
            else:
                self._icon = "mdi:trending-neutral"
        else:
            self._icon = "mdi:currency-" + lower_currency

        if lower_currency in CURRENCY_CODES:
            self._currency_symbol = CURRENCY_CODES[lower_currency]

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        self.fetch_data()
        return self._coordinator.last_update_success

    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""
        self._coordinator.async_add_listener(self.async_write_ha_state)

    async def async_will_remove_from_hass(self) -> None:
        """When entity will be removed from hass."""
        self._coordinator.async_remove_listener(self.async_write_ha_state)

    async def async_update(self) -> None:
        """Update symbol data."""
        await self._coordinator.async_request_refresh()


class YahooSymbolUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage Yahoo finance data update."""

    def __init__(self, symbols, hass, update_interval) -> None:
        """Initialize."""
        self._symbols = symbols
        self.data = None
        self.loop = hass.loop
        self.websession = async_get_clientsession(hass)

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=update_interval,
        )

    async def _async_update_data(self):
        """Fetch the latest data from the source."""
        try:
            await self.update()
        except () as error:
            raise UpdateFailed(error)
        return self.data

    async def get_json(self):
        """Get the JSON data."""
        json = None
        try:
            async with async_timeout.timeout(DEFAULT_TIMEOUT, loop=self.loop):
                response = await self.websession.get(BASE + ",".join(self._symbols))
                json = await response.json()

            _LOGGER.debug("Data = %s", json)
            self.last_update_success = True
        except asyncio.TimeoutError:
            _LOGGER.error("Timed out getting data")
            self.last_update_success = False
        except aiohttp.ClientError as exception:
            _LOGGER.error("Error getting data: %s", exception)
            self.last_update_success = False

        return json

    async def update(self):
        """Update data."""
        json = await self.get_json()
        if json is not None:
            if "error" in json:
                raise ValueError(json["error"]["info"])

            result = json["quoteResponse"]["result"]
            data = {}

            for item in result:
                symbol = item["symbol"]

                # Return data pieces which we care about, use 0 for missing numeric values
                data[symbol] = {}
                for key in NUMERIC_DATA_KEYS:
                    data[symbol][key] = item.get(key, 0)
                for key in STRING_DATA_KEYS:
                    data[symbol][key] = item.get(key)

                _LOGGER.debug(
                    "Updated %s=%s",
                    symbol,
                    data[symbol]["regularMarketPrice"],
                )

            self.data = data
            _LOGGER.info("Data updated")
