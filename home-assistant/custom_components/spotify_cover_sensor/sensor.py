import urllib.request
import logging
import asyncio
import os
import json
import tempfile

from homeassistant.helpers.event import async_track_state_change
from homeassistant.helpers.entity import Entity
from homeassistant.components.spotify.media_player import (
  CONF_CACHE_PATH,
  CONF_CLIENT_ID,
  CONF_CLIENT_SECRET,
  DEFAULT_CACHE_PATH,
  SCOPE,
  AUTH_CALLBACK_PATH
)

from homeassistant.const import (
  STATE_PLAYING,
  STATE_OFF,
  STATE_ON
)

LOGGER       = logging.getLogger(__name__)

class SpotifyCoverSensor(Entity):
  def __init__(self, hass, config):
    self.hass = hass
    self.config = config
    self._state = STATE_OFF
    self._name  = 'spotify_cover'
    self._player = None
    self._oauth = None
    self.token_info = None
    self._dominant_color = None
    self._accent_color_1 = None
    self._accent_color_2 = None
    self._accent_color_3 = None
    self._load_token()
    self._listen_for_media_player_state_change()

  def _listen_for_media_player_state_change(self):
    media_players = self.hass.states.entity_ids('media_player')
    async_track_state_change(self.hass, media_players, self._on_player_state_change)

  @asyncio.coroutine
  def _on_player_state_change(self, entity_id, old_state, new_state):
    self.schedule_update_ha_state()

  @property
  def state(self):
    return self._state

  @property
  def name(self):
    return self._name

  @property
  def state_attributes(self):
    return {
      'dominant_rgb': self._dominant_color,
      'accent_rgb_1': self._accent_color_1,
      'accent_rgb_2': self._accent_color_2,
      'accent_rgb_3': self._accent_color_3
    }

  def update(self):
    LOGGER.info("Updating sensor information using spotify api")
    self._prepare_player()

    self._state = STATE_OFF

    if self._player is None:
      LOGGER.warning("Player is disabled")
      return

    if self._token_expired():
      LOGGER.warning("Spotify failed to update, token expired.")
      return 

    current = self._player.current_playback()
    if current is None:
      return

    if current.get('is_playing'):
      item = current.get('item')
      self._state = item.get('album').get('id')
      album_id = item.get('album').get('id')
      cover_url = item.get('album').get('images')[-2].get('url')
      
      self._state = STATE_ON

      colors = self._fetch_colors(album_id, cover_url)
      self._dominant_color = colors['dominant']
      self._accent_color_1 = colors['accent_1']
      self._accent_color_2 = colors['accent_2']
      self._accent_color_3 = colors['accent_3']

  def _fetch_cover(self, album_id, cover_url):
    cover_path = os.path.join(tempfile.gettempdir(), 'cover_'+album_id+'.png')
    if os.path.isfile(cover_path):
      return cover_path
    
    LOGGER.info('Downloading ' + cover_url + ' to ' + cover_path)
    urllib.request.urlretrieve(cover_url, cover_path)
    return cover_path

  def _format_color(self, color):
    return { 'r': color[0], 'g': color[1], 'b': color[2] }

  def _fetch_colors(self, album_id, cover_url):
    cover_path = self._fetch_cover(album_id, cover_url)
    cover_json = os.path.join(tempfile.gettempdir(), 'cover_'+album_id+'.json')

    # if os.path.isfile(cover_json) is False:
    #   from colorthief import ColorThief

    #   color_thief = ColorThief(cover_path)
    #   pallete = color_thief.get_palette(color_count=4, quality=1)
    #   colors = {
    #     'dominant': pallete[0],
    #     'accent_1': pallete[1],
    #     'accent_2': pallete[2],
    #     'accent_3': pallete[3]
    #   }
    #   file = open(cover_json, 'w')
    #   file.write(json.dumps(colors))
    #   file.close()

    return json.load(open(cover_json, 'r'))

  def _load_token(self):
    try:
      import spotipy.oauth2
      callback_url = '{}{}'.format(self.hass.config.api.base_url, AUTH_CALLBACK_PATH)
      cache = self.config.get(CONF_CACHE_PATH, self.hass.config.path(DEFAULT_CACHE_PATH))
      self.oauth = spotipy.oauth2.SpotifyOAuth(
            self.config.get(CONF_CLIENT_ID), self.config.get(CONF_CLIENT_SECRET),
            callback_url, scope=SCOPE,
            cache_path=cache)
      self.token_info = self.oauth.get_cached_token()
    except Exception as e:
      LOGGER.error("Could not refresh token")
      LOGGER.error(e)

  def _token_expired(self):
    return self.token_info is None or self.oauth.is_token_expired(self.token_info)

  def _prepare_player(self):
    if self._token_expired():
      self._load_token()
      self._player = None

    if self._token_expired():
      return None

    if self._player is None:
      import spotipy
      self._player = spotipy.Spotify(auth=self.token_info.get('access_token'))

def setup_platform(hass, config, add_devices, discovery_info=None):
  add_devices([SpotifyCoverSensor(hass, config)])
  return True
