import appdaemon.plugins.hass.hassapi as hass
import datetime

# Check if all devices are charged
class BatteryWatcher(hass.Hass):
  def initialize(self):
    self.log("Working!")
    time = datetime.time(18, 0, 0)
    self.run_daily(self.check_batteries, time)
    
  def check_batteries(self, kwargs):
    treshold = int(self.args["threshold"])
    self.log("Checking batteries level. Min threshold is: {}".format(treshold))
    devices = self.get_state()
    values = {}
    low = []
    for device in devices:
      battery = None
      device_state = devices[device]
      if "attributes" in device_state:
        if "battery" in device_state["attributes"]:
          battery = device_state["attributes"]["battery"]
        if "battery_level" in device_state["attributes"]:
          battery = device_state["attributes"]["battery_level"]
        if battery != None:
          if int(battery) < treshold:
            self.log("Device: {} has low battery level: {}".format(device, battery))
            low.append({ 'device': device, 'battery': battery })

    message = "Bettery Level Report\n\n"
    if low:
      message += "The following devices are low: (< {}) ".format(self.args["threshold"])
      for device in low:
        message = "Device {} has {} % battery left".format(device['device'], int(device['battery']))
      message += "\n\n"
      
    if low:
      self.log("Oh no! Battery is low for: "+message)
      self.call_service('notify/all', title="Home Assistant Battery Report", message=message)