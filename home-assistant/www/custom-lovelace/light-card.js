class LightCard extends HTMLElement {

  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this.delay;
  }

  setConfig(config) {
    if (!config.entity) {
      throw new Error('You need to define an entity');
    }
    const root = this.shadowRoot;
    if (root.lastChild) root.removeChild(root.lastChild);
    const card = document.createElement('ha-card');
    const content = document.createElement('paper-button');
    card.appendChild(content);
    const bulbIcon = document.createElement('ha-icon');

    bulbIcon.style.display = 'block';
    bulbIcon.style.margin = 'auto';
    const cardConfig = Object.assign({}, config);
    bulbIcon.style.width = `${cardConfig.size ? cardConfig.size : "40%"}`;
    bulbIcon.style.height = `${cardConfig.size ? cardConfig.size : "40%"}`;
    if (!cardConfig.bulb_icon){
      cardConfig.bulb_icon = 'mdi:lightbulb';
    }
    bulbIcon.icon = cardConfig.bulb_icon;
    content.addEventListener('click', event => {
      this._fire('hass-more-info', { entityId: cardConfig.entity });
    });
    content.appendChild(bulbIcon);
    root.appendChild(card);
    this._config = cardConfig;

  }


  set hass(hass) {

    const entityId = this._config.entity;
    const state = hass.states[entityId];
    if (!state) {
      return
    }
    const stateStr = state ? state.state : 'unavailable';
    if (state.attributes.rgb_color) {
      this.shadowRoot.children[0].children[0].children[0].style.color = `rgb(${state.attributes.rgb_color.join(',')})`;
    } else if (state.state === 'on') {
      this.shadowRoot.children[0].children[0].children[0].style.color = `rgb(255, 218, 109)`;
    }
    if (state.state === 'off') {
      this.shadowRoot.children[0].children[0].children[0].style.color = "var(--disabled-text-color)";
    }
  }

  _fire(type, detail, options) {
    const node = this.shadowRoot;
    options = options || {};
    detail = (detail === null || detail === undefined) ? {} : detail;
    const event = new Event(type, {
      bubbles: options.bubbles === undefined ? true : options.bubbles,
      cancelable: Boolean(options.cancelable),
      composed: options.composed === undefined ? true : options.composed
    });
    event.detail = detail;
    node.dispatchEvent(event);
    return event;
  }


  getCardSize() {
    return 3;
  }
}

customElements.define('light-card', LightCard);
