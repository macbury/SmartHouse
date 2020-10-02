import appdaemon.plugins.hass.hassapi as hass
import datetime

class AdaptiveRoomHeating(hass.Hass):
  def initialize(self):
    self.listen_state(self.on_adaptation_callback, entity = self.args['outside_temperature'])
    self.listen_state(self.on_adaptation_callback, entity = self.args['family_devices'])
    self.listen_state(self.on_adaptation_callback, entity = self.args['calendar'])
    if 'main_light' in self.args:
      self.log('Has support for main light')
      self.listen_state(self.on_adaptation_callback, entity = self.args['main_light'])
    else:
      self.log('Dont have support for main light')
    self.adapt_temperature()

  def outside_temperature(self):
    return float(self.get_state(self.args['outside_temperature']))


  def anyone_in_home(self):
    return self.get_state(self.args['family_devices']) == 'home'

  def heating_time(self):
    if self.get_state(self.args['calendar']) == 'on':
      self.log("Calendar: {} is On".format(self.args['calendar']))
      return True
    else:
      self.log("Calendar: {} is Off".format(self.args['calendar']))
      return False

  def main_light_on(self):
    if 'main_light' in self.args:
      return self.get_state(self.args['main_light']) == 'on'
    else:
      return False

  def stop_heating(self):
    self.log("Lowering temperature")
    self.call_service('climate/turn_off', entity_id=self.args['climate'])

  def start_heating(self):
    self.log("Raising temperature")
    self.call_service('climate/turn_on', entity_id=self.args['climate'])

  def change_preset(self, preset):
    self.log("Change preset")
    self.call_service('climate/set_preset_mode', entity_id=self.args['climate'], preset=preset)

  def on_adaptation_callback(self, entity, attribute, old, new, kwargs):
    self.log("State callback triggered for {} from {} to {}. Adapting temperature".format(entity, old, new))
    self.adapt_temperature()

  def adapt_temperature(self):
    if self.main_light_on():
      self.log("Main light is on, increasing temperature")
      self.start_heating()
    elif self.outside_temperature() > 20:
      self.log("Outside temperature is {}, lowering temperature".format(self.outside_temperature()))
      self.stop_heating()
    elif self.anyone_in_home() and self.heating_time():
      self.log("Somebody is home, and still heating time is")
      self.start_heating()
    else self.anyone_in_home():
      self.log("Nobody home or night")
      self.stop_heating()
    if self.anyone_in_home():
      self.change_preset('none')
    else:
      self.change_preset('away')
