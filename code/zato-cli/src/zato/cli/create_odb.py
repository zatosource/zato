# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from datetime import datetime
from getpass import getuser
from socket import gethostname

# SQLAlchemy
from sqlalchemy.dialects.postgresql.base import PGTypeCompiler

# Zato
from zato.cli import common_odb_opts, is_arg_given, ZatoCommand
from zato.common.odb.model import AlembicRevision, Base, ZatoInstallState

LATEST_ALEMBIC_REVISION = '0028_ae3419a9'
VERSION = 1

class Create(ZatoCommand):
    """ Creates a new Zato ODB (Operational Database)
    """
    opts = common_odb_opts
    opts.append({'name':'--skip-if-exists',
        'help':'Return without raising an error if ODB already exists', 'action':'store_true'})

    def execute(self, args, show_output=True):
        engine = self._get_engine(args)
        session = self._get_session(engine)

        if engine.dialect.has_table(engine.connect(), 'install_state'):

            if is_arg_given(args, 'skip-if-exists'):
                if show_output:
                    if self.verbose:
                        self.logger.debug('ODB already exists, skipped its creation')
                    else:
                        self.logger.info('OK')
            else:
                if show_output:
                    version = session.query(ZatoInstallState.version).one().version
                    msg = (
                        'The ODB (v. {}) already exists, not creating it. ' +
                        "Use the 'zato delete odb' command first if you'd like to start afresh and " +
                        'recreate all ODB objects.').format(version)
                    self.logger.error(msg)

                return self.SYS_ERROR.ODB_EXISTS

        else:

            # This is needed so that PubSubMessage.data can continue to use length
            # in the column's specification which in itself is needed for MySQL to use LONGTEXT.

            def _render_string_type(self, type_, name):

                text = name
                if type_.length and name != 'TEXT':
                    text += "(%d)" % type_.length
                if type_.collation:
                    text += ' COLLATE "%s"' % type_.collation
                return text

            PGTypeCompiler._render_string_type = _render_string_type

            Base.metadata.create_all(engine)

            state = ZatoInstallState(None, VERSION, datetime.now(), gethostname(), getuser())
            alembic_rev = AlembicRevision(LATEST_ALEMBIC_REVISION)

            session.add(state)
            session.add(alembic_rev)

            session.commit()

            if show_output:
                if self.verbose:
                    self.logger.debug('Successfully created the ODB')
                else:
                    self.logger.info('OK')
