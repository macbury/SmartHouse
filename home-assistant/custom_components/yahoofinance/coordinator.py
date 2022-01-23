"""
The Yahoo finance component.

https://github.com/iprak/yahoofinance
"""
from __future__ import annotations

from datetime import timedelta
import logging
from typing import Final

import async_timeout
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import event
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.event import async_track_point_in_utc_time
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util.dt import utcnow

from .const import (
    BASE,
    DATA_REGULAR_MARKET_PRICE,
    NUMERIC_DATA_DEFAULTS,
    NUMERIC_DATA_GROUPS,
    STRING_DATA_KEYS,
)

_LOGGER = logging.getLogger(__name__)
WEBSESSION_TIMEOUT: Final = 15
DELAY_ASYNC_REQUEST_REFRESH: Final = 5
FAILURE_ASYNC_REQUEST_REFRESH: Final = 20


class YahooSymbolUpdateCoordinator(DataUpdateCoordinator):
    """Yahoo finance data update coordinator."""

    @staticmethod
    def parse_symbol_data(symbol_data: dict) -> dict[str, any]:
        """Return data pieces which we care about, use 0 for missing numeric values."""
        data = {}

        # get() ensures that we have an entry in symbol_data.
        for data_group in NUMERIC_DATA_GROUPS.values():
            for value in data_group:
                key = value[0]

                # Default value for most missing numeric keys is 0
                default_value = NUMERIC_DATA_DEFAULTS.get(key, 0)

                data[key] = symbol_data.get(key, default_value)

        for key in STRING_DATA_KEYS:
            data[key] = symbol_data.get(key)

        return data

    @staticmethod
    def fix_conversion_symbol(symbol: str, symbol_data: any) -> str:
        """Fix the conversion symbol from data."""

        if symbol is None or symbol == "" or not symbol.endswith("=X"):
            return symbol

        # Data analysis showed that data for conversion symbol has 'shortName': 'USD/EUR'
        short_name = symbol_data["shortName"] or ""
        from_to = short_name.split("/")
        if len(from_to) != 2:
            return symbol

        from_currency = from_to[0]
        to_currency = from_to[1]
        if from_currency == "" or to_currency == "":
            return symbol

        conversion_symbol = f"{from_currency}{to_currency}=X"

        if conversion_symbol != symbol:
            _LOGGER.info(
                "Conversion symbol updated to %s from %s", conversion_symbol, symbol
            )

        return conversion_symbol

    def __init__(
        self, symbols: list[str], hass: HomeAssistant, update_interval: timedelta
    ) -> None:
        """Initialize."""
        self._symbols = symbols
        self.data = None
        self.loop = hass.loop
        self.websession = async_get_clientsession(hass)
        self._update_interval = update_interval
        self._failure_update_interval = timedelta(seconds=FAILURE_ASYNC_REQUEST_REFRESH)

        super().__init__(
            hass,
            _LOGGER,
            name="YahooSymbolUpdateCoordinator",
            update_method=self._async_update,
            update_interval=update_interval,
        )

    def get_next_update_interval(self) -> timedelta:
        """Get the update interval for the next async_track_point_in_utc_time call."""
        if self.last_update_success:
            return self._update_interval
        else:
            _LOGGER.warning(
                "Error obtaining data, retrying in %d seconds.",
                FAILURE_ASYNC_REQUEST_REFRESH,
            )
            return self._failure_update_interval

    @callback
    def _schedule_refresh(self) -> None:
        """Schedule a refresh."""
        if self._unsub_refresh:
            self._unsub_refresh()
            self._unsub_refresh = None

        # We _floor_ utcnow to create a schedule on a rounded second,
        # minimizing the time between the point and the real activation.
        # That way we obtain a constant update frequency,
        # as long as the update process takes less than a second

        update_interval = self.get_next_update_interval()
        if update_interval is not None:
            self._unsub_refresh = async_track_point_in_utc_time(
                self.hass,
                self._handle_refresh_interval,
                utcnow().replace(microsecond=0) + update_interval,
            )

    def get_symbols(self) -> list[str]:
        """Return symbols tracked by the coordinator."""
        return self._symbols

    async def _async_request_refresh_later(self, _now):
        """Request async_request_refresh."""
        await self.async_request_refresh()

    def add_symbol(self, symbol: str) -> bool:
        """Add symbol to the symbol list."""
        if symbol not in self._symbols:
            self._symbols.append(symbol)

            # Request a refresh to get data for the missing symbol.
            # This would have been called while data for sensor was being parsed.
            # async_request_refresh has debouncing built into it, so multiple calls
            # to add_symbol will still resut in single refresh.
            event.async_call_later(
                self.hass,
                DELAY_ASYNC_REQUEST_REFRESH,
                self._async_request_refresh_later,
            )

            _LOGGER.info(
                "Added %s and requested update in %d seconds.",
                symbol,
                DELAY_ASYNC_REQUEST_REFRESH,
            )
            return True

        return False

    async def get_json(self) -> dict:
        """Get the JSON data."""
        json = None
        url = BASE + ",".join(self._symbols)
        _LOGGER.debug("Requesting data from '%s'", url)

        async with async_timeout.timeout(WEBSESSION_TIMEOUT):
            response = await self.websession.get(url)
            json = await response.json()

        return json

    async def _async_update(self) -> dict:
        """
        Return updated data if new JSON is valid.

        The exception will get properly handled in the caller (DataUpdateCoordinator.async_refresh)
        which also updates last_update_success. UpdateFailed is raised if JSON is invalid.
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

        (error_encountered, data) = self.process_json_result(result)

        if error_encountered:
            _LOGGER.info("Data = %s", result)
        else:
            _LOGGER.debug("Data = %s", result)

        _LOGGER.info("All symbols updated")
        return data

    def process_json_result(self, result) -> tuple[bool, dict]:
        """Process json result and return (error status, updated data)."""

        # Using current data if available. If returned data is missing then we might be
        # able to use previous data.
        data = self.data or {}

        symbols = self._symbols.copy()
        error_encountered = False

        for symbol_data in result:
            symbol = symbol_data["symbol"]

            if symbol in symbols:
                symbols.remove(symbol)
            else:
                # Sometimes data for USDEUR=X just contains EUR=X, try to fix such
                # symbols. The source of truth is the symbol in the data since data
                # pieces could be out of order.
                fixed_symbol = self.fix_conversion_symbol(symbol, symbol_data)

                if fixed_symbol in symbols:
                    symbols.remove(fixed_symbol)
                    symbol = fixed_symbol
                else:
                    _LOGGER.warning("Received %s not in symbol list", symbol)
                    error_encountered = True

            data[symbol] = self.parse_symbol_data(symbol_data)

            _LOGGER.debug(
                "Updated %s to %s",
                symbol,
                data[symbol][DATA_REGULAR_MARKET_PRICE],
            )

        if len(symbols) > 0:
            _LOGGER.warning("No data received for %s", symbols)
            error_encountered = True

        return (error_encountered, data)
