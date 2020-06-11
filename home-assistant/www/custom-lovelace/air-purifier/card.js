import { LitElement, html } from 'https://unpkg.com/@polymer/lit-element@0.6.5/lit-element.js?module';

const styles = html`
  <style>
    :host {
      display: flex;
      flex: 1;
      flex-direction: column;
    }
    ha-card {
      background-color: #36455f;
      // background: #36435d;
      flex-direction: column;
      flex: 1;
      position: relative;
      padding: 0px;
      border-radius: 4px;
      overflow: hidden;
    }

    .preview {
      background: transparent no-repeat center url('/local/custom-lovelace/air-purifier/working.gif');
      height: 220px;
      background-size: 280px 280px;
      display: flex;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
    }

    .preview.idle {
      background-image: url('/local/custom-lovelace/air-purifier/standby.gif');
      background-size: 280px 280px;
    }

    .current-aqi {
      font-size: 48px;
      font-weight: bold;
      align-self: center;
      line-height: 48px;
      padding: 5px 10px;
      border-radius: 2px;
      background: rgba(0, 0, 0, 0.6);
    }

    .current-aqi sup {
      font-size: 16px;
      line-height: 16px;
      font-weight: normal;
    }

    .number-off {
      opacity: 0.2;
    }

    .toolbar {
      background: #fff;
      min-height: 30px;
      display: flex;
      flex-direction: row;
      justify-content: space-evenly;
      padding: 0px;
    }

    .stats {
      border-top: 1px solid rgba(255, 255, 255, 0.2);
      display: flex;
      flex-direction: row;
      justify-content: space-evenly;
    }

    .stats-block {
      margin: 10px 0px;
      text-align: center;
      border-right: 1px solid rgba(255, 255, 255, 0.2);
      flex-grow: 1;
    }

    .stats-block:last-child {
      border: 0px;
    }

    .stats-hours {
      font-size: 20px;
      font-weight: bold;
    }

    .toolbar ha-icon-button {
      color: #319ef9;
      flex-direction: column;
      width: 44px;
      height: 54px;
      padding-right: 10px;
    }

    .toolbar ha-icon-button:active {
      opacity: 0.4;
      background: rgba(0, 0, 0, 0.1);
    }

    .toolbar ha-icon-button:last-child {
      margin-right: 0px;
    }

    .toolbar ha-button {
      color: #319ef9;
      flex-direction: row;
    }

    .toolbar ha-icon {
      color: #319ef9;
      padding-right: 15px;
    }

    .toolbar-split {
      padding-right: 15px;
    }

    .toolbar-item {
      opacity: 0.5;
    }

    .toolbar-item-on {
      opacity: 1.0;
    }
  </style>
`

class AirPurifierCard extends LitElement {
  static get properties() {
    return {
      hass: Object,
      config: Object,
    }
  }

  get entity() {
    return this.hass.states[this.config.entity]
  }

  handleMore() {
    const e = new Event('hass-more-info', { bubbles: true, composed: true })
    e.detail = { entityId: this.entity.entity_id }
    this.dispatchEvent(e);
  }

  handleSpeed(e) {
    const fan_speed = e.target.getAttribute('value');
    this.callService('set_fan_speed', {
      fan_speed
    });
  }

  callService(service, options = {}) {
    this.hass.callService('fan', service, {
      entity_id: this.config.entity,
      ...options
    });
  }

  callXiaomiService(service, options = {}) {
    this.hass.callService('xiaomi_miio', service, {
      entity_id: this.config.entity,
      ...options
    });
  }

  renderAQI(aqi) {
    let prefix = '';
    if (aqi < 10) {
      prefix = html`<span class="number-off">00</span>`
    } else if (aqi < 100) {
      prefix = html`<span class="number-off">0</span>`
    }
    return html`
      ${prefix}<span class="number-on">${aqi}</span>
    `
  }

  renderStats() {
    const {
      attributes: {
        filter_life_remaining,
        motor_speed
      }
    } = this.entity

    return html`
      <div class="stats-block">
        <span class="stats-hours">${filter_life_remaining}</span> <sup>%</sup>
        <div class="stats-subtitle">Filter remaining</div>
      </div>
      <div class="stats-block">
        <span class="stats-hours">${motor_speed}</span> <sup>RPM</sup>
        <div class="stats-subtitle">Motor speed</div>
      </div>
    `
  }

  render() {
    if (!this.entity) {
      return html`<ha-card>Loading component</ha-card>`
    }
    const { state, attributes: { aqi } } = this.entity
    const on = state === 'on';
    const off = !on;

    return html`
      ${styles}
      <ha-card>
        <div class="preview ${off && 'idle'}" @click='${(e) => this.handleMore()}' ?more-info=true>
          <div class="current-aqi">
            ${this.renderAQI(aqi)}
            <sup>AQI</sup>
          </div>
        </div>
        <div class="stats">${this.renderStats()}</div>
        ${this.renderToolbar()}
      </ha-card>
    `
  }

  setFavorite(level) {
    this.callService('turn_on')
    setTimeout(() => {
      this.callService('set_speed', { speed: 'Favorite' })
    }, 500)
    setTimeout(() => {
      this.callXiaomiService('fan_set_favorite_level', { level })
    }, 1000)
  }

  renderToolbar() {
    const { state, attributes: { favorite_level, mode } } = this.entity

    return html`
      <div class="toolbar">
        <ha-icon-button  icon="mdi:power-standby"
                            title="Power"
                            class="toolbar-split toolbar-item ${state == 'on' && 'toolbar-item-on'}"
                            @click='${(e) => this.callService('toggle')}'>
        </ha-icon-button>
        <div class="fill-gap"></div>

        <ha-icon-button  icon="mdi:weather-night"
                            title="Sleep"
                            class="toolbar-item ${mode == 'silent' && 'toolbar-item-on'}"
                            @click='${(e) => this.callService('set_speed', { speed: 'Silent' })}'>
        </ha-icon-button>

        <ha-icon-button  icon="mdi:circle-slice-3"
                            title="30%"
                            class="toolbar-item ${mode == 'favorite' && favorite_level == 3 && 'toolbar-item-on'}"
                            @click='${(e) => this.setFavorite(3)}'>
        </ha-icon-button>

        <ha-icon-button  icon="mdi:circle-slice-4"
                            title="50%"
                            class="toolbar-item ${mode == 'favorite' && favorite_level == 6 && 'toolbar-item-on'}"
                            @click='${(e) => this.setFavorite(6)}'>
        </ha-icon-button>
        <ha-icon-button  icon="mdi:circle-slice-6"
                            title="70%"
                            class="toolbar-item ${mode == 'favorite' && favorite_level == 8 && 'toolbar-item-on'}"
                            @click='${(e) => this.setFavorite(8)}'>
        </ha-icon-button>
        <ha-icon-button  icon="mdi:circle-slice-8"
                            title="100%"
                            class="toolbar-item ${mode == 'favorite' && favorite_level == 12 && 'toolbar-item-on'}"
                            @click='${(e) => this.setFavorite(12)}'>
        </ha-icon-button>
        <ha-icon-button  icon="mdi:brightness-auto"
                            title="Auto"
                            class="toolbar-item ${mode == 'auto' && 'toolbar-item-on'}"
                            @click='${(e) => this.callService('set_speed', { speed: 'Auto' })}'>
        </ha-icon-button>
      </div>
    `
  }

  setConfig(config) {
    this.config = config;
  }

  getCardSize() {
    return 1;
  }
}

customElements.define('air-purifier-card', AirPurifierCard);
