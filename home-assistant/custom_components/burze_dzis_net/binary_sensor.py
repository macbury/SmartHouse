from datetime import timedelta
import voluptuous as vol
import logging

from homeassistant.util import Throttle
from homeassistant.util.dt import parse_datetime
from homeassistant.components.binary_sensor import DEVICE_CLASS_SAFETY, PLATFORM_SCHEMA, ENTITY_ID_FORMAT
from homeassistant.const import CONF_NAME, CONF_RADIUS, CONF_API_KEY, ATTR_ATTRIBUTION, CONF_LATITUDE, CONF_LONGITUDE, \
    CONF_SCAN_INTERVAL
import homeassistant.helpers.config_validation as cv
try:
    from homeassistant.components.binary_sensor import BinarySensorEntity
except ImportError:
    from homeassistant.components.binary_sensor import BinarySensorDevice as BinarySensorEntity
from homeassistant.helpers.entity import async_generate_entity_id

_LOGGER = logging.getLogger(__name__)

CONF_WARNINGS = 'warnings'
CONF_STORMS_NEARBY = 'storms_nearby'

DEFAULT_NAME = 'Burze.dzis.net'
DEFAULT_SCAN_INTERVAL = timedelta(minutes=2, seconds=30)
ATTRIBUTION = 'Information provided by Burze.dzis.net.'

WARNING_TYPES = {
    'frost_warning': ['mroz', 'Ostrzeżenie - Mróz', 'mdi:weather-snowy'],
    'heat_warning': ['upal', 'Ostrzeżenie - Upał', 'mdi:weather-sunny'],
    'wind_warning': ['wiatr', 'Ostrzeżenie - Wiatr', 'mdi:weather-windy'],
    'precipitation_warning': ['opad', 'Ostrzeżenie - Opad', 'mdi:weather-pouring'],
    'storm_warning': ['burza', 'Ostrzeżenie - Burza', 'mdi:weather-lightning-rainy'],
    'tornado_warning': ['traba', 'Ostrzeżenie - Trąba', 'mdi:weather-hurricane'],
}
WARNING_DESCRIPTIONS = {
    'frost_warning': {
        1: "od -20 do -25°C",
        2: "od -26 do -30°C",
        3: "poniżej -30°C"
    },
    'heat_warning': {
        1: "od 30 do 34°C",
        2: "od 35 do 38°C",
        3: "powyżej 38°C"
    },
    'wind_warning': {
        1: "w porywach od 70 do 90 km/h",
        2: "w porywach od 91 do 110 km/h",
        3: "w porywach powyżej 110 km/h"
    },
    'precipitation_warning': {
        1: "deszcz od 25 do 40 mm w ciągu 24 godzin/śnieg od 10 do 15 cm w ciągu 24 godzin",
        2: "deszcz od 41 do 70 mm w ciągu 24 godzin/śnieg od 16 do 30 cm w ciągu 24 godzin/śnieg od 10 do 15 cm w ciągu 12 godzin",
        3: "deszcz powyżej 70 mm w ciągu 24 godzin/śnieg powyżej 30 cm w ciągu 24 godzin/śnieg powyżej 15 cm w ciągu 12 godzin"
    },
    'storm_warning': {
        1: "deszcz od 15 do 40 mm/wiatr w porywach od 60 do 90 km/h/grad poniżej 2 cm",
        2: "deszcz od 41 do 70 mm/wiatr w porywach od 91 do 110 km/h/grad od 2 do 5 cm",
        3: "wiatr w porywach od 91 do 110 km/h/grad od 2 do 5 cm/deszcz powyżej 70 mm/wiatr w porywach powyżej 110 km/h/grad powyżej 5 cm"
    },
    'tornado_warning': {
        1: "ryzyko niewielkie",
        2: "ryzyko umiarkowane",
        3: "ryzyko wysokie"
    }
}
STORM_NEARBY = ['Burze w pobliżu', 'mdi:weather-lightning']

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_LATITUDE): cv.string,
    vol.Optional(CONF_LONGITUDE): cv.string,
    vol.Required(CONF_API_KEY): cv.string,
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Optional(CONF_WARNINGS, default=[]):
        vol.All(cv.ensure_list, [vol.In(WARNING_TYPES)]),
    vol.Optional(CONF_STORMS_NEARBY):
        vol.Schema({
            vol.Required(CONF_RADIUS): cv.positive_int
        }),
    vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): cv.time_period
})


def convert_to_dm(dmf):
    return '{}.{:02}'.format(int(dmf), round(dmf % 1 * 60))


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    name = config.get(CONF_NAME)
    latitude = float(config.get(CONF_LATITUDE, hass.config.latitude))
    longitude = float(config.get(CONF_LONGITUDE, hass.config.longitude))
    api_key = config.get(CONF_API_KEY)
    warnings = config.get(CONF_WARNINGS)
    storms_nearby = config.get(CONF_STORMS_NEARBY)
    scan_interval = config.get(CONF_SCAN_INTERVAL)
    radius = 0
    if storms_nearby is not None:
        radius = storms_nearby.get(CONF_RADIUS)
    sensors = []
    sensor_name = '{} - '.format(name)
    x = convert_to_dm(longitude)
    y = convert_to_dm(latitude)
    updater = BurzeDzisNetDataUpdater(hass, x, y, radius, api_key, scan_interval)
    await updater.async_update()
    for warning_type in warnings:
        uid = '{}_{}'.format(name, warning_type)
        entity_id = async_generate_entity_id(ENTITY_ID_FORMAT, uid, hass=hass)
        sensors.append(BurzeDzisNetWarningsSensor(entity_id, sensor_name, updater, warning_type))
    if storms_nearby is not None:
        uid = '{}_storms_nearby'.format(name)
        entity_id = async_generate_entity_id(ENTITY_ID_FORMAT, uid, hass=hass)
        sensors.append(BurzeDzisNetStormsNearbySensor(entity_id, sensor_name, updater))
    async_add_entities(sensors, True)


class BurzeDzisNetSensor(BinarySensorEntity):

    def __init__(self, entity_id, name, updater):
        self.entity_id = entity_id
        self._name = name
        self._updater = updater
        self._data = None

    @property
    def extra_state_attributes(self):
        output = dict()
        output[ATTR_ATTRIBUTION] = ATTRIBUTION
        return output

    @property
    def device_class(self):
        return DEVICE_CLASS_SAFETY

    async def async_update(self):
        await self._updater.async_update()


class BurzeDzisNetWarningsSensor(BurzeDzisNetSensor):
    def __init__(self, entity_id, name, updater, warning_type):
        super().__init__(entity_id, name, updater)
        self._warning_type = warning_type
        self._warning_key = WARNING_TYPES[self._warning_type][0]

    @property
    def is_on(self):
        data = self._updater.ostrzezenia_pogodowe_output
        return data is not None and data[self._warning_key] > 0

    @property
    def extra_state_attributes(self):
        output = super().extra_state_attributes
        if self.is_on:
            data = self._updater.ostrzezenia_pogodowe_output
            output['level'] = data[self._warning_key]
            output['description'] = WARNING_DESCRIPTIONS[self._warning_type][data[self._warning_key]]
            output['from'] = str(parse_datetime(data[self._warning_key + '_od_dnia'] + 'Z'))
            output['to'] = str(parse_datetime(data[self._warning_key + '_do_dnia'] + 'Z'))
        return output

    @property
    def icon(self):
        return WARNING_TYPES[self._warning_type][2]

    @property
    def name(self):
        return self._name + WARNING_TYPES[self._warning_type][1]


class BurzeDzisNetStormsNearbySensor(BurzeDzisNetSensor):
    def __init__(self, entity_id, name, updater):
        super().__init__(entity_id, name, updater)

    @property
    def is_on(self):
        data = self._updater.szukaj_burzy_output
        return data is not None and data['liczba'] > 0

    @property
    def extra_state_attributes(self):
        output = super().extra_state_attributes
        if self.is_on:
            data = self._updater.szukaj_burzy_output
            output['number'] = data['liczba']
            output['distance'] = data['odleglosc']
            output['direction'] = data['kierunek']
            output['period'] = data['okres']
        return output

    @property
    def name(self):
        return self._name + STORM_NEARBY[0]

    @property
    def icon(self):
        return STORM_NEARBY[1]


class BurzeDzisNetDataUpdater:
    def __init__(self, hass, x, y, radius, api_key, scan_interval):
        self._hass = hass
        self._x = x
        self._y = y
        self._radius = radius
        self._api_key = api_key
        self.szukaj_burzy_output = None
        self.ostrzezenia_pogodowe_output = None
        self.async_update = Throttle(scan_interval)(self._async_update)

    async def _async_update(self):
        await self._hass.async_add_executor_job(self._update_data)

    def _update_data(self):
        from zeep import Client
        from zeep.exceptions import Fault
        service = Client('https://burze.dzis.net/soap.php?WSDL').service
        try:
            self.ostrzezenia_pogodowe_output = service.ostrzezenia_pogodowe(self._y, self._x, self._api_key)
            self.szukaj_burzy_output = service.szukaj_burzy(self._y, self._x, self._radius, self._api_key)
        except Fault as fault:
            _LOGGER.error('Error setting up burze_dzis_net: {}', fault)
