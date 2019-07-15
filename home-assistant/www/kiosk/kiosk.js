const { ipcRenderer } = require('electron')
class KioskApp {
  constructor() {
    const style = document.createElement('style');
    style.type = 'text/css';
    style.appendChild(document.createTextNode(`
      ::-webkit-scrollbar { 
        display: none; 
      }
    `));

    document.body.appendChild(style);

    document.body.addEventListener('touchstart', function(e) {
      ipcRenderer.send('kiosk:wake');
    });
    ipcRenderer.send('kiosk:wake');
  }
}

window.kioskApp = new KioskApp();
