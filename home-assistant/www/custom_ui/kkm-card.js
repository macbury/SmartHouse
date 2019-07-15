import { LitElement, html } from 'https://unpkg.com/@polymer/lit-element@0.6.5/lit-element.js?module';

const styles = html`
  <style>
    :host {
      display: flex;
      flex: 1;
      flex-direction: column;
    }
    ha-card {
      flex-direction: column;
      flex: 1;
      padding: 16px;
      position: relative;
      cursor: pointer;
    }

    ha-card > div {
      padding: 20px 0 0 8px;
    }
    ha-card > div:first-child {
      padding-top: 0;
    }
    .flex {
      display: flex;
      display: -webkit-flex;
      min-width: 0;
    }
    .name {
      align-items: center;
      min-width: 0;
      opacity: .8;
    }
    .name > span {
      font-size: 1.2rem;
      font-weight: 500;
      max-height: 1.4rem;
      opacity: .75;
    }
    .icon {
      color: var(--paper-item-icon-color, #44739e);
      display: inline-block;
      flex: 0 0 24px;
      margin-right: 8px;
      text-align: center;
      width: 24px;
    }

    .subinfo {
      color: var(--paper-item-icon-color, #44739e);
      font-size: 1.0em;
      margin-top: 0px;
      padding-top: 3px;
      padding-left: 40px;
    }

    .info {
      flex-wrap: wrap;
      font-weight: 300;
      text-align: center;
    }

    .state {
      display: inline-block;
      font-size: 3.4em;
      line-height: 1em;
      margin-right: 4px;
      max-size: 100%;
    }

    .uom {
      align-self: flex-end;
      display: inline-block;
      font-size: 2.4em;
      font-weight: 400;
      line-height: 1.2em;
      margin-top: .1em;
      opacity: .6;
      vertical-align: bottom;
    }
    
    .ellipsis {
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
  </style>
`

class KKMCard extends LitElement {
  static get properties() {
    return {
      hass: Object,
      config: Object,
    }
  }

  get entity() {
    return this.hass.states[this.config.entity_id]
  }

  handleMore() {
    const e = new Event('hass-more-info', { bubbles: true, composed: true })
    e.detail = { entityId: this.entity.entity_id }
    this.dispatchEvent(e);
  }

  render() {
    const { state, attributes: { friendly_name, days, lines, expire_at } } = this.entity
    return html`
      ${styles}
      <ha-card @click='${(e) => this.handleMore()}' ?more-info=true>
        <div class='header flex'>
          <div class='icon'>
            <ha-icon icon='mdi:train'></ha-icon>
          </div>
          <div class='name flex'>
            <span class='ellipsis'>${friendly_name}</span>
          </div>
        </div>
        <div class='subinfo flex'>
          <b>Linie: </b> ${lines.join(', ')}
        </div>
        <div class='info'>
          <span class='state ellipsis'>${days}</span>
          <span class='uom ellipsis'>dni</span>
        </div>
      </ha-card>
    `
  }

  setConfig(config) {
    this.config = config;
  }

  // @TODO: This requires more intelligent logic
  getCardSize() {
    return 1;
  }
}

customElements.define('kkm-card', KKMCard);