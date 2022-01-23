function getLogConfig() {
  config = {
    forceConsole: true,
  };

  if (process.env.LOGFILENAME) {
    config.filename = process.env.LOGFILENAME;
  }

  return config;
}

// Obtain the security keys from the environment variables.
// The server and driver don't allow blank or undefined keys,
// so skip any unset/blank environment variables. The server checks
// the key lengths and converts to a Buffer for us.
function getSecurityKeys() {
  const env_keys = {
    S2_AccessControl: process.env.S2_ACCESS_CONTROL_KEY,
    S2_Authenticated: process.env.S2_AUTHENTICATED_KEY,
    S2_Unauthenticated: process.env.S2_UNAUTHENTICATED_KEY,
    S0_Legacy: process.env.S0_LEGACY_KEY || process.env.NETWORK_KEY,
  };

  keys = {};
  for (const [name, key] of Object.entries(env_keys)) {
    if (key) {
      keys[name] = key;
    }
  }

  return keys;
}

module.exports = {
  logConfig: getLogConfig(),
  storage: {
    cacheDir: "/cache",
    deviceConfigPriorityDir: "/cache/config",
  },
  securityKeys: getSecurityKeys(),
};
