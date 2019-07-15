// Modules to control application life and create native browser window
const { app, BrowserWindow, ipcMain } = require('electron')
const WakeUp = require('./wakeup')
const argv = require('yargs').argv

app.commandLine.appendSwitch('--enable-touch-events')
app.commandLine.appendSwitch('touch-events', 'enabled');
app.commandLine.appendSwitch('pinch', 'enabled');
app.commandLine.appendSwitch('smooth-scrolling', 'enabled');
app.commandLine.appendSwitch('scroll-prediction', 'enabled');

if (!argv.host) {
  console.error("Set --host= flag to point your home assistant instance")
  process.exit(127)
}

// Keep a global reference of the window object, if you don't, the window will
// be closed automatically when the JavaScript object is garbage collected.
let mainWindow

const extendHaScript = `
  const script = document.createElement('script');
  script.type = "module";
  script.src = '/local/kiosk/kiosk.js?'+(new Date()).getTime();
  document.body.appendChild(script);
`

function createWindow () {
  const production = !!argv.production
  // Create the browser window.
  mainWindow = new BrowserWindow({
    title: 'SmartHouse',
    width: 1366, 
    height: 768,
    movable: !production,
    alwaysOnTop: production,
    fullscreen: production,
    showCursor: false,
    acceptFirstMouse: true,
    kiosk: production,
    webPreferences: {
      devTools: !production,
      experimentalFeatures: true,
      nodeIntegration: true,
      plugins: true,
      allowDisplayingInsecureContent: true,
      scrollBounce: false
    }
  })

  // and load the index.html of the app.
  mainWindow.loadFile('index.html')
  mainWindow.argv = argv

  // Open the DevTools.
  if (argv.dev) {
    mainWindow.webContents.openDevTools()
  }

  // Emitted when the window is closed.
  mainWindow.on('closed', function () {
    // Dereference the window object, usually you would store windows
    // in an array if your app supports multi windows, this is the time
    // when you should delete the corresponding element.
    mainWindow = null
  })

  const { webContents } = mainWindow

  //http://simurai.com/electron.atom.io/docs/tutorial/using-widevine-cdm-plugin/#getting-the-plugin
  // Allow embedding spotify web player in iframe :P
  webContents.session.webRequest.onHeadersReceived({}, (d, c) => {     
    if(d.responseHeaders['x-frame-options'] ||
        d.responseHeaders['X-Frame-Options'] || 
        d.responseHeaders['Content-Security-Policy'] ||
        d.responseHeaders['content-security-policy']){
      delete d.responseHeaders['x-frame-options'];
      delete d.responseHeaders['X-Frame-Options'];
      delete d.responseHeaders['Content-Security-Policy'];
      delete d.responseHeaders['content-security-policy'];
    }

    c({cancel: false, responseHeaders: d.responseHeaders, statusLine: d.statusLine});
  });

  const wakeUp = new WakeUp();
  wakeUp.screenOn();
  webContents.on("did-finish-load", () => {
    if (webContents.getURL().match(argv.host)) {
      wakeUp.screenOn();
      console.log("Loaded home assistant instance!");
      webContents.executeJavaScript(extendHaScript);
    }
  })

  ipcMain.on('kiosk:wake', (event, arg) => {
    wakeUp.reset();
  })
}

// This method will be called when Electron has finished
// initialization and is ready to create browser windows.
// Some APIs can only be used after this event occurs.
app.on('ready', createWindow)

// Quit when all windows are closed.
app.on('window-all-closed', function () {
  // On macOS it is common for applications and their menu bar
  // to stay active until the user quits explicitly with Cmd + Q
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

app.on('activate', function () {
  // On macOS it's common to re-create a window in the app when the
  // dock icon is clicked and there are no other windows open.
  if (mainWindow === null) {
    createWindow()
  }
})

// In this file you can include the rest of your app's specific main process
// code. You can also put them in separate files and require them here.
