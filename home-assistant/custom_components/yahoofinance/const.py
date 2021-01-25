"""Constants for Yahoo Finance sensor."""

# Additional attributes exposed by the sensor
ATTR_CURRENCY_SYMBOL = "currencySymbol"
ATTR_SYMBOL = "symbol"
ATTR_TRENDING = "trending"

# Hass data
HASS_DATA_CONFIG = "config"
HASS_DATA_COORDINATOR = "coordinator"

# JSON data pieces
DATA_CURRENCY_SYMBOL = "currency"
DATA_FINANCIAL_CURRENCY = "financialCurrency"
DATA_SHORT_NAME = "shortName"

DATA_REGULAR_MARKET_PREVIOUS_CLOSE = "regularMarketPreviousClose"
DATA_REGULAR_MARKET_PRICE = "regularMarketPrice"

NUMERIC_DATA_KEYS = [
    "averageDailyVolume10Day",
    "averageDailyVolume3Month",
    "fiftyDayAverage",
    "fiftyDayAverageChange",
    "fiftyDayAverageChangePercent",
    "postMarketChange",
    "postMarketChangePercent",
    "postMarketPrice",
    "regularMarketChange",
    "regularMarketChangePercent",
    "regularMarketDayHigh",
    "regularMarketDayLow",
    DATA_REGULAR_MARKET_PREVIOUS_CLOSE,
    DATA_REGULAR_MARKET_PRICE,
    "regularMarketVolume",
    "twoHundredDayAverage",
    "twoHundredDayAverageChange",
    "twoHundredDayAverageChangePercent",
]

STRING_DATA_KEYS = [
    DATA_FINANCIAL_CURRENCY,
    DATA_SHORT_NAME,
    DATA_CURRENCY_SYMBOL,
]


ATTRIBUTION = "Data provided by Yahoo Finance"
BASE = "https://query1.finance.yahoo.com/v7/finance/quote?symbols="
CONF_DECIMAL_PLACES = "decimal_places"
CONF_SHOW_TRENDING_ICON = "show_trending_icon"
CONF_SYMBOLS = "symbols"
DEFAULT_CONF_SHOW_TRENDING_ICON = False
DEFAULT_CURRENCY = "USD"
DEFAULT_CURRENCY_SYMBOL = "$"
DEFAULT_DECIMAL_PLACES = 2
DEFAULT_ICON = "mdi:currency-usd"
DOMAIN = "yahoofinance"
SERVICE_REFRESH = "refresh_symbols"

CURRENCY_CODES = {
    "bdt": "৳",
    "brl": "R$",
    "btc": "₿",
    "cny": "¥",
    "eth": "Ξ",
    "eur": "€",
    "gbp": "£",
    "ils": "₪",
    "inr": "₹",
    "jpy": "¥",
    "krw": "₩",
    "kzt": "лв",
    "ngn": "₦",
    "php": "₱",
    "rial": "﷼",
    "rub": "₽",
    "sign": "",
    "try": "₺",
    "twd": "$",
    "usd": "$",
}
