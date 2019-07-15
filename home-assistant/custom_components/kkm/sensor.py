"""
Fetch how many days you have left on your train card from http://www.mpk.krakow.pl/
"""

import voluptuous as vol
import logging
import homeassistant.helpers.config_validation as cv
import async_timeout
import aiohttp
import asyncio
import homeassistant.util as util

from datetime import timedelta, datetime
import time
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.const import CONF_NAME, STATE_OFF, STATE_ON
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.config_validation import PLATFORM_SCHEMA

REQUIREMENTS = ['beautifulsoup4==4.6.3']

CONF_IDENTITY = 'identity'
CONF_CITY_CARD = 'city_card'
TIMEOUT = 60
MIN_TIME_BETWEEN_SCANS = timedelta(minutes=60)
MIN_TIME_BETWEEN_FORCED_SCANS = timedelta(seconds=30)
ENDPOINT="http://www.mpk.krakow.pl/pl/sprawdz-waznosc-biletu/index,1.html"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
  vol.Required(CONF_IDENTITY): cv.string,
  vol.Required(CONF_CITY_CARD): cv.string,
  vol.Required(CONF_NAME): cv.string
})

_LOGGER = logging.getLogger(__name__)

def setup_platform(hass, config, add_devices, discovery_info=None):
  city_card_id = config.get(CONF_CITY_CARD)
  identity_id = config.get(CONF_IDENTITY)
  name = config.get(CONF_NAME)

  add_devices([KKMSensor(hass, city_card_id, identity_id, name)])

class KKMSensor(Entity):
  """Representation of a Sensor."""

  def __init__(self, hass, city_card_id, identity_id, name):
    """Initialize the sensor."""
    self.hass = hass
    self.websession = async_get_clientsession(hass)
    self.city_card_id = city_card_id
    self.identity_id = identity_id
    self._lines = []
    self._name = name
    self._expire_at = None
    self._state = STATE_OFF

  @property
  def name(self):
    """Return the name of the sensor."""
    return self._name

  @property
  def state(self):
    """Return the state of the sensor."""
    return self._state

  def days(self):
    if self._expire_at:
      days = (self._expire_at - datetime.today()).days
      if days < 0:
        days = 0
      return days
    else:
      return 0

  def extract_date(self, raw_data):
    try:
      date = raw_data.select(".kkm-card div:nth-of-type(8) b")[0].string
      d = time.strptime(date, '%Y-%m-%d')
      self._expire_at = datetime(*d[:6])
      self._lines = raw_data.select(".kkm-card div:nth-of-type(10) b")[0].string.split(',')
    except IndexError as error:
      _LOGGER.error("Failed to extract date from page: %s", error)

  @property
  def state_attributes(self):
    return {
      'days': self.days(),
      'expire_at': self._expire_at,
      'lines': self._lines
    }

  @util.Throttle(MIN_TIME_BETWEEN_SCANS, MIN_TIME_BETWEEN_FORCED_SCANS)
  async def async_update(self):
    try:
      from bs4 import BeautifulSoup
      with async_timeout.timeout(TIMEOUT, loop=self.hass.loop):
        response = await self.websession.get(ENDPOINT, params={ "identityNumber": self.identity_id, "cityCardNumber": self.city_card_id })
        data = await response.text()
        #_LOGGER.debug(data)
        raw_data = BeautifulSoup(data, 'html.parser')
        self.extract_date(raw_data)

        if self.days() == 0:
          self._state = STATE_OFF
        else:
          self._state = STATE_ON
    except (asyncio.TimeoutError, aiohttp.ClientError) as error:
      _LOGGER.error("Failed getting kkm information: %s", error)
