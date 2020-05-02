import appdaemon.plugins.hass.hassapi as hass

class HumidifierController(hass.Hass):
  def initialize(self):
    self.log("Started!")

    self.humidifer_id = self.args['humidifer']
    self.max_humidity = self.args['max_humidity']
    self.min_humidity = self.args['min_humidity']

    self.listen_state(self.on_adaptation_callback, entity = self.args['family_devices'])
    self.listen_state(self.on_adaptation_callback, entity = self.args['calendar'])
    self.listen_state(self.on_adaptation_callback, entity = self.args['humidity_sensor'])
    if 'balcone_door' in self.args:
      self.listen_state(self.on_adaptation_callback, entity = self.args['balcone_door'])
    
    self.adapt()

  def on_adaptation_callback(self, entity, attribute, old, new, kwargs):
    self.log("State callback triggered for {} from {} to {}. Adapting humdity".format(entity, old, new))
    self.adapt()

  def balcone_door_opened(self):
    if 'balcone_door' in self.args:
      return self.get_state(self.args['balcone_door']) == 'on'
    else:
      return False

  def current(self):
    return float(self.get_state(self.args['humidity_sensor']))

  def anyone_in_home(self):
    state = self.get_state(self.args['family_devices'])
    self.log("State is {} for {}".format(state, self.args['family_devices']))
    return state == 'home'

  def work_time(self):
    if self.get_state(self.args['calendar']) == 'on':
      self.log("Calendar: {} is On".format(self.args['calendar']))
      return True
    else:
      self.log("Calendar: {} is Off".format(self.args['calendar']))
      return False

  def turn_off(self):
    self.log("Turning off humidifier")
    self.call_service('switch/turn_off', entity_id=self.humidifer_id)

  def turn_on(self):
    self.log("Turning on humidifier")
    self.call_service('switch/turn_on', entity_id=self.humidifer_id)

  def adapt(self):
    self.log("Starting adaptation")
    if self.balcone_door_opened():
      self.log("Balcone door opened, no sense to run humidify whole city")
      self.turn_off()
    elif self.anyone_in_home() and self.work_time():
      if self.current() <= self.min_humidity:
        self.log("Humidity {} is below {}".format(self.current(), self.min_humidity))
        self.turn_on()
      elif self.current() >= self.max_humidity:
        self.log("Humidity {} is above {}".format(self.current(), self.max_humidity))
        self.turn_off()
      else:
        self.turn_on()
        self.log("Humidity is {} and min is {} and max is {}".format(self.current(), self.min_humidity, self.max_humidity))
    else:
      self.log("Nobody home, turning off humidifier")
      self.turn_off()
