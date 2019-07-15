const Wallpaper = {
  viewDiv: null,
  hass: null,
  entityId: null,

  timeOfDay: () => {
    if (!Wallpaper.hass) {
      return 'evening'
    }

    const entity = Wallpaper.hass.states[Wallpaper.entityId]
    const {
      state,
      attributes: {
        next_dawn,
        next_dusk,
        next_midnight,
        next_noon,
        next_rising,
        next_setting
      }
    } = entity

    const nextDawn = new Date(next_dawn); // świt
    const nextRising = new Date(next_rising); // wschód
    const nextNoon = new Date(next_noon); // południe
    const nextSetting = new Date(next_setting); // zachód
    const nextDusk = new Date(next_dusk); // zmierzch
    const nextMidnight = new Date(next_midnight); // północ

    const now = new Date();

    let timeOfDay = 'night';

    if (nextRising > nextSetting) {
      if (nextRising < now) {
        timeOfDay = 'morning';
      } else {
        timeOfDay = 'afternoon';
      }
    } else {
      if (nextDusk < now) {
        timeOfDay = 'evening';
      } else {
        timeOfDay = 'night';
      }
    }

    return timeOfDay
  },

  refresh: () => {
    Wallpaper.viewDiv.style.background = `linear-gradient( rgba(0,0,0,.5), rgba(0,0,0,.5) ), url("/local/wallpapers/${Wallpaper.timeOfDay()}.png") fixed center bottom/cover`;
    Wallpaper.viewDiv.style.marginTop = '0px';
    window.dispatchEvent(new Event('resize'))
  }
}

const docRoot = document.querySelector('home-assistant').shadowRoot;
const main = docRoot.querySelector('home-assistant-main').shadowRoot;
const viewDiv = main.querySelector('ha-panel-lovelace').shadowRoot.querySelector('hui-root').shadowRoot.querySelector('ha-app-layout').querySelector('[id="view"]');

Wallpaper.viewDiv = viewDiv

setInterval(Wallpaper.refresh, 100)

class DynamicWallpaper extends HTMLElement {
  set hass(hass) {
    Wallpaper.hass = hass
    Wallpaper.entityId = this.config.entity
    Wallpaper.refresh()
  }

  setConfig(config) {
    this.config = config;
  }

  getCardSize() {
    return 0;
  }
}

customElements.define('dynamic-wallpaper', DynamicWallpaper);
