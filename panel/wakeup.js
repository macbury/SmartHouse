const exec = require('child_process').exec;

class WakeUp {
  constructor() {
    this.timeout = null
  }

  reset() {
    if (this.timeout != null) {
      clearTimeout(this.timeout);
      this.timeout = null;
    }
    this.timeout = setTimeout(() => this.screenOff(), 25 * 1000)
  }

  screenOff() {
    console.log("Screen off");
    try {
      exec("xset -display :0.0 dpms force off", null);
    } catch(e) {
      console.error(e);
    }
  }

  screenOn() {
    console.log("Screen on");
    try {
      exec("xset -display :0.0 dpms force on", null);
    } catch(e) {
      console.error(e);
    }
  }
}

module.exports = WakeUp