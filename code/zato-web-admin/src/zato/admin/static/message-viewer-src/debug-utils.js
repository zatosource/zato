// debug-utils.js - Simplified logging utilities as ES module

/**
 * Log levels
 * 0 = OFF - No logging
 * 1 = ERROR - Only errors
 * 2 = WARN - Errors and warnings
 * 3 = INFO - Errors, warnings, and info
 * 4 = DEBUG - All logs including debug
 */
export const LOG_LEVEL = {
  OFF: 0,
  ERROR: 1,
  WARN: 2,
  INFO: 3,
  DEBUG: 4
};

// Reverse mapping for log level names
const LOG_LEVEL_NAMES = Object.freeze({
  [LOG_LEVEL.DEBUG]: 'DEBUG',
  [LOG_LEVEL.INFO]: 'INFO',
  [LOG_LEVEL.WARN]: 'WARN',
  [LOG_LEVEL.ERROR]: 'ERROR',
  [LOG_LEVEL.OFF]: 'OFF'
});

// Set the current log level (adjust as needed, e.g., via config or env var)
export let CURRENT_LOG_LEVEL = LOG_LEVEL.DEBUG;

// --- Helper function to get call site ---
function getCallSite() {
    try {
        const err = new Error();
        if (!err.stack || typeof err.stack !== 'string') {
            return { func: 'unknown', path: 'unknown', line: '0', col: '0' };
        }

        const stackLines = err.stack.split('\n');
        const basePathMarker = '/static/message-viewer-src/';

        for (let i = 2; i < stackLines.length; i++) {
            const callerLine = stackLines[i] ? stackLines[i].trim() : '';
            if (!callerLine || callerLine.includes('debug-utils.js')) continue;

            let match;
            match = callerLine.match(/at (?:\S+\.)?(\S+) \((.+):(\d+):(\d+)\)/) || callerLine.match(/at (.+?) \((.+):(\d+):(\d+)\)/);
            if (match) {
                let funcName = match[1];
                let filePath = match[2];
                let lineNum = match[3];
                let colNum = match[4];
                if (funcName) {
                    funcName = funcName.replace('/<', '');
                    if (funcName.startsWith('Object.')) {
                        funcName = funcName.substring('Object.'.length);
                    }
                }

                const basePath = '/static/message-viewer-src/';
                let relativePath = 'unknown_path';
                const pathIndex = filePath.indexOf(basePath);
                if (pathIndex !== -1) {
                    relativePath = filePath.substring(pathIndex + basePath.length);
                } else {
                    const lastSlashIndex = filePath.lastIndexOf('/');
                    if (lastSlashIndex !== -1) {
                        relativePath = filePath.substring(lastSlashIndex + 1);
                    } else {
                        relativePath = filePath;
                    }
                }

                return { func: funcName, path: relativePath, line: lineNum, col: colNum };
            } else {
                match = callerLine.match(/^(.*)@(.+):(\d+):(\d+)$/);
                if (match) {
                    let funcName = match[1] || '<anonymous>';
                    let filePath = match[2];
                    let lineNum = match[3];
                    let colNum = match[4];
                    if (funcName) {
                        funcName = funcName.replace('/<', '');
                        if (funcName.startsWith('Object.')) {
                            funcName = funcName.substring('Object.'.length);
                        }
                    }

                    const basePath = '/static/message-viewer-src/';
                    let relativePath = 'unknown_path';
                    const pathIndex = filePath.indexOf(basePath);
                    if (pathIndex !== -1) {
                        relativePath = filePath.substring(pathIndex + basePath.length);
                    } else {
                        const lastSlashIndex = filePath.lastIndexOf('/');
                        if (lastSlashIndex !== -1) {
                            relativePath = filePath.substring(lastSlashIndex + 1);
                        } else {
                            relativePath = filePath;
                        }
                    }

                    return { func: funcName, path: relativePath, line: lineNum, col: colNum };
                } else {
                    match = callerLine.match(/^(.*):(\d+):(\d+)$/);
                    if (match) {
                        let funcName = '<anonymous>';
                        let filePath = match[1];
                        let lineNum = match[2];
                        let colNum = match[3];
                        const basePath = '/static/message-viewer-src/';
                        let relativePath = 'unknown_path';
                        const pathIndex = filePath.indexOf(basePath);
                        if (pathIndex !== -1) {
                            relativePath = filePath.substring(pathIndex + basePath.length);
                        } else {
                            const lastSlashIndex = filePath.lastIndexOf('/');
                            if (lastSlashIndex !== -1) {
                                relativePath = filePath.substring(lastSlashIndex + 1);
                            } else {
                                relativePath = filePath;
                            }
                        }

                        return { func: funcName, path: relativePath, line: lineNum, col: colNum };
                    }
                }
            }
        }
    } catch (e) {
        console.warn("Error getting call site for logging:", e);
    }

    return { func: 'unknown', path: 'unknown', line: '1', col: '1' };
}

export class Logger {
  constructor(moduleName, level) {
    this.moduleName = moduleName;
    this.level = level;
  }

  setLevel(level) {
    this.level = level;
  }

  debug(message, data) {
    if (this.level >= LOG_LEVEL.DEBUG) {
      const levelName = LOG_LEVEL_NAMES[LOG_LEVEL.DEBUG];
      const callSiteInfo = getCallSite();
      const prefix = `${levelName} [${this.moduleName} - ${callSiteInfo.func} - ${callSiteInfo.path}:${callSiteInfo.line}:${callSiteInfo.col}]`;
      if (data !== undefined) {
        console.debug(prefix, message, data);
      } else {
        console.debug(prefix, message);
      }
    }
  }

  info(message, data) {
    if (this.level >= LOG_LEVEL.INFO) {
      const levelName = LOG_LEVEL_NAMES[LOG_LEVEL.INFO];
      const callSiteInfo = getCallSite();
      const prefix = `${levelName} [${this.moduleName} - ${callSiteInfo.func} - ${callSiteInfo.path}:${callSiteInfo.line}:${callSiteInfo.col}]`;
      if (data !== undefined) {
        console.info(prefix, message, data);
      } else {
        console.info(prefix, message);
      }
    }
  }

  warn(message, data) {
    if (this.level >= LOG_LEVEL.WARN) {
      const levelName = LOG_LEVEL_NAMES[LOG_LEVEL.WARN];
      const callSiteInfo = getCallSite();
      const prefix = `${levelName} [${this.moduleName} - ${callSiteInfo.func} - ${callSiteInfo.path}:${callSiteInfo.line}:${callSiteInfo.col}]`;
      if (data !== undefined) {
        console.warn(prefix, message, data);
      } else {
        console.warn(prefix, message);
      }
    }
  }

  error(message, data) {
    if (this.level >= LOG_LEVEL.ERROR) {
      const levelName = LOG_LEVEL_NAMES[LOG_LEVEL.ERROR];
      const callSiteInfo = getCallSite();
      const prefix = `${levelName} [${this.moduleName} - ${callSiteInfo.func} - ${callSiteInfo.path}:${callSiteInfo.line}:${callSiteInfo.col}]`;
      if (data !== undefined) {
        console.error(prefix, message, data);
      } else {
        console.error(prefix, message);
      }
    }
  }
}

export function getModuleLogger(moduleName, defaultLevel = CURRENT_LOG_LEVEL) {
  return new Logger(moduleName, defaultLevel);
}

export function setLogLevel(level) {
  CURRENT_LOG_LEVEL = level;
}

export function debug_log(message, data) {
  if (CURRENT_LOG_LEVEL >= LOG_LEVEL.DEBUG) {
    const levelName = LOG_LEVEL_NAMES[LOG_LEVEL.DEBUG];
    const callSiteInfo = getCallSite();
    const prefix = `${levelName} [${callSiteInfo.func} - ${callSiteInfo.path}:${callSiteInfo.line}:${callSiteInfo.col}]`;
    if (data !== undefined) {
      console.debug(prefix, message, data);
    } else {
      console.debug(prefix, message);
    }
  }
}

export function info_log(message, data) {
  if (CURRENT_LOG_LEVEL >= LOG_LEVEL.INFO) {
    const levelName = LOG_LEVEL_NAMES[LOG_LEVEL.INFO];
    const callSiteInfo = getCallSite();
    const prefix = `${levelName} [${callSiteInfo.func} - ${callSiteInfo.path}:${callSiteInfo.line}:${callSiteInfo.col}]`;
    if (data !== undefined) {
      console.info(prefix, message, data);
    } else {
      console.info(prefix, message);
    }
  }
}

export function warn_log(message, data) {
  if (CURRENT_LOG_LEVEL >= LOG_LEVEL.WARN) {
    const levelName = LOG_LEVEL_NAMES[LOG_LEVEL.WARN];
    const callSiteInfo = getCallSite();
    const prefix = `${levelName} [${callSiteInfo.func} - ${callSiteInfo.path}:${callSiteInfo.line}:${callSiteInfo.col}]`;
    if (data !== undefined) {
      console.warn(prefix, message, data);
    } else {
      console.warn(prefix, message);
    }
  }
}

export function error_log(message, data) {
  if (CURRENT_LOG_LEVEL >= LOG_LEVEL.ERROR) {
    const levelName = LOG_LEVEL_NAMES[LOG_LEVEL.ERROR];
    const callSiteInfo = getCallSite();
    const prefix = `${levelName} [${callSiteInfo.func} - ${callSiteInfo.path}:${callSiteInfo.line}:${callSiteInfo.col}]`;
    if (data !== undefined) {
      console.error(prefix, message, data);
    } else {
      console.error(prefix, message);
    }
  }
}
