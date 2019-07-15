import appdaemon.plugins.hass.hassapi as hass
import datetime

class AdaptiveRoomHeating(hass.Hass):
  def initialize(self):
    self.listen_state(self.on_adaptation_callback, entity = self.args['comeback_input'])
    self.listen_state(self.on_adaptation_callback, entity = self.args['outside_temperature'])
    self.listen_state(self.on_adaptation_callback, entity = self.args['family_devices'])
    self.listen_state(self.on_adaptation_callback, entity = self.args['max_temperature'])
    self.listen_state(self.on_adaptation_callback, entity = self.args['min_temperature'])
    self.listen_state(self.on_adaptation_callback, entity = self.args['temperature_sensor'])
    self.listen_state(self.on_adaptation_callback, entity = self.args['calendar'])
    self.adapt_temperature()

  def outside_temperature(self):
    return float(self.get_state(self.args['outside_temperature']))

  def current_temperature(self):
    try:
      return float(self.get_state(self.args['temperature_sensor']))
    except Exception as e:
      return 20

  def anyone_in_home(self):
    return self.get_state(self.args['family_devices']) == 'home'

  def comeback(self):
    return self.get_state('input_boolean.comeback') == 'on'

  def heating_time(self):
    if self.get_state(self.args['calendar']) == 'on':
      self.log("Calendar: {} is On".format(self.args['calendar']))
      return True
    else:
      self.log("Calendar: {} is Off".format(self.args['calendar']))
      return False

  def max_temperature(self):
    return float(self.get_state(self.args['max_temperature']))

  def min_temperature(self):
    return float(self.get_state(self.args['min_temperature']))

  def lower_temperature(self):
    self.log("Lowering temperature")
    self.call_service('climate/set_temperature', entity_id=self.args['climate'], temperature=7.0)
  def raise_temperature(self):
    self.log("Raising temperature")
    self.call_service('climate/set_temperature', entity_id=self.args['climate'], temperature=28.0)

  def on_hour_callback(self, kwargs):
    self.log("Hour callback")
    self.adapt_temperature()

  def on_adaptation_callback(self, entity, attribute, old, new, kwargs):
    self.log("State callback triggered for {} from {} to {}. Adapting temperature".format(entity, old, new))
    self.adapt_temperature()

  def adapt_temperature(self):
    self.heating_time()
    self.log("Adapting temperature, Current temp is: {}, outside is: {}".format(self.current_temperature(), self.outside_temperature()))
    if self.outside_temperature() > 20:
      self.log("Outside temperature is {}, lowering temperature".format(self.outside_temperature()))
      self.lower_temperature()
    elif self.comeback():
      self.log("Somebody is coming back!")
      self.raise_temperature()
    elif self.current_temperature() >= self.max_temperature():
      self.log("It is too hot")
      self.lower_temperature()
    elif self.current_temperature() <= self.min_temperature():
      self.log("Its cold here")
      self.raise_temperature()
    elif self.anyone_in_home() and self.heating_time():
      self.log("Somebody is home, and still heating time is")
      self.raise_temperature()
    else:
      self.log("Nobody home or night")
      self.lower_temperature()
