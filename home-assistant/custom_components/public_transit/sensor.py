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
MIN_TIME_BETWEEN_SCANS = timedelta(seconds=30)
MIN_TIME_BETWEEN_FORCED_SCANS = timedelta(seconds=1)
CONF_ENDPOINT = 'endpoint'
CONF_FROM = 'from'
CONF_TO = 'to'
CONF_COUNT = 'count'

QUERY = """
query($from: String!, $to: String!, $count: Int!) {
  departures(first: $count, from: $from, to: $to, at: "now"){
    edges {
      node {
        line {
          name
          kind
        }
        
        direction {
          start {
            name
          }
          
          target {
            name
          }
        }

        time {
          formatted
          date
        }
      }
    }
  }
}
"""

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
  vol.Required(CONF_ENDPOINT): cv.string,
  vol.Required(CONF_NAME): cv.string,
  vol.Required(CONF_FROM): cv.string,
  vol.Required(CONF_TO): cv.string,
  vol.Required(CONF_COUNT): cv.string
})

_LOGGER = logging.getLogger(__name__)

def setup_platform(hass, config, add_devices, discovery_info=None):
  endpoint = config.get(CONF_ENDPOINT)
  name = config.get(CONF_NAME)
  from_stop = config.get(CONF_FROM)
  to_stop = config.get(CONF_TO)
  count = int(config.get(CONF_COUNT))

  websession = async_get_clientsession(hass)

  add_devices([PublicTransportSensor(hass, websession, name, endpoint, from_stop, to_stop, count)])

class PublicTransportSensor(Entity):
  """Representation of a Sensor."""

  def __init__(self, hass, websession, name, endpoint, from_stop, to_stop, count):
    """Initialize the sensor."""
    self.hass = hass
    self.websession = websession
    self._name = name
    self.endpoint = endpoint
    self.from_stop = from_stop
    self.to_stop = to_stop
    self.departures = []
    self.count = count
    self.next_departure = STATE_UNKNOWN

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
      "from": self.from_stop,
      "to": self.to_stop,
      "departures": self.departures,
    }

  def extract(self, data):
    self.departures = []
    for node in data['departures']['edges']:
      self.departures.append(node['node'])
    if len(self.departures) > 0:
      date = parse(self.departures[0]['time']['date'])
      self.next_departure = round((date - datetime.now(timezone.utc)).total_seconds())
      if self.next_departure < 0:
        self.next_departure = 0
    else:
      self.next_departure = STATE_UNKNOWN

  @util.Throttle(MIN_TIME_BETWEEN_SCANS, MIN_TIME_BETWEEN_FORCED_SCANS)
  async def async_update(self):
    try:
      with async_timeout.timeout(TIMEOUT, loop=self.hass.loop):
        _LOGGER.error("POST: {}".format(self.endpoint))
        variables = { "from": self.from_stop, "to": self.to_stop, "count": self.count }
        response = await self.websession.post(self.endpoint, data={ "query": QUERY, "variables": json.dumps(variables) })
        data = await response.text()
        _LOGGER.error("Updating sensor: {}".format(data))
        self.extract(json.loads(data)['data'])
    except (asyncio.TimeoutError, aiohttp.ClientError, IndexError) as error:
      _LOGGER.error("Failed getting devices: %s", error)
      self.departures = []
