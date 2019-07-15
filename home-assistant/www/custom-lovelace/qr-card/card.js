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
      flex-direction: column;
      flex: 1;
      position: relative;
      padding: 0px;
      border-radius: 2px;
      overflow: hidden;
    }

    ha-card img {
      width: 100%;
      image-rendering: crisp-edges;
    }
  </style>
`

class QRCard extends LitElement {
  static get properties() {
    return {
      hass: Object,
      config: Object,
      src: {
        type: String,
        notify: true,
        reflectToAttribute: true,
      },
    }
  }

  render() {
    const { code } = this.config
    QRCode.toDataURL(code, { errorCorrectionLevel: 'H' } , (err, url) => {
      this.src = url
    })

    return html`
      ${styles}
      <ha-card>
        <img src="${this.src}" />
      </ha-card>
    `
  }

  setConfig(config) {
    this.config = config;
  }

  getCardSize() {
    return 1;
  }
}

customElements.define('qr-card', QRCard);
