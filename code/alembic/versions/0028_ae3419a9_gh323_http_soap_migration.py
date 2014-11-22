"""gh323 http_soap migration

Revision ID: 0028_ae3419a9
Revises: 0027_e139a019
Create Date: 2014-11-03 19:31:51

"""

# revision identifiers, used by Alembic.
revision = '0028_ae3419a9'
down_revision = '0027_e139a019'

from alembic import context, op
import sqlalchemy as sa

# Zato
from zato.common import HTTP_SOAP_SERIALIZATION_TYPE, MISC, MSG_PATTERN_TYPE
from zato.common.odb import model

sa_url = context.config.get_section('alembic').get('sqlalchemy.url')
engine = sa.create_engine(sa_url)

pubapi_sec_id = list(engine.execute("SELECT id FROM sec_base WHERE name='pubapi'"))[0][0]
cluster_id = list(engine.execute('SELECT id FROM cluster'))[0][0]

diff = (
    ('zato.cloud.aws.s3.create', 'zato.server.service.internal.cloud.aws.s3.Create'),
    ('zato.cloud.aws.s3.create.json', 'zato.server.service.internal.cloud.aws.s3.Create'),
    ('zato.cloud.aws.s3.delete', 'zato.server.service.internal.cloud.aws.s3.Delete'),
    ('zato.cloud.aws.s3.delete.json', 'zato.server.service.internal.cloud.aws.s3.Delete'),
    ('zato.cloud.aws.s3.edit', 'zato.server.service.internal.cloud.aws.s3.Edit'),
    ('zato.cloud.aws.s3.edit.json', 'zato.server.service.internal.cloud.aws.s3.Edit'),
    ('zato.cloud.aws.s3.get-list', 'zato.server.service.internal.cloud.aws.s3.GetList'),
    ('zato.cloud.aws.s3.get-list.json', 'zato.server.service.internal.cloud.aws.s3.GetList'),
    ('zato.cloud.openstack.swift.create', 'zato.server.service.internal.cloud.openstack.swift.Create'),
    ('zato.cloud.openstack.swift.create.json', 'zato.server.service.internal.cloud.openstack.swift.Create'),
    ('zato.cloud.openstack.swift.delete', 'zato.server.service.internal.cloud.openstack.swift.Delete'),
    ('zato.cloud.openstack.swift.delete.json', 'zato.server.service.internal.cloud.openstack.swift.Delete'),
    ('zato.cloud.openstack.swift.edit', 'zato.server.service.internal.cloud.openstack.swift.Edit'),
    ('zato.cloud.openstack.swift.edit.json', 'zato.server.service.internal.cloud.openstack.swift.Edit'),
    ('zato.cloud.openstack.swift.get-list', 'zato.server.service.internal.cloud.openstack.swift.GetList'),
    ('zato.cloud.openstack.swift.get-list.json', 'zato.server.service.internal.cloud.openstack.swift.GetList'),
    ('zato.definition.cassandra.create', 'zato.server.service.internal.definition.cassandra.Create'),
    ('zato.definition.cassandra.create.json', 'zato.server.service.internal.definition.cassandra.Create'),
    ('zato.definition.cassandra.delete', 'zato.server.service.internal.definition.cassandra.Delete'),
    ('zato.definition.cassandra.delete.json', 'zato.server.service.internal.definition.cassandra.Delete'),
    ('zato.definition.cassandra.edit', 'zato.server.service.internal.definition.cassandra.Edit'),
    ('zato.definition.cassandra.edit.json', 'zato.server.service.internal.definition.cassandra.Edit'),
    ('zato.definition.cassandra.get-by-id', 'zato.server.service.internal.definition.cassandra.GetByID'),
    ('zato.definition.cassandra.get-by-id.json', 'zato.server.service.internal.definition.cassandra.GetByID'),
    ('zato.definition.cassandra.get-list', 'zato.server.service.internal.definition.cassandra.GetList'),
    ('zato.definition.cassandra.get-list.json', 'zato.server.service.internal.definition.cassandra.GetList'),
    ('zato.info.get-info', 'zato.server.service.internal.info.GetInfo'),
    ('zato.info.get-info.json', 'zato.server.service.internal.info.GetInfo'),
    ('zato.info.get-server-info', 'zato.server.service.internal.info.GetServerInfo'),
    ('zato.info.get-server-info.json', 'zato.server.service.internal.info.GetServerInfo'),
    ('zato.security.apikey.change-password', 'zato.server.service.internal.security.apikey.ChangePassword'),
    ('zato.security.apikey.change-password.json', 'zato.server.service.internal.security.apikey.ChangePassword'),
    ('zato.security.apikey.create', 'zato.server.service.internal.security.apikey.Create'),
    ('zato.security.apikey.create.json', 'zato.server.service.internal.security.apikey.Create'),
    ('zato.security.apikey.delete', 'zato.server.service.internal.security.apikey.Delete'),
    ('zato.security.apikey.delete.json', 'zato.server.service.internal.security.apikey.Delete'),
    ('zato.security.apikey.edit', 'zato.server.service.internal.security.apikey.Edit'),
    ('zato.security.apikey.edit.json', 'zato.server.service.internal.security.apikey.Edit'),
    ('zato.security.apikey.get-list', 'zato.server.service.internal.security.apikey.GetList'),
    ('zato.security.apikey.get-list.json', 'zato.server.service.internal.security.apikey.GetList'),
    ('zato.security.aws.change-password', 'zato.server.service.internal.security.aws.ChangePassword'),
    ('zato.security.aws.change-password.json', 'zato.server.service.internal.security.aws.ChangePassword'),
    ('zato.security.aws.create', 'zato.server.service.internal.security.aws.Create'),
    ('zato.security.aws.create.json', 'zato.server.service.internal.security.aws.Create'),
    ('zato.security.aws.delete', 'zato.server.service.internal.security.aws.Delete'),
    ('zato.security.aws.delete.json', 'zato.server.service.internal.security.aws.Delete'),
    ('zato.security.aws.edit', 'zato.server.service.internal.security.aws.Edit'),
    ('zato.security.aws.edit.json', 'zato.server.service.internal.security.aws.Edit'),
    ('zato.security.aws.get-list', 'zato.server.service.internal.security.aws.GetList'),
    ('zato.security.aws.get-list.json', 'zato.server.service.internal.security.aws.GetList'),
    ('zato.security.ntlm.change-password', 'zato.server.service.internal.security.ntlm.ChangePassword'),
    ('zato.security.ntlm.change-password.json', 'zato.server.service.internal.security.ntlm.ChangePassword'),
    ('zato.security.ntlm.create', 'zato.server.service.internal.security.ntlm.Create'),
    ('zato.security.ntlm.create.json', 'zato.server.service.internal.security.ntlm.Create'),
    ('zato.security.ntlm.delete', 'zato.server.service.internal.security.ntlm.Delete'),
    ('zato.security.ntlm.delete.json', 'zato.server.service.internal.security.ntlm.Delete'),
    ('zato.security.ntlm.edit', 'zato.server.service.internal.security.ntlm.Edit'),
    ('zato.security.ntlm.edit.json', 'zato.server.service.internal.security.ntlm.Edit'),
    ('zato.security.ntlm.get-list', 'zato.server.service.internal.security.ntlm.GetList'),
    ('zato.security.ntlm.get-list.json', 'zato.server.service.internal.security.ntlm.GetList'),
    ('zato.security.openstack.change-password', 'zato.server.service.internal.security.openstack.ChangePassword'),
    ('zato.security.openstack.change-password.json', 'zato.server.service.internal.security.openstack.ChangePassword'),
    ('zato.security.openstack.create', 'zato.server.service.internal.security.openstack.Create'),
    ('zato.security.openstack.create.json', 'zato.server.service.internal.security.openstack.Create'),
    ('zato.security.openstack.delete', 'zato.server.service.internal.security.openstack.Delete'),
    ('zato.security.openstack.delete.json', 'zato.server.service.internal.security.openstack.Delete'),
    ('zato.security.openstack.get-list', 'zato.server.service.internal.security.openstack.GetList'),
    ('zato.security.openstack.get-list.json', 'zato.server.service.internal.security.openstack.GetList'),
    ('zato.security.rbac.client_role.create', 'zato.server.service.internal.security.rbac.client_role.Create'),
    ('zato.security.rbac.client_role.create.json', 'zato.server.service.internal.security.rbac.client_role.Create'),
    ('zato.security.rbac.client_role.delete', 'zato.server.service.internal.security.rbac.client_role.Delete'),
    ('zato.security.rbac.client_role.delete.json', 'zato.server.service.internal.security.rbac.client_role.Delete'),
    ('zato.security.rbac.client_role.get-list', 'zato.server.service.internal.security.rbac.client_role.get-list'),
    ('zato.security.rbac.client_role.get-list.json', 'zato.server.service.internal.security.rbac.client_role.get-list'),
    ('zato.security.rbac.permission.create', 'zato.server.service.internal.security.rbac.permission.Create'),
    ('zato.security.rbac.permission.create.json', 'zato.server.service.internal.security.rbac.permission.Create'),
    ('zato.security.rbac.permission.delete', 'zato.server.service.internal.security.rbac.permission.Delete'),
    ('zato.security.rbac.permission.delete.json', 'zato.server.service.internal.security.rbac.permission.Delete'),
    ('zato.security.rbac.permission.edit', 'zato.server.service.internal.security.rbac.permission.Edit'),
    ('zato.security.rbac.permission.edit.json', 'zato.server.service.internal.security.rbac.permission.Edit'),
    ('zato.security.rbac.permission.get-list', 'zato.server.service.internal.security.rbac.permission.get-list'),
    ('zato.security.rbac.permission.get-list.json', 'zato.server.service.internal.security.rbac.permission.get-list'),
    ('zato.security.rbac.role.create', 'zato.server.service.internal.security.rbac.role.Create'),
    ('zato.security.rbac.role.create.json', 'zato.server.service.internal.security.rbac.role.Create'),
    ('zato.security.rbac.role.delete', 'zato.server.service.internal.security.rbac.role.Delete'),
    ('zato.security.rbac.role.delete.json', 'zato.server.service.internal.security.rbac.role.Delete'),
    ('zato.security.rbac.role.edit', 'zato.server.service.internal.security.rbac.role.Edit'),
    ('zato.security.rbac.role.edit.json', 'zato.server.service.internal.security.rbac.role.Edit'),
    ('zato.security.rbac.role.get-list', 'zato.server.service.internal.security.rbac.role.get-list'),
    ('zato.security.rbac.role.get-list.json', 'zato.server.service.internal.security.rbac.role.get-list'),
    ('zato.security.rbac.role_permission.create', 'zato.server.service.internal.security.rbac.role_permission.Create'),
    ('zato.security.rbac.role_permission.create.json', 'zato.server.service.internal.security.rbac.role_permission.Create'),
    ('zato.security.rbac.role_permission.delete', 'zato.server.service.internal.security.rbac.role_permission.Delete'),
    ('zato.security.rbac.role_permission.delete.json', 'zato.server.service.internal.security.rbac.role_permission.Delete'),
    ('zato.security.rbac.role_permission.get-list', 'zato.server.service.internal.security.rbac.role_permission.get-list'),
    ('zato.security.rbac.role_permission.get-list.json', 'zato.server.service.internal.security.rbac.role_permission.get-list'),
    ('zato.security.xpath.change-password', 'zato.server.service.internal.security.xpath.ChangePassword'),
    ('zato.security.xpath.change-password.json', 'zato.server.service.internal.security.xpath.ChangePassword'),
    ('zato.security.xpath.create', 'zato.server.service.internal.security.xpath.Create'),
    ('zato.security.xpath.create.json', 'zato.server.service.internal.security.xpath.Create'),
    ('zato.security.xpath.delete', 'zato.server.service.internal.security.xpath.Delete'),
    ('zato.security.xpath.delete.json', 'zato.server.service.internal.security.xpath.Delete'),
    ('zato.security.xpath.edit', 'zato.server.service.internal.security.xpath.Edit'),
    ('zato.security.xpath.edit.json', 'zato.server.service.internal.security.xpath.Edit'),
    ('zato.security.xpath.get-list', 'zato.server.service.internal.security.xpath.GetList'),
    ('zato.security.xpath.get-list.json', 'zato.server.service.internal.security.xpath.GetList'),
)

def get_json_insert(name, service_id):
    return """
        INSERT INTO http_soap(name, service_id, security_id, is_active, is_internal,
            connection, transport, url_path, soap_action, data_format, cluster_id, audit_enabled,
            audit_back_log, audit_max_payload, audit_repl_patt_type, serialization_type, timeout, has_rbac)

        VALUES('{}', '{}', '{}', 1, 1,
            'channel', 'plain_http', '/zato/json/{}', '', 'json', '{}', 0,
            '{}', '{}', '{}',
            '{}', '{}', 0)

    """.format(name, service_id, pubapi_sec_id,
               name, cluster_id,
               MISC.DEFAULT_AUDIT_BACK_LOG, MISC.DEFAULT_AUDIT_MAX_PAYLOAD, MSG_PATTERN_TYPE.JSON_POINTER.id,
               HTTP_SOAP_SERIALIZATION_TYPE.STRING_VALUE.id, MISC.DEFAULT_HTTP_TIMEOUT)

def get_soap_insert(name, service_id):
    return """
        INSERT INTO http_soap(name, service_id, security_id, is_active, is_internal,
            connection, transport, url_path, soap_action, soap_version, data_format, cluster_id, audit_enabled,
            audit_back_log, audit_max_payload, audit_repl_patt_type, serialization_type, timeout, has_rbac)

        VALUES('{}', '{}', '{}', 1, 1,
            'channel', 'soap', '/zato/soap', '', '1.1', 'xml', '{}', 0,
            '{}', '{}', '{}',
            '{}', '{}', 0)

    """.format(name, service_id, pubapi_sec_id,
               cluster_id,
               MISC.DEFAULT_AUDIT_BACK_LOG, MISC.DEFAULT_AUDIT_MAX_PAYLOAD, MSG_PATTERN_TYPE.XPATH.id,
               HTTP_SOAP_SERIALIZATION_TYPE.SUDS.id, MISC.DEFAULT_HTTP_TIMEOUT)

def upgrade():
    for name, impl_name in diff:
        service_id = list(engine.execute("SELECT id FROM service WHERE impl_name='{}'".format(impl_name)))[0][0]

        insert = (get_json_insert if 'json' in name else get_soap_insert)(name, service_id)
        engine.execute(insert)

def downgrade():
    for name, _ in diff:
        engine.execute("DELETE FROM http_soap WHERE name='{}'".format(name))
