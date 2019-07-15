import ThermostatUI from './lib.js?v=10'

class ThermostatCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
  }
  set hass(hass) {
    const config = this._config;

    const ambient_temperature = parseFloat(hass.states[config.temperature].state);
    const target_temperature = parseFloat(hass.states[config.target_temperature].state);

    const options = {
      min_value: 4,
      max_value: 28,
      ambient_temperature,
      hvac_state: 'heat'
    }

    if (!this.thermostat.in_control || this._hass == null) {
      options.target_temperature = target_temperature;
    }

    this.thermostat.updateState(options);
    this._hass = hass;
  }

  _controlSetPoints() {
    const config = this._config;
    const options = {
      entity_id: config.target_temperature,
      value: parseFloat(this.thermostat.temperature.target)
    };

    this._hass.callService('input_number', 'set_value', options);
  }

  setConfig(config) {
    // // Check config
    // if (!config.entity && config.entity.split(".")[0] === 'climate') {
    //   throw new Error('Please define an entity');
    // }

    // Cleanup DOM
    const root = this.shadowRoot;
    if (root.lastChild) root.removeChild(root.lastChild);

    // Prepare config defaults
    const cardConfig = Object.assign({}, config);
    cardConfig.hvac = Object.assign({}, config.hvac);
    if (!cardConfig.diameter) cardConfig.diameter = 400;
    if (!cardConfig.pending) cardConfig.pending = 2;
    if (!cardConfig.idle_zone) cardConfig.idle_zone = 2;
    if (!cardConfig.step) cardConfig.step = 0.5;
    if (!cardConfig.highlight_tap) cardConfig.highlight_tap = true;
    if (!cardConfig.no_card) cardConfig.no_card = false;
    if (!cardConfig.chevron_size) cardConfig.chevron_size = 50;
    if (!cardConfig.num_ticks) cardConfig.num_ticks = 150;
    if (!cardConfig.tick_degrees) cardConfig.tick_degrees = 300;
    if (!cardConfig.hvac.states) cardConfig.hvac.states = { 'off': 'off', 'heat': 'heat', 'cool': 'cool', };

    // Extra config values generated for simplicity of updates
    cardConfig.radius = cardConfig.diameter / 2;
    cardConfig.ticks_outer_radius = cardConfig.diameter / 30;
    cardConfig.ticks_inner_radius = cardConfig.diameter / 8;
    cardConfig.offset_degrees = 180 - (360 - cardConfig.tick_degrees) / 2;
    cardConfig.control = this._controlSetPoints.bind(this);
    this.thermostat = new ThermostatUI(cardConfig);

    if (cardConfig.no_card === true) {
      root.appendChild(this.thermostat.container);
    }
    else {
      const card = document.createElement('div');
      card.style.padding = '5%';
      card.appendChild(this.thermostat.container);
      root.appendChild(card);
    }
    this._config = cardConfig;
  }
}
customElements.define('thermostat-card', ThermostatCard);
