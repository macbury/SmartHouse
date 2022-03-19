import appdaemon.plugins.hass.hassapi as hass
import datetime

class AdaptiveRoomHeating(hass.Hass):
  def initialize(self):
    self.listen_state(self.on_adaptation_callback, entity_id = self.args['outside_temperature'])
    self.listen_state(self.on_adaptation_callback, entity_id = self.args['family_devices'])
    self.listen_state(self.on_adaptation_callback, entity_id = self.args['calendar'])
    if 'main_light' in self.args:
      self.log('Has support for main light')
      self.listen_state(self.on_adaptation_callback, entity_id = self.args['main_light'])
    else:
      self.log('Dont have support for main light')

    if 'window_door' in self.args:
      self.log('Has support for window or door')
      self.listen_state(self.on_adaptation_callback, entity_id = self.args['window_door'])
    else:
      self.log('Dont have support for main light')
    self.adapt_temperature()

  def outside_temperature(self):
    return float(self.get_state(self.args['outside_temperature']))

  def anyone_in_home(self):
    return self.get_state(self.args['family_devices']) == 'home'

  def window_opened(self):
    if 'window_door' in self.args:
      return self.get_state(self.args['window_door']) == 'on'
    else:
      return False

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
    self.log("Change preset to: {}".format(preset))
    self.call_service('climate/set_preset_mode', entity_id=self.args['climate'], preset_mode=preset)

  def on_adaptation_callback(self, entity, attribute, old, new, kwargs):
    self.log("State callback triggered for {} from {} to {}. Adapting temperature".format(entity, old, new))
    self.adapt_temperature()

  def adapt_temperature(self):
    if self.window_opened():
      self.log("Window is opened, stopping heating")
      self.stop_heating()
    elif self.main_light_on():
      self.log("light is on, start heating")
      self.start_heating()
    elif self.anyone_in_home() and self.heating_time():
      self.log("Family in home, and heating time")
      self.start_heating()
    else:
      self.log("Stopping heating")
      self.stop_heating()
