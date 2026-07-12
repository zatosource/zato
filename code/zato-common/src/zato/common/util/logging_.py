# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os
from contextvars import ContextVar

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import anydict, anylist, dictlist, intnone, stranydict
    anydict = anydict
    anylist = anylist
    dictlist = dictlist
    intnone = intnone
    stranydict = stranydict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# The global override applies to every logger, the per-logger ones select a single logger by the suffix
log_level_env_global = 'Zato_Log_Level'
log_level_env_prefix = 'Zato_Log_Level_'

# Level names that the env variables accept
_allowed_log_levels = {'TRACE1', 'NOTSET', 'DEBUG', 'INFO', 'WARN', 'WARNING', 'ERROR', 'CRITICAL'}

# The name under which the root logger is exposed to callers
_root_logger_name = 'root'

# Loggers that are never returned to callers
_loggers_to_ignore = {'bzr', 'future_stdlib', 'pyasn1', 'sh.command', 'zato_audit_pii', 'zato.depth_debug'}

# Used when a caller submits an empty logging configuration
_no_input_error = 'No loggers provided'

# ################################################################################################################################
# ################################################################################################################################

current_cid: ContextVar[str] = ContextVar('current_cid', default='')
current_service_name: ContextVar[str] = ContextVar('current_service_name', default='')

# ################################################################################################################################
# ################################################################################################################################

class ServiceContextFilter(logging.Filter):
    def filter(self, record):
        _cid = current_cid.get()
        _service_name = current_service_name.get()
        if _cid:
            record.zato_ctx = ' ' + _service_name + ' - ' + _cid + ' -'
        else:
            record.zato_ctx = ''
        return True

# ################################################################################################################################
# ################################################################################################################################

logging_conf_contents = """
loggers:
    '':
        level: INFO
        handlers: [stdout, default]
    'zato.server.main':
        level: INFO
        handlers: [stdout, default]
    'pytds':
        level: WARN
        handlers: [stdout, default]
    zato:
        level: INFO
        handlers: [stdout, default]
        qualname: zato
        propagate: false
    zato_rest:
        level: INFO
        handlers: [stdout, default]
        qualname: zato
        propagate: false
    zato_access_log:
        level: INFO
        handlers: [http_access_log]
        qualname: zato_access_log
        propagate: false
    zato_admin:
        level: INFO
        handlers: [admin]
        qualname: zato_admin
        propagate: false
    zato_connector:
        level: INFO
        handlers: [connector]
        qualname: zato_connector
        propagate: false
    zato_scheduler:
        level: INFO
        handlers: [stdout, scheduler]
        qualname: zato_scheduler
        propagate: false
handlers:
    default:
        formatter: default
        class: {log_handler_class}
        filename: './logs/server.log'
        mode: 'a'
        maxBytes: {server_log_max_size}
        backupCount: {server_log_backup_count}
        encoding: 'utf8'
    stdout:
        formatter: default
        class: logging.StreamHandler
        stream: ext://sys.stdout
    http_access_log:
        formatter: default
        class: {log_handler_class}
        filename: './logs/http_access.log'
        mode: 'a'
        maxBytes: {server_log_max_size}
        backupCount: {server_log_backup_count}
        encoding: 'utf8'
    admin:
        formatter: default
        class: {log_handler_class}
        filename: './logs/admin.log'
        mode: 'a'
        maxBytes: 20000000
        backupCount: 10
        encoding: 'utf8'
    connector:
        formatter: default
        class: {log_handler_class}
        filename: './logs/connector.log'
        mode: 'a'
        maxBytes: 20000000
        backupCount: 10
        encoding: 'utf8'
    scheduler:
        formatter: default
        class: {log_handler_class}
        filename: './logs/scheduler.log'
        mode: 'a'
        maxBytes: 20000000
        backupCount: 10
        encoding: 'utf8'

formatters:
    default:
        format: '%(asctime)s - %(levelname)s - %(process)d:%(threadName)s -%(zato_ctx)s %(name)s:%(lineno)d - %(message)s'
    http_access_log:
        format: '%(remote_ip)s %(cid_resp_time)s "%(channel_name)s" [%(req_timestamp)s] "%(method)s %(path)s %(http_version)s" %(status_code)s %(response_size)s "-" "%(user_agent)s"'
version: 1
""" # noqa: E501

# ################################################################################################################################
# ################################################################################################################################

def get_logging_conf_contents() -> 'str':
    # type: (str) -> str

    # We import it here to make CLI work faster
    from zato.common.util.platform_ import is_linux

    linux_log_handler_class     = 'logging.handlers.RotatingFileHandler' # Previously = ConcurrentRotatingFileHandler
    non_linux_log_handler_class = 'logging.handlers.RotatingFileHandler'

    # Under Windows, we cannot have multiple processes access the same log file
    log_handler_class = linux_log_handler_class if is_linux else non_linux_log_handler_class

    # This can be overridden by users
    if server_log_max_size := os.environ.get('Zato_Server_Log_Max_Size'):
        server_log_max_size = int(server_log_max_size)
    else:
        server_log_max_size = 1000000000 # 1 GB by default

    # This can be overridden by users
    if server_log_backup_count := os.environ.get('Zato_Server_Log_Backup_Count'):
        server_log_backup_count = int(server_log_backup_count)
    else:
        server_log_backup_count = 2

    return logging_conf_contents.format(
        log_handler_class=log_handler_class,
        server_log_max_size=server_log_max_size,
        server_log_backup_count=server_log_backup_count,
    )

# ################################################################################################################################
# ################################################################################################################################

def _get_logger_env_suffix(logger_name:'str') -> 'str':
    """ Maps a logger name to the lowercase suffix that selects it in a per-logger env variable.
    """

    # The root logger has no name of its own
    if logger_name == '':
        return 'root'

    # The zato logger is configured through the global variable alone
    if logger_name == 'zato':
        return ''

    # Strip the leading zato prefix, it is already part of the variable name ..
    out = logger_name
    for prefix in ('zato.', 'zato_'):
        if out.startswith(prefix):
            out = out[len(prefix):]
            break

    # .. turn dotted names into underscored ones ..
    out = out.replace('.', '_')

    # .. and normalize the case for comparisons.
    out = out.lower()

    return out

# ################################################################################################################################
# ################################################################################################################################

def _get_validated_log_level(env_name:'str', value:'str') -> 'str':
    """ Normalizes a level name read from an env variable, rejecting unknown ones.
    """
    out = value.upper()

    # Reject anything that is not a known level name
    if out not in _allowed_log_levels:
        raise Exception(f'Unknown log level `{value}` in environment variable `{env_name}`')

    return out

# ################################################################################################################################
# ################################################################################################################################

def apply_logging_env_overrides(config:'anydict') -> 'anydict':
    """ Applies log levels from environment variables to a configuration dict loaded from logging.conf.
    """
    loggers = config['loggers']

    # The global override applies to every logger first ..
    if global_level := os.environ.get(log_level_env_global):
        global_level = _get_validated_log_level(log_level_env_global, global_level)
        for logger_config in loggers.values():
            logger_config['level'] = global_level

    # .. map each logger to the suffix that selects it, computed once ..
    suffix_to_config = {}

    for logger_name, logger_config in loggers.items():
        suffix = _get_logger_env_suffix(logger_name)

        # An empty suffix means this logger cannot be selected individually
        if suffix:
            suffix_to_config[suffix] = logger_config

    # .. and let the per-logger overrides win over the global one. Suffixes that select
    # .. no logger are skipped because the same variables reach components whose own
    # .. logging.conf may not define every logger.
    for env_name, env_value in os.environ.items():

        if not env_name.startswith(log_level_env_prefix):
            continue

        env_suffix = env_name[len(log_level_env_prefix):].lower()

        if logger_config := suffix_to_config.get(env_suffix):
            logger_config['level'] = _get_validated_log_level(env_name, env_value)

    return config

# ################################################################################################################################
# ################################################################################################################################

def parse_logging_lines(text:'str') -> 'anylist':
    """ Parses lines in the logger=LEVEL format, returning tuples of (name, level, raw_line, error).
    """
    out:'anylist' = []

    for line in text.strip().split('\n'):
        line = line.strip()

        # Skip empty lines ..
        if not line:
            continue

        # .. and comments too ..
        if line.startswith('#'):
            continue

        # .. reject lines that are not assignments ..
        if '=' not in line:
            out.append((None, None, line, 'Missing "=" sign'))
            continue

        # .. split the line into its parts, levels are case-insensitive on input ..
        name, _, level = line.partition('=')
        name = name.strip()
        level = level.strip().upper()

        # .. a name is always required ..
        if not name:
            out.append((None, None, line, 'Empty logger name'))
            continue

        # .. and now we know the line is well-formed.
        out.append((name, level, line, None))

    return out

# ################################################################################################################################
# ################################################################################################################################

def _get_current_level(name:'str') -> 'intnone':
    """ Returns the level of an existing logger without creating one, or None if it does not exist.
    """

    # Our response to produce
    out = None

    # The root logger always exists ..
    if name == _root_logger_name:
        out = logging.root.level

    # .. named loggers are looked up without getLogger so that the lookup itself never registers a new one.
    else:
        logger_obj = logging.Logger.manager.loggerDict.get(name)
        if isinstance(logger_obj, logging.Logger):
            out = logger_obj.level

    return out

# ################################################################################################################################
# ################################################################################################################################

def get_logging_levels() -> 'stranydict':
    """ Returns all loggers whose level is set explicitly, along with their current levels.
    """
    items:'dictlist' = []

    # The root logger always goes first ..
    root_level_name = logging.getLevelName(logging.root.level)
    items.append({'name': _root_logger_name, 'level': root_level_name})

    # .. followed by named loggers, sorted by name.
    for name in sorted(logging.Logger.manager.loggerDict):
        logger_obj = logging.Logger.manager.loggerDict[name]

        # .. some loggers are never returned ..
        if name in _loggers_to_ignore:
            continue

        # .. placeholders have no level of their own ..
        if not isinstance(logger_obj, logging.Logger):
            continue

        # .. skip loggers that inherit their level from a parent ..
        if logger_obj.level == logging.NOTSET:
            continue

        # .. and report the level under its name.
        level_name = logging.getLevelName(logger_obj.level)
        items.append({'name': name, 'level': level_name})

    out = {'items': items}
    return out

# ################################################################################################################################
# ################################################################################################################################

def test_logging_levels(text:'str') -> 'stranydict':
    """ Reports what would change if the given logger levels were applied, without applying anything.
    """

    # Reject empty input outright ..
    if not text.strip():
        out = {
            'success': False,
            'error': _no_input_error,
            'results': [],
            'change_count': 0,
            'delete_count': 0,
        }
        return out

    # .. parse the input into individual lines ..
    parsed = parse_logging_lines(text)

    results:'dictlist' = []
    has_errors = False
    change_count = 0

    for name, level, raw_line, error in parsed:

        # .. malformed lines are reported as they were typed ..
        if error:
            has_errors = True
            results.append({
                'label': raw_line,
                'status': 'error',
                'message': error,
            })
            continue

        # .. unknown level names are errors too ..
        if level not in _allowed_log_levels:
            has_errors = True
            results.append({
                'label': name,
                'status': 'error',
                'message': f'Unknown log level `{level}`',
            })
            continue

        # .. compare numeric levels so that aliases like WARN and WARNING are equal ..
        current_level = _get_current_level(name)
        level_number = logging.getLevelName(level)

        # .. a logger that does not exist yet will be created on save ..
        if current_level is None:
            change_count += 1
            results.append({
                'label': name,
                'status': 'new',
                'message': level,
            })

        # .. an existing logger is reported only if its level would actually change.
        elif current_level != level_number:
            change_count += 1
            results.append({
                'label': name,
                'status': 'changed',
                'message': level,
            })

    out = {
        'success': not has_errors,
        'results': results,
        'change_count': change_count,
        'delete_count': 0,
    }
    return out

# ################################################################################################################################
# ################################################################################################################################

def set_logging_levels(text:'str') -> 'stranydict':
    """ Applies the given logger levels to the current process.
    """

    # Reject empty input outright ..
    if not text.strip():
        out = {
            'success': False,
            'error': _no_input_error,
        }
        return out

    # .. parse the input into individual lines ..
    parsed = parse_logging_lines(text)
    set_count = 0

    for name, level, _, error in parsed:

        # .. skip malformed lines ..
        if error:
            continue

        # .. and unknown level names too ..
        if level not in _allowed_log_levels:
            continue

        # .. resolve the target logger, creating it if needed ..
        if name == _root_logger_name:
            target = logging.root
        else:
            target = logging.getLogger(name)

        # .. and apply the new level.
        level_number = logging.getLevelName(level)
        target.setLevel(level_number)
        set_count += 1

    # Log what we did, using the correct singular or plural form.
    suffix = 'logger' if set_count == 1 else 'loggers'
    logger.info('Logging levels set for %d %s', set_count, suffix)

    out = {
        'success': True,
        'message': f'{set_count} set',
    }
    return out

# ################################################################################################################################
# ################################################################################################################################

def attach_service_context_filter() -> 'None':
    """ Attaches the service context filter to every handler configured so far.
    """
    context_filter = ServiceContextFilter()

    # The root logger's handlers ..
    for handler in logging.root.handlers:
        handler.addFilter(context_filter)

    # .. and the handlers of every named logger too. The manager's dict may hold
    # .. placeholder objects which have no handlers of their own, hence the check.
    for logger_obj in logging.Logger.manager.loggerDict.values():
        if hasattr(logger_obj, 'handlers'):
            for handler in logger_obj.handlers:
                handler.addFilter(context_filter)

# ################################################################################################################################
# ################################################################################################################################
