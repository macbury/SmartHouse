const { remote } = require('electron')
const electron = require('electron');

async function waithForHa() {
  const host = remote.getCurrentWindow().argv.host
  try {
    const resp = await fetch(host)
    if (resp.ok) {
      window.location.href = host
    } else {
      setTimeout(waithForHa, 5000)
    }
  } catch (e) {
    setTimeout(waithForHa, 5000)
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const webFrame = electron.webFrame;
  webFrame.setZoomLevel(1.0);
  webFrame.setVisualZoomLevelLimits(1, 1);
  webFrame.setLayoutZoomLevelLimits(0, 0);
  document.body.requestPointerLock();
  waithForHa();
})