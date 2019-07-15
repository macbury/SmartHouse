import urllib.parse
import async_timeout
import aiohttp
import asyncio
import logging
import voluptuous as vol
import homeassistant.util as util
import voluptuous as vol

from datetime import timedelta
from homeassistant.helpers.aiohttp_client import async_get_clientsession

_LOGGER      = logging.getLogger(__name__)

MIN_TIME_BETWEEN_SCANS = timedelta(seconds=3)
MIN_TIME_BETWEEN_FORCED_SCANS = timedelta(seconds=1)

from homeassistant.helpers import config_validation as cv

from homeassistant.components.media_player.const import (
  MEDIA_TYPE_CHANNEL,
  SUPPORT_TURN_ON,
  SUPPORT_TURN_OFF,
  SUPPORT_VOLUME_MUTE,
  SUPPORT_SELECT_SOURCE,
  SUPPORT_VOLUME_SET,
)

from homeassistant.components.media_player import (
  MediaPlayerDevice,
  MEDIA_PLAYER_SCHEMA
)

from homeassistant.const import (
  CONF_NAME,
  CONF_HOST,
  STATE_IDLE,
  STATE_PLAYING,
  STATE_OFF
)

MULTI_ROOM_SOURCE_TYPE = [
  'optical',
  'soundshare',
  'hdmi',
  'wifi',
  'aux',
  'bt'
]

BOOL_OFF = 'off'
BOOL_ON = 'on'
TIMEOUT = 10
SUPPORT_SAMSUNG_MULTI_ROOM = SUPPORT_VOLUME_SET | SUPPORT_VOLUME_MUTE | SUPPORT_SELECT_SOURCE

CONF_MAX_VOLUME = 'max_volume'
CONF_PORT = 'port'

PLATFORM_SCHEMA = vol.Schema({
  vol.Optional('platform', default='samsung_multi_room'): cv.string,
  vol.Optional(CONF_NAME, default='soundbar'): cv.string,
  vol.Optional(CONF_HOST, default='127.0.0.1'): cv.string,
  vol.Optional(CONF_PORT, default='55001'): cv.string,
  vol.Optional(CONF_MAX_VOLUME, default='100'): cv.string
})

class MultiRoomApi():
  def __init__(self, ip, port, session, hass):
    self.session = session
    self.hass = hass
    self.ip = ip
    self.port = port
    self.endpoint = 'http://{0}:{1}'.format(ip, port)

  async def _exec_cmd(self, cmd, key_to_extract):
    import xmltodict
    query = urllib.parse.urlencode({ "cmd": cmd }, quote_via=urllib.parse.quote)
    url = '{0}/UIC?{1}'.format(self.endpoint, query)

    with async_timeout.timeout(TIMEOUT, loop=self.hass.loop):
      _LOGGER.debug("Executing: {} with cmd: {}".format(url, cmd))
      response = await self.session.get(url)
      data = await response.text()
      _LOGGER.debug(data)
      response = xmltodict.parse(data)
      if key_to_extract in response['UIC']['response']:
        return response['UIC']['response'][key_to_extract]
      else:
        return None

  async def _exec_get(self, action, key_to_extract):
    return await self._exec_cmd('<name>{0}</name>'.format(action), key_to_extract)

  async def _exec_set(self, action, property_name, value):
    if type(value) is str:
      value_type = 'str'
    else:
      value_type = 'dec'
    cmd = '<name>{0}</name><p type="{3}" name="{1}" val="{2}"/>'.format(action, property_name, value, value_type)
    return await self._exec_cmd(cmd, property_name)

  async def get_main_info(self):
    return await self._exec_get('GetMainInfo')

  async def get_volume(self):
    return int(await self._exec_get('GetVolume', 'volume'))

  async def set_volume(self, volume):
    return await self._exec_set('SetVolume', 'volume', int(volume))

  async def get_speaker_name(self):
    return await self._exec_get('GetSpkName', 'spkname')

  async def get_muted(self):
    return await self._exec_get('GetMute', 'mute') == BOOL_ON

  async def set_muted(self, mute):
    if mute:
      return await self._exec_set('SetMute', 'mute', BOOL_ON)
    else:
      return await self._exec_set('SetMute', 'mute', BOOL_OFF)

  async def get_source(self):
    return await self._exec_get('GetFunc', 'function')

  async def set_source(self, source):
    return await self._exec_set('SetFunc', 'function', source)

class MultiRoomDevice(MediaPlayerDevice):
  def __init__(self, name, max_volume, api):
    _LOGGER.info('Initializing MultiRoomDevice')
    self._name = name
    self.api = api
    self._state = STATE_OFF
    self._current_source = None
    self._volume = 0
    self._muted = False
    self._max_volume = max_volume

  @property
  def supported_features(self):
    return SUPPORT_SAMSUNG_MULTI_ROOM

  @property
  def name(self):
    return self._name

  @property
  def state(self):
    return self._state

  @property
  def volume_level(self):
    return self._volume

  async def async_set_volume_level(self, volume):
    await self.api.set_volume(volume * self._max_volume)
    await self.async_update()

  @property
  def source(self):
    return self._current_source

  @property
  def source_list(self):
    return sorted(MULTI_ROOM_SOURCE_TYPE)

  async def async_select_source(self, source):
    await self.api.set_source(source)
    await self.async_update()

  @property
  def is_volume_muted(self):
    return self._muted

  async def async_mute_volume(self, mute):
    self._muted = mute
    await self.api.set_muted(self._muted)
    await self.async_update()

  @util.Throttle(MIN_TIME_BETWEEN_SCANS, MIN_TIME_BETWEEN_FORCED_SCANS)
  async def async_update(self):
    _LOGGER.info('Refreshing state...')
    self._current_source = await self.api.get_source()
    self._volume = await self.api.get_volume() / self._max_volume
    self._muted = await self.api.get_muted()
    if self._current_source:
      self._state = STATE_PLAYING
    else:
      self._state = STATE_OFF


def setup_platform(hass, config, add_devices, discovery_info=None):
  _LOGGER.error('Setup of the soundbar')
  ip = config.get(CONF_HOST)
  port = config.get(CONF_PORT)
  name = config.get(CONF_NAME)
  max_volume = int(config.get(CONF_MAX_VOLUME))
  session = async_get_clientsession(hass)
  api = MultiRoomApi(ip, port, session, hass)
  add_devices([MultiRoomDevice(name, max_volume, api)], True)
