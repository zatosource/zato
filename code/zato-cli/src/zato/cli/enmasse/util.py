# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.cli.enmasse.importer import EnmasseYAMLImporter
    from zato.common.typing_ import anydict, bool_

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

def security_needs_update(yaml_item:'anydict', db_def:'anydict', importer:'EnmasseYAMLImporter') -> 'bool_':

    yaml_security = yaml_item.get('security')
    db_security_id = db_def.get('security_id')

    # If security is not defined in YAML but exists in DB - update needed
    if yaml_security is None and db_security_id is not None:
        logger.info('Security removed in YAML but exists in DB')
        return True

    # If security is defined in YAML but not in DB - update needed
    elif yaml_security is not None and db_security_id is None:
        logger.info('Security defined in YAML but missing in DB')
        return True

    # If security is defined in both, check if they match
    elif yaml_security is not None and db_security_id is not None:
        if yaml_security not in importer.sec_defs:
            logger.warning('Security definition %s not found, skipping comparison', yaml_security)
            return False

        sec_def = importer.sec_defs[yaml_security]
        if sec_def['id'] != db_security_id:
            logger.info('Security mismatch: YAML=%s DB_ID=%s', yaml_security, db_security_id)
            return True

    return False

# ################################################################################################################################
# ################################################################################################################################
