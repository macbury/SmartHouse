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
      position: relative;
      padding: 0px;
      border-radius: 4px;
      overflow: hidden;
    }

    .preview {
      display: flex;
      flex-direction: row;
      background: #ef7f02; /* fallback for old browsers */
      background: -webkit-linear-gradient(to bottom, #ef7f02, #cc6d02); /* Chrome 10-25, Safari 5.1-6 */
      background: linear-gradient(to bottom, #ef7f02, #cc6d02); /* W3C, IE 10+/ Edge, Firefox 16+, Chrome 26+, Opera 12+, Safari 7+ */
      overflow: hidden;
      position: relative;
      min-height: 365px;
    }

    .preview .toolbar {
      width: 164px;
    }

    .preview .knob {
      background: #fff;
      position: absolute;
      right: 55px;
      top: 100px;
      border-radius: 35px;
      width: 50px;
      overflow: hidden;
      height: 196px;
    }

    .preview .knob .knob-button {
      display: block;
      height: 98px;
      width: 50px;
    }

    .preview .knob .knob-button ha-icon {
      width: 50px;
      height: 98px;
      color: #030303;
    }

    .preview .knob .knob-button:active {
      background: rgba(0, 0, 0, 0.06);
    }

    .courtain-container {
      position: relative;
    }

    .courtain-preview {
      flex: 1;
      border-right: 1px solid rgba(255, 255, 255, 0.1);
    }

    .courtain-engine {
      background: #fffdfa;
      width: 100%;
      height: 40px;
      z-index: 10;
      position: absolute;
      top: 0px;
    }

    .courtain-slate {
      background: #fffdfa;
      opacity: 0.9;
      width: 100%;
      height: 20px;
      position: absolute;
    }

    .courtain-fabric {
      background: #ffab51;
      width: 100%;
      height: 365px;
      opacity: 0.5;
      position: relative;
      transition: all 0.2s linear;
    }

    .presets-container {
      position: absolute;
      right: 10px;
      top: 10px;
    }
  </style>
`

class CourtainCard extends LitElement {
  static get properties() {
    return {
      hass: Object,
      config: Object,
      stepBy: Object,
      targetHeight: Object
    }
  }

  get entity() {
    return this.hass.states[this.config.entity]
  }

  get alpha() {
    return (this.targetHeight - this.minHeight) / (this.maxHeight - this.minHeight)
  }

  get maxHeight() {
    return this.config.height.max
  }

  get minHeight() {
    return this.config.height.min
  }

  handleMore() {
    const e = new Event('hass-more-info', { bubbles: true, composed: true })
    e.detail = { entityId: this.entity.entity_id }
    this.dispatchEvent(e);
  }

  callService(service, options = {}) {
    this.hass.callService('cover', service, {
      entity_id: this.config.entity,
      ...options
    });
  }

  handlePreset(e) {
    const height = parseInt(e.target.getAttribute('value'))
    this.targetHeight = height
    this.updateHeight()
  }

  renderPresets() {
    const presets = this.config.presets
    const selected = presets.find(({ target }) => target == this.targetHeight)
    const preset = selected ? selected.label : 'Custom'

    return html`
      <paper-menu-button class='preset-menu' slot='dropdown-trigger'
        .horizontalAlign=${'right'} .verticalAlign=${'top'}
        .verticalOffset=${40} .noAnimations=${true}
        @click='${(e) => e.stopPropagation()}'>
        <paper-button class='preset-menu__button' slot='dropdown-trigger'>
          <span class='preset-menu__preset' show=${true}>
            ${preset}
          </span>
          <ha-icon icon="mdi:unfold-more-horizontal"></ha-icon>
        </paper-button>
        <paper-listbox slot='dropdown-content' selected=${preset}
          @click='${(e) => this.handlePreset(e)}'>
          ${presets.map(item => html`<paper-item value=${item.target}>${item.label}</paper-item>`)}
        </paper-listbox>
      </paper-menu-button>`;
  }

  tick() {
    this.targetHeight += this.stepBy
    if (this.targetHeight > this.maxHeight) {
      this.targetHeight = this.maxHeight
    } else if (this.targetHeight < this.minHeight) {
      this.targetHeight = this.minHeight
    } else {
      this.updateHeight()
      this.tickTimer = setTimeout(() => this.tick(), 100)
    }
  }

  updateHeight() {
    this.callService('set_cover_position', { position: Math.round(this.alpha * 100) })
  }

  incPressed(e) {
    this.stepBy = 1
    this.tick()
  }

  decPressed(e) {
    this.stepBy = -1
    this.tick()
  }

  cancelPress(e) {
    this.stepBy = 0
    if (this.tickTimer) {
      clearTimeout(this.tickTimer)
      this.tickTimer = null
    }
  }

  calculateOffset(maxValue) {
    return Math.round(maxValue * (1.0 - this.alpha))
  }

  render() {
    return html`
      ${styles}
      <ha-card>
        <div class="preview">
          <div class="courtain-preview">
            <div class="courtain-container">
              <div class="courtain-fabric" style="transform: translateY(0px)">
                <div class="courtain-slate" style="top: 20px;"></div>
                <div class="courtain-slate" style="top: 60px;"></div>
                <div class="courtain-slate" style="top: 100px;"></div>
                <div class="courtain-slate" style="top: 140px;"></div>
                <div class="courtain-slate" style="top: 180px;"></div>
                <div class="courtain-slate" style="top: 220px;"></div>
                <div class="courtain-slate" style="top: 260px;"></div>
                <div class="courtain-slate" style="top: 300px;"></div>
                <div class="courtain-slate" style="top: 340px;"></div>
              </div>
              <div class="courtain-engine"></div>
            </div>
          </div>

          <div class="toolbar">
            <div class="knob">
              <div class="knob-button" 
                  @touchstart='${() => this.incPressed()}' 
                  @mousedown='${() => this.incPressed()}' 
                  @touchend='${() => this.cancelPress()}'
                  @mouseup='${() => this.cancelPress()}'>
                <ha-icon icon="mdi:chevron-up"></ha-icon>
              </div>

              <div class="knob-button" 
                  @touchstart='${() => this.decPressed()}' 
                  @mousedown='${() => this.decPressed()}' 
                  @touchend='${() => this.cancelPress()}'
                  @mouseup='${() => this.cancelPress()}'>
                <ha-icon icon="mdi:chevron-down"></ha-icon>
              </div>
            </div>

            <div class="presets-container">
              ${this.renderPresets()}

              <paper-icon-button icon="hass:dots-vertical" @click='${() => this.handleMore()}' />
            </div>
          </div>
        </div>
      </ha-card>
    `
  }

  setConfig(config) {
    this.config = config;
    this.targetHeight = config.height.min
  }

  getCardSize() {
    return 2;
  }
}

customElements.define('courtain-card', CourtainCard);