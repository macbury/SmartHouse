"""
The Car Wash binary sensor.

For more details about this platform, please refer to the documentation at
https://github.com/Limych/ha-car_wash/
"""

# Base component constants
VERSION = "1.2.12"
ISSUE_URL = "https://github.com/Limych/ha-car_wash/issues"

CONF_WEATHER = "weather"
CONF_DAYS = "days"

DEFAULT_NAME = "Car Wash"
DEFAULT_DAYS = 2

BAD_CONDITIONS = [
    "lightning-rainy",
    "rainy",
    "pouring",
    "snowy",
    "snowy-rainy",
    "hail",
    "exceptional",
]
