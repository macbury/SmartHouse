import appdaemon.plugins.hass.hassapi as hass
import datetime

class AirPurifierAI(hass.Hass):
  def initialize(self):
    self.log("Started service...")
    self.fan_id = self.args['fan_id']
    self.update_handle = None
    self.log("Current fan: {}".format(self.fan_id))
    self.listen_state(self.on_adaptation_callback, entity = self.args['family_devices'])
    self.listen_state(self.on_adaptation_callback, entity = self.args['calendar'])

    if 'balcone_door' in self.args:
      self.listen_state(self.on_adaptation_callback, entity = self.args['balcone_door'])
    
    if 'alt_mode_entity' in self.args:
      self.log("Watching entity: {}".format(self.args['alt_mode_entity']))
      self.listen_state(self.on_adaptation_callback, entity = self.args['alt_mode_entity'])

    self.log("Finished configuration")
    self.adapt_air_purifier_mode()

  def alt_mode_entity_working(self):
    if 'alt_mode_entity' in self.args:
      return self.get_state(self.args['alt_mode_entity']) == 'on'
    else:
      return False

  def balcone_door_opened(self):
    if 'balcone_door' in self.args:
      return self.get_state(self.args['balcone_door']) == 'on'
    else:
      return False

  def anyone_in_home(self):
    state = self.get_state(self.args['family_devices'])
    self.log("State is {} for {}".format(state, self.args['family_devices']))
    return state == 'home'

  def cleaning_time(self):
    if self.get_state(self.args['calendar']) == 'on':
      self.log("Calendar: {} is On".format(self.args['calendar']))
      return True
    else:
      self.log("Calendar: {} is Off".format(self.args['calendar']))
      return False

  def update_speed(self, speed):
    self.log("Setting speed to: {}".format(speed))
    self.call_service('xiaomi_miio.fan_set_favorite_level', entity_id=self.fan_id, level=speed)
    self.call_service('fan/set_speed', entity_id=self.fan_id, speed='Auto')

  def turn_off(self):
    self.log("Turning off air purifier")
    self.call_service('fan/turn_off', entity_id=self.fan_id)

  def switch_to_mode(self):
    if self.alt_mode_entity_working():
      self.log("Switching to {} mode because {} is working".format(self.args['alt_mode'], self.args['alt_mode_entity']))
      self.call_service('fan/set_speed', entity_id=self.fan_id, speed=self.args['alt_mode'])
    else:
      self.log("Switching to {} mode".format(self.args['mode']))
      self.call_service('fan/set_speed', entity_id=self.fan_id, speed=self.args['mode'])

  def turn_on(self):
    self.log("Turning on air purifier")
    self.call_service('fan/turn_on', entity_id=self.fan_id)

  def on_adaptation_callback(self, entity, attribute, old, new, kwargs):
    self.log("State callback triggered for {} from {} to {}. Adapting air quality".format(entity, old, new))
    self.adapt_air_purifier_mode()
  
  def future_turn_on(self):
    self.log("Future Adapting speed!")
    self.turn_on()
    self.switch_to_mode()
    self.update_handle = None

  def adapt_air_purifier_mode(self):
    if self.anyone_in_home():
      self.log("People home")
      if self.balcone_door_opened():
        self.log("Balcone door is opened")
        self.turn_off()
      elif self.cleaning_time():
        if self.update_handle is not None:
          self.cancel_timer(self.update_handle)
        if 'alt_mode_entity' not in self.args:
          self.log("Will adapt now")
          self.future_turn_on()
        else:
          self.log("Will adapt now")
          self.future_turn_on()
      else:
        self.log("Turning off...")
        self.turn_off()
    else:
      self.log("Nobody home")
      self.log("Turn off completle")
      self.turn_off()
