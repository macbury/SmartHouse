import appdaemon.plugins.hass.hassapi as hass

def lerp(a, b, t):
  return round(a*(1.0 - t) + b*t)

class TemperatureLamp(hass.Hass):
  def initialize(self):
    self.log("Started!")

    self.light_id = self.args['light_id']
    self.temperature_id = self.args['outside_temperature_id']
    self.family_devices_id = self.args['family_devices']
    self.calendar_id = self.args['calendar_id']
    self.cold_temperature = self.args['cold_temperature']
    self.hot_temperature = self.args['hot_temperature']

    self.listen_state(self.on_adaptation_callback, entity = self.family_devices_id)
    self.listen_state(self.on_adaptation_callback, entity = self.temperature_id)
    self.listen_state(self.on_adaptation_callback, entity = self.calendar_id)
    self.adapt()

  def light_time(self):
    return self.get_state(self.calendar_id) == 'on'

  def on_adaptation_callback(self, entity, attribute, old, new, kwargs):
    self.log("State callback triggered for {} from {} to {}. ".format(entity, old, new))
    self.adapt()

  def current(self):
    return float(self.get_state(self.temperature_id))

  def anyone_in_home(self):
    state = self.get_state(self.family_devices_id)
    self.log("State is {} for {}".format(state, self.family_devices_id))
    return state == 'home'

  def rgb_color(self):
    c = [108, 181, 255]
    h = [255, 162, 71]
    progress = (self.current() - self.cold_temperature) / (self.hot_temperature - self.cold_temperature)
    progress = max([0.0, progress])
    progress = min([1.0, progress])
    self.log("Progress: {}".format(progress))

    return [lerp(c[0], h[0], progress), lerp(c[1], h[1], progress), lerp(c[2], h[2], progress)]

  def adapt(self):
    self.log("Starting adaptation")
    if self.anyone_in_home() and self.light_time():
       self.log("People in home, switching on lamp")
       self.call_service('light/turn_on', entity_id = self.light_id, brightness = 150, rgb_color = self.rgb_color())
    else:
      self.log("Nobody home, turning off humidifier")
      self.call_service('light/turn_off', entity_id = self.light_id)
