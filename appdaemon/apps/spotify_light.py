import appdaemon.plugins.hass.hassapi as hass
import json
SPOTIFY_SENSOR_ENTITY_ID = 'sensor.spotify_cover'
MAIN_LIGHT_ENTITY = 'group.living_room_main_light'
AMBIENT_LIGHT = 'group.living_room_ambient_light'
SPOTIFY_SOURCE = '[AV] Samsung Soundbar K650'

class SpotifyLight(hass.Hass):

  def initialize(self):
    self.listen_state(self.update_lighting_callback, entity = SPOTIFY_SENSOR_ENTITY_ID)
    self.listen_state(self.update_lighting_callback, entity = MAIN_LIGHT_ENTITY)
    self.listen_state(self.update_lighting_callback, entity = AMBIENT_LIGHT)
    self.update()

  def update_lighting_callback(self, entity, attribute, old, new, kwargs):
    self.log("State callback triggered for {} from {} to {}.".format(entity, old, new))
    if (entity == SPOTIFY_SENSOR_ENTITY_ID and new == 'on') or (entity == MAIN_LIGHT_ENTITY and new == 'off') or (entity == AMBIENT_LIGHT):
      self.update()

  def update(self):
    if self.get_state(SPOTIFY_SENSOR_ENTITY_ID) == 'off':
      self.log("Spotify sensor is disabled... ignoring change of lighting")
      return

    if self.get_state(MAIN_LIGHT_ENTITY) == 'on':
      self.log("Main light are on, ignoreing change of lighing")
      return

    if self.get_state(AMBIENT_LIGHT) == 'off':
      self.log('Ambient Light turned off, so ignore...')
      return

    if self.get_state('media_player.spotify', attribute='source') != SPOTIFY_SOURCE:
      self.log("Spotify source is not soundbar!, ignoring change of lighting")
      return

    self.log("Accent color is: {}".format(self.accent_color()))
    self.log("Dominant color is: {}".format(self.dominant_color()))

    self.set_light('light.living_room_sofa', self.dominant_color())
    #self.set_light('group.living_room_accent_ambient_light', self.accent_color())
    self.publish_color('home/living_room/led_strip/desk/set', self.dominant_color(), 173)
    self.publish_color('home/living_room/led_strip/lamp/set', self.accent_color(), 254)
    self.publish_color('home/living_room/led_strip/tv/set', self.dominant_color(), 254)

  def dominant_color(self):
    return self.get_state(SPOTIFY_SENSOR_ENTITY_ID, attribute = 'dominant_rgb') or [255, 255, 255]

  def accent_color(self):
    return self.get_state(SPOTIFY_SENSOR_ENTITY_ID, attribute =  'accent_rgb_1') or [255, 255, 255]

  def publish_color(self, topic, color, brightness):
    self.log("Sending to {}".format(topic))
    self.call_service('mqtt/publish', topic=topic, payload=json.dumps({ 'state': 'ON', 'brightness': brightness }), qos=2)
    self.call_service('mqtt/publish', topic=topic, payload=json.dumps({ 'state': 'ON', 'effect': 'SingleColor' }), qos=2)
    self.call_service('mqtt/publish', topic=topic, payload=json.dumps({ 'state': 'ON', 'color': { 'r': color[0], 'g': color[1], 'b': color[2] } }), qos=2)


  def set_light(self, entity_id, color):
    self.turn_on(entity_id, brightness=193, rgb_color=color)
