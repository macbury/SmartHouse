"""
Fetch how much work time is harvested on getharvest.com
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
from homeassistant.const import CONF_TOKEN, CONF_NAME, STATE_OFF, STATE_ON
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.config_validation import PLATFORM_SCHEMA

CONF_ACCOUNT_ID = 'account_id'
TIMEOUT = 10
MIN_TIME_BETWEEN_SCANS = timedelta(seconds=15)
MIN_TIME_BETWEEN_FORCED_SCANS = timedelta(seconds=1)
ENDPOINT="https://api.harvestapp.com/v2/time_entries"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
  vol.Required(CONF_ACCOUNT_ID): cv.string,
  vol.Required(CONF_TOKEN): cv.string,
  vol.Required(CONF_NAME): cv.string
})

_LOGGER = logging.getLogger(__name__)

def setup_platform(hass, config, add_devices, discovery_info=None):
  account_id = config.get(CONF_ACCOUNT_ID)
  token = config.get(CONF_TOKEN)
  name = config.get(CONF_NAME)

  websession = async_get_clientsession(hass)

  add_devices([HarvestSensor(hass, websession, account_id, token, name)])


class HarvestSensor(Entity):
  """Representation of a Sensor."""

  def __init__(self, hass, websession, account_id, token, name):
    """Initialize the sensor."""
    self.hass
    self.websession = websession
    self.account_id = account_id
    self.token = token
    self._name = name
    self._minutes = 0
    self._state = None

  @property
  def name(self):
    """Return the name of the sensor."""
    return self._name

  @property
  def state(self):
    """Return the state of the sensor."""
    if self._state:
      return STATE_ON
    else:
      return STATE_OFF

  @property
  def state_attributes(self):
    return {
      'minutes': self._minutes
    }

  def is_active(self, data):
    for entry in data['time_entries']:
      if entry['is_running']:
        return True
    return False

  def calculate_time(self, data):
    time_entries = data['time_entries']
    minutes = [round(entry['hours'] * 60.0) for entry in time_entries]
    return sum(minutes)

  @util.Throttle(MIN_TIME_BETWEEN_SCANS, MIN_TIME_BETWEEN_FORCED_SCANS)
  async def async_update(self):
    headers = {
      AUTHORIZATION: "Bearer {}".format(self.token),
      "Harvest-Account-ID": self.account_id
    }
    try:
      with async_timeout.timeout(TIMEOUT, loop=self.hass.loop):
        response = await self.websession.get(ENDPOINT, headers=headers, params={ "from": datetime.today().strftime("%Y-%m-%d") })
        data = await response.json(content_type=None)
        self._state = self.is_active(data)
        self._minutes = self.calculate_time(data)
        #_LOGGER.info("Data: {}".format(data))
    except (asyncio.TimeoutError, aiohttp.ClientError, IndexError) as error:
      _LOGGER.error("Failed getting devices: %s", error)
