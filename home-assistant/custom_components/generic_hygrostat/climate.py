"""Adds support for generic hygrostat units."""
import asyncio
import logging

import voluptuous as vol

from homeassistant.const import TEMP_CELSIUS
from homeassistant.components.climate import PLATFORM_SCHEMA, ClimateEntity
from homeassistant.components.climate.const import (
    ATTR_HUMIDITY,
    CURRENT_HVAC_DRY,
    CURRENT_HVAC_FAN,
    CURRENT_HVAC_IDLE,
    CURRENT_HVAC_OFF,
    HVAC_MODE_DRY,
    HVAC_MODE_FAN_ONLY,
    HVAC_MODE_OFF,
    SUPPORT_TARGET_HUMIDITY,
)
from homeassistant.const import (
    ATTR_ENTITY_ID,
    CONF_NAME,
    EVENT_HOMEASSISTANT_START,
    SERVICE_TURN_OFF,
    SERVICE_TURN_ON,
    STATE_ON,
    STATE_UNKNOWN,
)
from homeassistant.core import DOMAIN as HA_DOMAIN, callback
from homeassistant.helpers import condition
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.event import (
    async_track_state_change,
    async_track_time_interval,
)
from homeassistant.helpers.restore_state import RestoreEntity

_LOGGER = logging.getLogger(__name__)

DEFAULT_TOLERANCE = 3
DEFAULT_NAME = "Generic Hygrostat"

CONF_DRYER = "dryer"
CONF_SENSOR = "target_sensor"
CONF_MIN_HUMIDITY = "min_humidity"
CONF_MAX_HUMIDITY = "max_humidity"
CONF_TARGET_HUMIDITY = "target_humidity"
CONF_MOIST_MODE = "moist_mode"
CONF_MIN_DUR = "min_cycle_duration"
CONF_DRY_TOLERANCE = "dry_tolerance"
CONF_MOIST_TOLERANCE = "moist_tolerance"
CONF_KEEP_ALIVE = "keep_alive"
CONF_INITIAL_HVAC_MODE = "initial_hvac_mode"
SUPPORT_FLAGS = SUPPORT_TARGET_HUMIDITY

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_DRYER): cv.entity_id,
        vol.Required(CONF_SENSOR): cv.entity_id,
        vol.Optional(CONF_MOIST_MODE): cv.boolean,
        vol.Optional(CONF_MAX_HUMIDITY): vol.Coerce(float),
        vol.Optional(CONF_MIN_DUR): vol.All(cv.time_period, cv.positive_timedelta),
        vol.Optional(CONF_MIN_HUMIDITY): vol.Coerce(float),
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Optional(CONF_DRY_TOLERANCE, default=DEFAULT_TOLERANCE): vol.Coerce(float),
        vol.Optional(CONF_MOIST_TOLERANCE, default=DEFAULT_TOLERANCE): vol.Coerce(float),
        vol.Optional(CONF_TARGET_HUMIDITY): vol.Coerce(float),
        vol.Optional(CONF_KEEP_ALIVE): vol.All(cv.time_period, cv.positive_timedelta),
        vol.Optional(CONF_INITIAL_HVAC_MODE): vol.In(
            [HVAC_MODE_DRY, HVAC_MODE_FAN_ONLY, HVAC_MODE_OFF]
        ),
    }
)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the generic hygrostat platform."""
    name = config.get(CONF_NAME)
    dryer_entity_id = config.get(CONF_DRYER)
    sensor_entity_id = config.get(CONF_SENSOR)
    min_humidity = config.get(CONF_MIN_HUMIDITY)
    max_humidity = config.get(CONF_MAX_HUMIDITY)
    target_humidity = config.get(CONF_TARGET_HUMIDITY)
    moist_mode = config.get(CONF_MOIST_MODE)
    min_cycle_duration = config.get(CONF_MIN_DUR)
    dry_tolerance = config.get(CONF_DRY_TOLERANCE)
    moist_tolerance = config.get(CONF_MOIST_TOLERANCE)
    keep_alive = config.get(CONF_KEEP_ALIVE)
    initial_hvac_mode = config.get(CONF_INITIAL_HVAC_MODE)

    async_add_entities(
        [
            GenericHygrostat(
                name,
                dryer_entity_id,
                sensor_entity_id,
                min_humidity,
                max_humidity,
                target_humidity,
                moist_mode,
                min_cycle_duration,
                dry_tolerance,
                moist_tolerance,
                keep_alive,
                initial_hvac_mode,
            )
        ]
    )


class GenericHygrostat(ClimateEntity, RestoreEntity):
    """Representation of a Generic Hygrostat device."""

    def __init__(
        self,
        name,
        dryer_entity_id,
        sensor_entity_id,
        min_humidity,
        max_humidity,
        target_humidity,
        moist_mode,
        min_cycle_duration,
        dry_tolerance,
        moist_tolerance,
        keep_alive,
        initial_hvac_mode,
    ):
        """Initialize the hygrostat."""
        self._name = name
        self.dryer_entity_id = dryer_entity_id
        self.sensor_entity_id = sensor_entity_id
        self.moist_mode = moist_mode
        self.min_cycle_duration = min_cycle_duration
        self._dry_tolerance = dry_tolerance
        self._moist_tolerance = moist_tolerance
        self._keep_alive = keep_alive
        self._hvac_mode = initial_hvac_mode
        self._saved_target_humidity = target_humidity
        self._hvac_list = [HVAC_MODE_DRY, HVAC_MODE_FAN_ONLY, HVAC_MODE_OFF]
        self._active = False
        self._cur_humidity = None
        self._humidity_lock = asyncio.Lock()
        self._min_humidity = min_humidity
        self._max_humidity = max_humidity
        self._target_humidity = target_humidity
        self._support_flags = SUPPORT_FLAGS

    async def async_added_to_hass(self):
        """Run when entity about to be added."""
        await super().async_added_to_hass()

        # Add listener
        async_track_state_change(
            self.hass, self.sensor_entity_id, self._async_sensor_changed
        )
        async_track_state_change(
            self.hass, self.dryer_entity_id, self._async_switch_changed
        )

        if self._keep_alive:
            async_track_time_interval(
                self.hass, self._async_control_humidification, self._keep_alive
            )

        @callback
        def _async_startup(event):
            """Init on startup."""
            sensor_state = self.hass.states.get(self.sensor_entity_id)
            if sensor_state and sensor_state.state != STATE_UNKNOWN:
                self._async_update_humidity(sensor_state)

        self.hass.bus.async_listen_once(EVENT_HOMEASSISTANT_START, _async_startup)

        # Check If we have an old state
        old_state = await self.async_get_last_state()
        if old_state is not None:
            # If we have no initial humidity, restore
            if self._target_humidity is None:
                # If we have a previously saved humidity
                if old_state.attributes.get(ATTR_HUMIDITY) is None:
                    if self.moist_mode:
                        self._target_humidity = self.min_humidity
                    else:
                        self._target_humidity = self.max_humidity
                    _LOGGER.warning(
                        "Undefined target humidity, falling back to %s",
                        self._target_humidity,
                    )
                else:
                    self._target_humidity = float(old_state.attributes[ATTR_HUMIDITY])
            if not self._hvac_mode and old_state.state:
                self._hvac_mode = old_state.state

        else:
            # No previous state, try and restore defaults
            if self._target_humidity is None:
                if self.moist_mode:
                    self._target_humidity = self.min_humidity
                else:
                    self._target_humidity = self.max_humidity
            _LOGGER.warning(
                "No previously saved humidity, setting to %s", self._target_humidity
            )

        # Set default state to off
        if not self._hvac_mode:
            self._hvac_mode = HVAC_MODE_OFF

    @property
    def should_poll(self):
        """Return the polling state."""
        return False

    @property
    def name(self):
        """Return the name of the hygrostat."""
        return self._name

    @property
    def temperature_unit(self):
        """Return the unit of measurement."""
        return TEMP_CELSIUS

    @property
    def current_humidity(self):
        """Return the sensor humidity."""
        return self._cur_humidity

    @property
    def hvac_mode(self):
        """Return current operation."""
        return self._hvac_mode

    @property
    def hvac_action(self):
        """Return the current running hvac operation if supported.

        Need to be one of CURRENT_HVAC_*.
        """
        if self._hvac_mode == HVAC_MODE_FAN_ONLY:
            return CURRENT_HVAC_FAN
        if self._hvac_mode == HVAC_MODE_OFF:
            return CURRENT_HVAC_OFF
        if not self._is_device_active:
            return CURRENT_HVAC_IDLE
        return CURRENT_HVAC_DRY

    @property
    def target_humidity(self):
        """Return the humidity we try to reach."""
        return self._target_humidity

    @property
    def hvac_modes(self):
        """List of available operation modes."""
        return self._hvac_list

    async def async_set_hvac_mode(self, hvac_mode):
        """Set hvac mode."""
        if hvac_mode == HVAC_MODE_DRY:
            self._hvac_mode = HVAC_MODE_DRY
            await self._async_control_humidification(force=True)
        elif hvac_mode == HVAC_MODE_FAN_ONLY:
            self._hvac_mode = HVAC_MODE_FAN_ONLY
            await self._async_dryer_turn_on()
        elif hvac_mode == HVAC_MODE_OFF:
            self._hvac_mode = HVAC_MODE_OFF
            if self._is_device_active:
                await self._async_dryer_turn_off()
        else:
            _LOGGER.error("Unrecognized hvac mode: %s", hvac_mode)
            return
        # Ensure we update the current operation after changing the mode
        self.schedule_update_ha_state()

    async def async_set_humidity(self, humidity):
        """Set new target humidity."""
        if humidity is None:
            return
        self._target_humidity = humidity
        await self._async_control_humidification(force=True)
        await self.async_update_ha_state()

    @property
    def min_humidity(self):
        """Return the minimum humidity."""
        if self._min_humidity:
            return self._min_humidity

        # get default humidity from super class
        return super().min_humidity

    @property
    def max_humidity(self):
        """Return the maximum humidity."""
        if self._max_humidity:
            return self._max_humidity

        # Get default humidity from super class
        return super().max_humidity

    async def _async_sensor_changed(self, entity_id, old_state, new_state):
        """Handle humidity changes."""
        if new_state is None:
            return

        self._async_update_humidity(new_state)
        await self._async_control_humidification()
        await self.async_update_ha_state()

    @callback
    def _async_switch_changed(self, entity_id, old_state, new_state):
        """Handle dryer switch state changes."""
        if new_state is None:
            return
        self.async_schedule_update_ha_state()

    @callback
    def _async_update_humidity(self, state):
        """Update hygrostat with latest state from sensor."""
        try:
            self._cur_humidity = float(state.state)
        except ValueError as ex:
            _LOGGER.error("Unable to update from sensor: %s", ex)

    async def _async_control_humidification(self, time=None, force=False):
        """Check if we need to turn humidification on or off."""
        async with self._humidity_lock:
            if not self._active and None not in (self._cur_humidity, self._target_humidity):
                self._active = True
                _LOGGER.info(
                    "Obtained current and target humidity. "
                    "Generic hygrostat active. %s, %s",
                    self._cur_humidity,
                    self._target_humidity,
                )

            if not self._active or self._hvac_mode == HVAC_MODE_FAN_ONLY or self._hvac_mode == HVAC_MODE_OFF:
                return

            if not force and time is None:
                # If the `force` argument is True, we
                # ignore `min_cycle_duration`.
                # If the `time` argument is not none, we were invoked for
                # keep-alive purposes, and `min_cycle_duration` is irrelevant.
                if self.min_cycle_duration:
                    if self._is_device_active:
                        current_state = STATE_ON
                    else:
                        current_state = HVAC_MODE_OFF
                    long_enough = condition.state(
                        self.hass,
                        self.dryer_entity_id,
                        current_state,
                        self.min_cycle_duration,
                    )
                    if not long_enough:
                        return

            too_dry = self._target_humidity >= self._cur_humidity + self._dry_tolerance
            too_moist = self._cur_humidity >= self._target_humidity + self._moist_tolerance
            if self._is_device_active:
                if (self.moist_mode and too_moist) or (not self.moist_mode and too_dry):
                    _LOGGER.info("Turning off dryer %s", self.dryer_entity_id)
                    await self._async_dryer_turn_off()
                elif time is not None:
                    # The time argument is passed only in keep-alive case
                    _LOGGER.info(
                        "Keep-alive - Turning on dryer %s",
                        self.dryer_entity_id,
                    )
                    await self._async_dryer_turn_on()
            else:
                if (self.moist_mode and too_dry) or (not self.moist_mode and too_moist):
                    _LOGGER.info("Turning on dryer %s", self.dryer_entity_id)
                    await self._async_dryer_turn_on()
                elif time is not None:
                    # The time argument is passed only in keep-alive case
                    _LOGGER.info(
                        "Keep-alive - Turning off dryer %s", self.dryer_entity_id
                    )
                    await self._async_dryer_turn_off()

    @property
    def _is_device_active(self):
        """If the toggleable device is currently active."""
        return self.hass.states.is_state(self.dryer_entity_id, STATE_ON)

    @property
    def supported_features(self):
        """Return the list of supported features."""
        return self._support_flags

    async def _async_dryer_turn_on(self):
        """Turn dryer toggleable device on."""
        data = {ATTR_ENTITY_ID: self.dryer_entity_id}
        await self.hass.services.async_call(HA_DOMAIN, SERVICE_TURN_ON, data)

    async def _async_dryer_turn_off(self):
        """Turn dryer toggleable device off."""
        data = {ATTR_ENTITY_ID: self.dryer_entity_id}
        await self.hass.services.async_call(HA_DOMAIN, SERVICE_TURN_OFF, data)
