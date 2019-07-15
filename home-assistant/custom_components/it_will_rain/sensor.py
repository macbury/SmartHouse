"""
Check if it will rain using darksky component
"""

import voluptuous as vol
import logging
import homeassistant.helpers.config_validation as cv
import async_timeout
import aiohttp
import asyncio
import homeassistant.util as util

from aiohttp.hdrs import AUTHORIZATION
from datetime import timedelta, datetime
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.const import CONF_NAME, CONF_ENTITY_ID, STATE_OFF, STATE_ON, STATE_UNKNOWN
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.config_validation import PLATFORM_SCHEMA

MIN_TIME_BETWEEN_SCANS = timedelta(seconds=15)
MIN_TIME_BETWEEN_FORCED_SCANS = timedelta(seconds=1)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
  vol.Required(CONF_ENTITY_ID): cv.string,
  vol.Required(CONF_NAME): cv.string,
})

_LOGGER = logging.getLogger(__name__)

def setup_platform(hass, config, add_devices, discovery_info=None):
  entity_id = config.get(CONF_ENTITY_ID)
  name = config.get(CONF_NAME)

  add_devices([ItWillRain(hass, entity_id, name)])


class ItWillRain(Entity):
  """Representation of a Sensor."""

  def __init__(self, hass, entity_id, name):
    """Initialize the sensor."""
    self.hass = hass
    self._entity_id = entity_id
    self._name = name
    self._state = STATE_UNKNOWN

  @property
  def name(self):
    """Return the name of the sensor."""
    return self._name

  @property
  def state(self):
    """Return the state of the sensor."""
    return self._state

  @util.Throttle(MIN_TIME_BETWEEN_SCANS, MIN_TIME_BETWEEN_FORCED_SCANS)
  async def async_update(self):
    state = self.hass.states.get(self._entity_id)
    if not state:
      _LOGGER.error('Entity does not exists')
      self._state = STATE_UNKNOWN
      return

    forecasts = state.attributes.get('forecast')

    if not forecasts:
      _LOGGER.error('There is no forecast')
      self._state = STATE_OFF
      return

    self._state = STATE_OFF

    for forecast in forecasts[0:9]:
      precipitation = float(forecast['precipitation'])
      if precipitation and precipitation >= 0.0:
        self._state = STATE_ON
      
