"""
A component which presents Yahoo Finance stock quotes.

https://github.com/iprak/yahoofinance
"""

from __future__ import annotations

import datetime
import logging
from timeit import default_timer as timer
from typing import Union

from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN
from homeassistant.const import ATTR_ATTRIBUTION
from homeassistant.helpers.entity import async_generate_entity_id
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import slugify

from custom_components.yahoofinance import SymbolDefinition, convert_to_float
from custom_components.yahoofinance.coordinator import YahooSymbolUpdateCoordinator

from .const import (
    ATTR_CURRENCY_SYMBOL,
    ATTR_DIVIDEND_DATE,
    ATTR_MARKET_STATE,
    ATTR_QUOTE_SOURCE_NAME,
    ATTR_QUOTE_TYPE,
    ATTR_SYMBOL,
    ATTR_TRENDING,
    ATTRIBUTION,
    CONF_DECIMAL_PLACES,
    CONF_SHOW_TRENDING_ICON,
    CONF_SYMBOLS,
    CURRENCY_CODES,
    DATA_CURRENCY_SYMBOL,
    DATA_DIVIDEND_DATE,
    DATA_FINANCIAL_CURRENCY,
    DATA_MARKET_STATE,
    DATA_QUOTE_SOURCE_NAME,
    DATA_QUOTE_TYPE,
    DATA_REGULAR_MARKET_PREVIOUS_CLOSE,
    DATA_REGULAR_MARKET_PRICE,
    DATA_SHORT_NAME,
    DEFAULT_CURRENCY,
    DEFAULT_ICON,
    DEFAULT_NUMERIC_DATA_GROUP,
    DOMAIN,
    HASS_DATA_CONFIG,
    HASS_DATA_COORDINATOR,
    NUMERIC_DATA_GROUPS,
)

_LOGGER = logging.getLogger(__name__)
ENTITY_ID_FORMAT = SENSOR_DOMAIN + "." + DOMAIN + "_{}"


async def async_setup_platform(hass, _config, async_add_entities, _discovery_info=None):
    """Set up the Yahoo Finance sensor platform."""

    coordinator = hass.data[DOMAIN][HASS_DATA_COORDINATOR]
    domain_config = hass.data[DOMAIN][HASS_DATA_CONFIG]
    symbol_definitions: list[SymbolDefinition] = domain_config[CONF_SYMBOLS]

    sensors = [
        YahooFinanceSensor(hass, coordinator, symbol, domain_config)
        for symbol in symbol_definitions
    ]

    async_add_entities(sensors, update_before_add=False)
    _LOGGER.info("Entities added for %s", [item.symbol for item in symbol_definitions])


class YahooFinanceSensor(CoordinatorEntity):
    """Represents a Yahoo finance entity."""

    _currency = DEFAULT_CURRENCY
    _icon = DEFAULT_ICON
    _market_price = None
    _short_name = None
    _target_currency = None
    _original_currency = None
    _last_available_timer = None

    def __init__(
        self,
        hass,
        coordinator: YahooSymbolUpdateCoordinator,
        symbol_definition: SymbolDefinition,
        domain_config,
    ) -> None:
        """Initialize the YahooFinance entity."""
        super().__init__(coordinator)

        symbol = symbol_definition.symbol
        self._symbol = symbol
        self._show_trending_icon = domain_config[CONF_SHOW_TRENDING_ICON]
        self._decimal_places = domain_config[CONF_DECIMAL_PLACES]
        self._previous_close = None
        self._target_currency = symbol_definition.target_currency

        self._unique_id = symbol
        self.entity_id = async_generate_entity_id(ENTITY_ID_FORMAT, symbol, hass=hass)

        # _attr_extra_state_attributes is returned by extra_state_attributes
        self._attr_extra_state_attributes = {
            ATTR_ATTRIBUTION: ATTRIBUTION,
            ATTR_CURRENCY_SYMBOL: None,
            ATTR_SYMBOL: symbol,
            ATTR_QUOTE_TYPE: None,
            ATTR_QUOTE_SOURCE_NAME: None,
            ATTR_MARKET_STATE: None,
        }

        # List of groups to include as attributes
        self._numeric_data_to_include = []

        # pylint: disable=consider-using-dict-items

        # Initialize all numeric attributes which we want to include to None
        for group in NUMERIC_DATA_GROUPS:
            if group == DEFAULT_NUMERIC_DATA_GROUP or domain_config.get(group, True):
                for value in NUMERIC_DATA_GROUPS[group]:
                    self._numeric_data_to_include.append(value)

                    key = value[0]
                    self._attr_extra_state_attributes[key] = None

        # Delay initial data population to `available` which is called from `_async_write_ha_state`
        _LOGGER.debug(
            "Created entity for target_currency=%s",
            self._target_currency,
        )

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return self._unique_id

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        if self._short_name is not None:
            return self._short_name

        return self._symbol

    @property
    def state(self) -> StateType:
        """Return the state of the sensor."""
        return self._round(self._market_price)

    @property
    def unit_of_measurement(self) -> str:
        """Return the unit of measurement of this entity, if any."""
        return self._currency

    @property
    def icon(self) -> str:
        """Return the icon to use in the frontend, if any."""
        return self._icon

    def _round(self, value: Union[float, None]) -> Union[float, int, None]:
        """Return formatted value based on decimal_places."""
        if value is None:
            return None

        if self._decimal_places < 0:
            return value
        if self._decimal_places == 0:
            return int(value)

        return round(value, self._decimal_places)

    def _get_target_currency_conversion(self) -> Union[float, None]:
        value = None

        if self._target_currency and self._original_currency:
            if self._target_currency == self._original_currency:
                _LOGGER.info("%s No conversion necessary", self._symbol)
                return None

            conversion_symbol = (
                f"{self._original_currency}{self._target_currency}=X".upper()
            )
            data = self.coordinator.data

            if data is not None:
                symbol_data = data.get(conversion_symbol)

                if symbol_data is not None:
                    value = symbol_data[DATA_REGULAR_MARKET_PRICE]
                    _LOGGER.debug("%s %s is %s", self._symbol, conversion_symbol, value)
                else:
                    _LOGGER.debug(
                        "%s No data found for %s",
                        self._symbol,
                        conversion_symbol,
                    )
                    self.coordinator.add_symbol(conversion_symbol)

        return value

    @staticmethod
    def safe_convert(
        value: Union[float, None], conversion: Union[float, None]
    ) -> Union[float, None]:
        """Return the converted value. The original value is returned if there is no conversion."""
        if value is None:
            return None
        if conversion is None:
            return value
        return value * conversion

    @staticmethod
    def parse_dividend_date(dividend_date_timestamp) -> str | None:
        """Parse dividendDate JSON element."""

        dividend_date_timestamp = convert_to_float(dividend_date_timestamp)
        if dividend_date_timestamp is None:
            return None

        dividend_date = datetime.datetime.utcfromtimestamp(dividend_date_timestamp)
        dividend_date_date = dividend_date.date()
        return dividend_date_date.isoformat()

    def _update_original_currency(self, symbol_data) -> bool:
        """Update the original currency."""

        # Symbol currency does not change so calculate it only once
        if self._original_currency is not None:
            return

        # Prefer currency over financialCurrency, for foreign symbols financialCurrency
        # can represent the remote currency. But financialCurrency can also be None.
        financial_currency = symbol_data[DATA_FINANCIAL_CURRENCY]
        currency = symbol_data[DATA_CURRENCY_SYMBOL]

        _LOGGER.debug(
            "%s currency=%s financialCurrency=%s",
            self._symbol,
            currency,
            financial_currency,
        )

        self._original_currency = currency or financial_currency or DEFAULT_CURRENCY

    def _update_properties(self) -> None:
        """Update local fields."""

        data = self.coordinator.data
        if data is None:
            _LOGGER.debug("%s Coordinator data is None", self._symbol)
            return

        symbol_data: dict = data.get(self._symbol)
        if symbol_data is None:
            _LOGGER.debug("%s Symbol data is None", self._symbol)
            return

        self._update_original_currency(symbol_data)
        conversion = self._get_target_currency_conversion()

        self._short_name = symbol_data[DATA_SHORT_NAME]

        market_price = symbol_data[DATA_REGULAR_MARKET_PRICE]
        self._market_price = self.safe_convert(market_price, conversion)
        # _market_price gets rounded in the `state` getter.

        if conversion:
            _LOGGER.info(
                "%s converted %s X %s = %s",
                self._symbol,
                market_price,
                conversion,
                self._market_price,
            )

        self._previous_close = self.safe_convert(
            symbol_data[DATA_REGULAR_MARKET_PREVIOUS_CLOSE], conversion
        )

        for value in self._numeric_data_to_include:
            key = value[0]
            attr_value = symbol_data[key]

            # Convert if currency value
            if value[1]:
                attr_value = self.safe_convert(attr_value, conversion)

            self._attr_extra_state_attributes[key] = self._round(attr_value)

        # Add some other string attributes
        self._attr_extra_state_attributes[ATTR_QUOTE_TYPE] = symbol_data[
            DATA_QUOTE_TYPE
        ]
        self._attr_extra_state_attributes[ATTR_QUOTE_SOURCE_NAME] = symbol_data[
            DATA_QUOTE_SOURCE_NAME
        ]
        self._attr_extra_state_attributes[ATTR_MARKET_STATE] = symbol_data[
            DATA_MARKET_STATE
        ]

        self._attr_extra_state_attributes[
            ATTR_DIVIDEND_DATE
        ] = self.parse_dividend_date(symbol_data.get(DATA_DIVIDEND_DATE))

        # Use target_currency if we have conversion data. Otherwise keep using the
        # currency from data.
        if conversion is not None:
            currency = self._target_currency or self._original_currency
        else:
            currency = self._original_currency

        self._currency = currency.upper()
        lower_currency = self._currency.lower()

        trending_state = self._calc_trending_state()

        # Fall back to currency based icon if there is no trending state
        if trending_state is not None:
            self._attr_extra_state_attributes[ATTR_TRENDING] = trending_state

            if self._show_trending_icon:
                self._icon = f"mdi:trending-{trending_state}"
            else:
                self._icon = f"mdi:currency-{lower_currency}"
        else:
            self._icon = f"mdi:currency-{lower_currency}"

        # If this one of the known currencies, then include the correct currency symbol.
        # Don't show $ as the CurrencySymbol even if we can't get one.
        self._attr_extra_state_attributes[ATTR_CURRENCY_SYMBOL] = CURRENCY_CODES.get(
            lower_currency
        )

    def _calc_trending_state(self) -> Union[str, None]:
        """Return the trending state for the symbol."""
        if self._market_price is None or self._previous_close is None:
            return None

        if self._market_price > self._previous_close:
            return "up"
        if self._market_price < self._previous_close:
            return "down"

        return "neutral"

    @property
    def available(self) -> bool:
        """Return if entity is available."""

        current_timer = timer()

        # Limit data update if available was invoked within 400 ms.
        # This matched the slow entity reporting done in Entity.
        if (self._last_available_timer is None) or (
            (current_timer - self._last_available_timer) > 0.4
        ):
            self._update_properties()
            self._last_available_timer = current_timer

        return self.coordinator.last_update_success
