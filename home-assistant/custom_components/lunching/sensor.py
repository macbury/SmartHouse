"""
Fetch information from lunching.pl about ordered food
"""

import voluptuous as vol
import logging
import homeassistant.helpers.config_validation as cv
import async_timeout
import aiohttp
import asyncio
import homeassistant.util as util
import re

from aiohttp.hdrs import AUTHORIZATION
from datetime import timedelta, datetime
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.const import CONF_PASSWORD, CONF_NAME, CONF_USERNAME, STATE_OFF, STATE_ON
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.config_validation import PLATFORM_SCHEMA

TIMEOUT = 10
MIN_TIME_BETWEEN_SCANS = timedelta(seconds=60)
MIN_TIME_BETWEEN_FORCED_SCANS = timedelta(seconds=1)
ENDPOINT="https://api.lunching.pl/api/account/order-list"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
  vol.Required(CONF_NAME): cv.string,
  vol.Required(CONF_USERNAME): cv.string,
  vol.Required(CONF_PASSWORD): cv.string
})

_LOGGER = logging.getLogger(__name__)

def setup_platform(hass, config, add_devices, discovery_info=None):
  username = config.get(CONF_USERNAME)
  password = config.get(CONF_PASSWORD)
  name = config.get(CONF_NAME)

  websession = async_get_clientsession(hass)

  add_devices([LunchingSensor(hass, websession, name, username, password)])


class LunchingSensor(Entity):
  """Representation of a Sensor."""

  def __init__(self, hass, websession, name, username, password):
    """Initialize the sensor."""
    self.hass = hass
    self.websession = websession
    self._name = name
    self.username = username
    self.password = password
    self._meal = None
    self._deliver_from = None
    self._deliver_to = None

  @property
  def name(self):
    """Return the name of the sensor."""
    return self._name

  @property
  def state(self):
    """Return the state of the sensor."""
    if self._meal:
      return STATE_ON
    else:
      return STATE_OFF

  @property
  def state_attributes(self):
    return {
      'meal': self._meal,
      'deliver_to': self._deliver_to,
      'deliver_from': self._deliver_from
    }

  def extract_deilver_date(self, text):
    match = re.search('dziś (\d{1,2}):(\d{1,2}) - (\d{1,2}):(\d{1,2})', text)
    today = datetime.now()
    if match:
      self._deliver_from = today.replace(hour=int(match.group(1)), minute=int(match.group(2)), second=0, microsecond=0)
      self._deliver_to = today.replace(hour=int(match.group(3)), minute=int(match.group(4)), second=0, microsecond=0)

  @util.Throttle(MIN_TIME_BETWEEN_SCANS, MIN_TIME_BETWEEN_FORCED_SCANS)
  async def async_update(self):
    try:
      auth = aiohttp.BasicAuth(self.username, self.password)
      with async_timeout.timeout(TIMEOUT, loop=self.hass.loop):
        response = await self.websession.get(ENDPOINT, auth=auth)
        data = await response.json(content_type=None)
        if len(data) > 0:
          _LOGGER.debug("Updating sensor: {}".format(data))
          entry = data[0]
          self._meal = entry['meal']
          self.extract_deilver_date(entry['deliveryDate'])
        else:
          _LOGGER.debug("No data to update: {}".format(data))
          self._deliver_from = None
          self._deliver_to = None
          self._meal = None
    except (asyncio.TimeoutError, aiohttp.ClientError, IndexError) as error:
      _LOGGER.error("Failed getting devices: %s", error)
