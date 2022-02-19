"""Definition and setup of the Space Launch Live Sensors for Home Assistant."""

import datetime
import logging
import dateutil
import time

from homeassistant.util.dt import as_local, as_timestamp
from homeassistant.components.sensor import ENTITY_ID_FORMAT
from homeassistant.const import LENGTH_KILOMETERS, SPEED_KILOMETERS_PER_HOUR, ATTR_NAME
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)
from . import RocketLaunchLiveUpdater

from .const import ATTR_IDENTIFIERS, ATTR_MANUFACTURER, ATTR_MODEL, DOMAIN, COORDINATOR

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the sensor platforms."""

    coordinator = hass.data[DOMAIN][entry.entry_id][COORDINATOR]
    sensors = []
    sensor_count = 0

    for launch_id, launch in coordinator.data.items():
        sensor_count += 1
        sensors.append(
            RocketLaunchSensor(
                coordinator,
                sensor_count,
                launch_id,
                launch,
            )
        )

    async_add_entities(sensors)

class RocketLaunchSensor(CoordinatorEntity):
    """Defines a Rocket Launch Live launch sensor."""

    def __init__(
        self,
        coordinator: RocketLaunchLiveUpdater,
        sensor_count: int,
        launch_id: str,
        launch: dict,
    ):
        """Initialize entity."""

        super().__init__(coordinator=coordinator)

        self._name = f"Rocket Launch {sensor_count}"
        self._unique_id = f"rocket_launch_{sensor_count}"
        self._state = self.get_state(launch)
        self._icon = "mdi:rocket"
        self._launch_id = sensor_count -1
        self._attrs = self.get_attrs(launch)

    @property
    def unique_id(self):
        """Return the Home Assistant unique id."""
        return self._unique_id

    @property
    def name(self):
        """Return the name for Home Assistant."""
        return self._name

    @property
    def icon(self):
        """Return the assigned icon."""
        return self._icon

    @property
    def extra_state_attributes(self):
        """Return the device attributes."""
        attrs = self.get_attrs(self.coordinator.data[self._launch_id])
        return attrs

    @property
    def device_info(self):
        """Return the device info for entity registry."""
        return {
            ATTR_IDENTIFIERS: {(DOMAIN, "next_5_launches")},
            ATTR_NAME: "Rocket Launch Live",
            ATTR_MANUFACTURER: "rocketlaunch.live",
            ATTR_MODEL: "Next 5 Launches",
        }

    @property
    def state(self):
        """Return the current state of the sensor."""
        state = self.get_state(self.coordinator.data[self._launch_id])
        return state

    async def async_update(self):
        """Update the data coordinator."""
        await self.coordinator.async_request_refresh()

    async def async_added_to_hass(self):
        """Subscribe to updates."""
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )    

    def get_state(self, launch:dict):
        """Return a standardized string state."""

        return f"{launch['name']} ({launch['provider']['name']})"

    def get_attrs(self, launch:dict):
        """Return standardized attrs."""

        attrs = {}
        attrs["name"] = launch["name"]
        attrs["provider"] = launch["provider"]["name"]
        attrs["vehicle"] = launch["vehicle"]["name"]
        attrs["launch_pad"] = f"{launch['pad']['location']['name']} ({launch['pad']['name']})"
        attrs["launch_location"] = launch["pad"]["location"]["country"]

        missions = ""
        for mission in launch["missions"]:
            missions = f"{missions}{mission['name']} |"
        attrs["launch_missions"] = missions
        attrs["launch_description"] = launch["launch_description"]

        attrs["launch_media_link"] = ""

        for this_media in launch["media"]:
            if this_media.get("ldfeatured"):
                attrs["launch_media_link"] = f"https://www.youtube.com/watch?v={this_media.get('youtube_vidid')}"

        attrs["launch_24h_warning"] = "false"
        attrs["launch_20m_warning"] = "false"
        attrs["launch_target_timestamp"] = ""

        if launch.get("win_open"):
            launch_timestamp = as_timestamp(dateutil.parser.parse(launch["win_open"]))
            launch_target = as_local(dateutil.parser.parse(launch["win_open"]))
            attrs["launch_target"] = launch_target.strftime("%d-%b-%y %I:%M %p")
            attrs["launch_target_timestamp"] = int(launch_timestamp)

            if launch_timestamp < (time.time() + (24 * 60 * 60)) and launch_timestamp > time.time():
                attrs["launch_24h_warning"] = "true"

            if launch_timestamp < (time.time() + (20 * 60)) and launch_timestamp > time.time():
                attrs["launch_20m_warning"] = "true"
            
        else:
            attrs["launch_target"] = "NA"

        if launch["est_date"].get("year") and launch["est_date"].get("month") and launch["est_date"].get("day"):
            year = str(launch["est_date"]["year"])
            month = str(launch["est_date"]["month"])
            day = str(launch["est_date"]["day"])

            if len(month)==1:
                month = f"0{month}"

            if len(day)==1:
                day = f"0{day}"

            attrs["est_launch_date"] = datetime.datetime.fromisoformat(
                f"{year}-{month}-{day}"
            )
        else:
            attrs["est_launch_date"] = "NA"

        attrs["launch_date_target"] = launch["date_str"]

        tag_string = ""
        for tag in launch["tags"]:
            tag_string = f"{tag_string}{tag['text']} | "

        attrs["tags"] = tag_string[:255] if len(tag_string) > 255 else tag_string

        if launch.get("weather_summary"):
            attrs["weather_summary"] = launch["weather_summary"].replace("\n", ", ")
        else:
            attrs["weather_summary"] = "TBD"
        attrs["weather_temp"] = launch["weather_temp"]
        attrs["last_updated"] = launch["modified"]

        return attrs

