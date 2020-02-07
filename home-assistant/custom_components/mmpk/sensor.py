"""
Fetch information from busix instance
"""

import voluptuous as vol
import logging
import homeassistant.helpers.config_validation as cv
import async_timeout
import aiohttp
import asyncio
import json
import homeassistant.util as util

from dateutil.parser import parse
from aiohttp.hdrs import AUTHORIZATION
from datetime import timedelta, datetime, timezone

from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.const import CONF_NAME, STATE_UNKNOWN
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.config_validation import PLATFORM_SCHEMA

TIMEOUT = 10
MIN_TIME_BETWEEN_SCANS = timedelta(seconds=10)
MIN_TIME_BETWEEN_FORCED_SCANS = timedelta(seconds=5)
CONF_STOP_ID='stop_id'
CONF_DIRECTION='direction'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
  vol.Required(CONF_STOP_ID): cv.string,
  vol.Required(CONF_DIRECTION): cv.string,
  vol.Required(CONF_NAME): cv.string
})

_LOGGER = logging.getLogger(__name__)

def addSecs(tm, secs):
  fulldate = tm + timedelta(seconds=secs)
  return fulldate

def setup_platform(hass, config, add_devices, discovery_info=None):
  stop_id = config.get(CONF_STOP_ID)
  direction = config.get(CONF_DIRECTION)
  name = config.get(CONF_NAME)

  _LOGGER.info("Initializing sensor for: {}".format(stop_id))
  add_devices([PublicTransportSensor(hass, name, stop_id, direction)])

class PublicTransportSensor(Entity):
  """Representation of a Sensor."""

  def __init__(self, hass, name, stop_id, direction):
    """Initialize the sensor."""
    self.hass = hass
    self.websession = async_get_clientsession(hass)
    self._name = name
    self.stop_id = stop_id
    self.direction = direction
    self.data = {
      'stopName': '...',
      'actual': []
    }

  @property
  def name(self):
    """Return the name of the sensor."""
    return self._name

  @property
  def state(self):
    """Return the state of the sensor."""
    return self.next_departure

  @property
  def state_attributes(self):
    return {
      "direction": self.direction,
      "stop_name": self.stop_name,
      "departures": self.departures,
    }

  @property
  def stop_name(self):
    return self.data['stopName']

  @property
  def next_departure(self):
    if len(self.departures) > 0:
      return self.departures[0]['relativeTime']
    else:
      return STATE_UNKNOWN

  @property
  def departures(self):
    deps = []

    for departure in self.data['actual']:
      direction = departure['direction']
      _LOGGER.debug("Found route: {}".format(direction))
      if direction == self.direction:
        route_id = departure['patternText']
        time = addSecs(datetime.now(), departure['actualRelativeTime'])
        _LOGGER.debug("Adding route: {}".format(route_id))

        deps.append({
          'line': route_id,
          'direction': direction,
          'relativeTime': departure['actualRelativeTime'],
          'time': {
            'date': time.isoformat()
          }
        })

    return deps

  def query_url(self):
    return 'http://www.ttss.krakow.pl/internetservice/services/passageInfo/stopPassages/stop?mode=departure&language=pl&stop={}'.format(self.stop_id)

  @util.Throttle(MIN_TIME_BETWEEN_SCANS, MIN_TIME_BETWEEN_FORCED_SCANS)
  async def async_update(self):
    _LOGGER.info("Updating".format(self.query_url()))
    try:
      with async_timeout.timeout(TIMEOUT, loop=self.hass.loop):
        response = await self.websession.get(self.query_url())
        self.data = await response.json()
        _LOGGER.debug("Updating sensor: {}".format(self.data))
        _LOGGER.debug("next departure: {}".format(self.next_departure))
    except (asyncio.TimeoutError, aiohttp.ClientError, IndexError) as error:
      _LOGGER.error("Failed getting devices: %s", error)
