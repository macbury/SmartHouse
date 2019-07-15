import appdaemon.plugins.hass.hassapi as hass

class Blinds(hass.Hass):
  def initialize(self):
    self.log("Started service...")
    self.listen_state(self.on_adaptation_callback, entity = self.args['family_group_entity_id'])
    self.listen_state(self.on_adaptation_callback, entity = self.args['calendar_entity_id'])
    self.listen_state(self.on_adaptation_callback, entity = self.args['luminance_entity_id'], duration = 3 * 60)
    self.run_at_sunrise(self.on_adaptation_callback)
    self.run_at_sunset(self.on_adaptation_callback)

  def anyone_in_home(self):
    family_group_entity_id = self.args['family_group_entity_id']
    state = self.get_state(family_group_entity_id)
    self.log("State is {} for {}".format(state, family_group_entity_id))
    return state == 'home'
  
  def is_in_control_time(self):
    return self.get_state(self.args['calendar_entity_id']) == 'on'

  def close_blinds(self):
    blinds_entity_id = self.args['blinds_entity_id']
    self.log("Closing blinds: {}".format(blinds_entity_id))
    self.call_service('cover/close_cover', entity_id=blinds_entity_id)

  def open_blinds(self):
    blinds_entity_id = self.args['blinds_entity_id']
    self.log("Opening blinds: {}".format(blinds_entity_id))

    if self.current_luminance() >= 2500:
      self.call_service('cover/set_cover_position', entity_id=blinds_entity_id, position=40)
    else:
      self.call_service('cover/open_cover', entity_id=blinds_entity_id)

  def on_adaptation_callback(self, kwargs):
    self.log("State callback triggered")
    self.update_blinds()

  def close_treshold(self):
    return float(self.args['close_treshold'])
  
  def current_luminance(self):
    return float(self.get_state(self.args['luminance_entity_id']))

  def update_blinds(self):
    if not self.anyone_in_home():
      self.log("Nobody home, closing blinds")
      self.close_blinds()
      return

    if self.sun_down():
      self.log("Sun is down!")
      self.close_blinds()
      return
    
    if self.is_in_control_time():
      if self.current_luminance() >= self.close_treshold():
        self.log("To bright: {} closing blinds".format(self.current_luminance()))
        self.close_blinds()
      else:
        self.log("It is ok: {} opening blinds".format(self.current_luminance()))
        self.open_blinds()
    else:
      self.log("Sun is up, but not in control time, ignore...")
      
    