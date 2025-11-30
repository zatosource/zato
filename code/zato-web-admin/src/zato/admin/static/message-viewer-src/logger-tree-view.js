import { getModuleLogger, LOG_LEVEL } from './debug-utils.js';

const logger = getModuleLogger('tree-view');
logger.setLevel(LOG_LEVEL.INFO);

export { logger };
