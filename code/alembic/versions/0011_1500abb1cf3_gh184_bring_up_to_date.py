"""gh184 Bring Alembic migrations up to date

Revision ID: 0011_1500abb1cf3
Revises: 0010_3f03ae0ef253
Create Date: 2014-04-11 09:25:03.206296

"""

# revision identifiers, used by Alembic.
revision = '0011_1500abb1cf3'
down_revision = '0010_3f03ae0ef253'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.schema import CreateSequence, DropSequence

# Zato
from zato.common.odb import model
from zato.common import CLOUD, HTTP_SOAP_SERIALIZATION_TYPE, MISC, PUB_SUB

# ################################################################################################################################

add_col = op.add_column

def alter_column_nullable_false(table_name, column_name, default_value, column_type):
    column = sa.sql.table(table_name, sa.sql.column(column_name))
    op.execute(column.update().values({column_name:default_value}))
    op.alter_column(table_name, column_name, type_=column_type, existing_type=column_type, nullable=False)

def upgrade():
    op.create_unique_constraint(
        'sec_base_cluster_id_username_sec_type_key', model.SecurityBase.__tablename__, ['cluster_id', 'username', 'sec_type'])

    op.create_table(
        model.NTLM.__tablename__,sa.Column('id', sa.Integer(), sa.ForeignKey('sec_base.id'), primary_key=True)
        )

    op.create_table(
        model.APIKeySecurity.__tablename__,sa.Column('id', sa.Integer(), sa.ForeignKey('sec_base.id'), primary_key=True)
        )

    op.create_table(
        model.XPathSecurity.__tablename__,
        sa.Column('id', sa.Integer(), sa.ForeignKey('sec_base.id'), primary_key=True),
        sa.Column('username_expr', sa.String(200), nullable=False),
        sa.Column('password_expr', sa.String(200), nullable=True),
        )
                                                   
    add_col(
        model.HTTPSOAP.__tablename__, sa.Column('serialization_type', sa.String(200), nullable=True))
    alter_column_nullable_false(
            model.HTTPSOAP.__tablename__, 'serialization_type', HTTP_SOAP_SERIALIZATION_TYPE.SUDS.id, sa.String(200))

    add_col(
        model.HTTPSOAP.__tablename__, sa.Column('timeout', sa.Integer(), nullable=True))
    alter_column_nullable_false(
            model.HTTPSOAP.__tablename__, 'timeout', MISC.DEFAULT_HTTP_TIMEOUT, sa.Integer())

    op.create_table(
        model.AWSSecurity.__tablename__, sa.Column('id', sa.Integer(), sa.ForeignKey('sec_base.id'), primary_key=True))

    op.execute(CreateSequence(sa.Sequence('deliv_def_seq')))

    op.execute(CreateSequence(sa.Sequence('deliv_seq')))

    op.execute(CreateSequence(sa.Sequence('deliv_payl_seq')))

    op.execute(CreateSequence(sa.Sequence('msg_ns_seq')))
    
    op.execute(CreateSequence(sa.Sequence('http_soap_audit_seq')))
    op.create_table(
        model.HTTSOAPAudit.__tablename__,
        sa.Column('id', sa.Integer(), sa.Sequence('http_soap_audit_seq'), primary_key=True),
        sa.Column('name', sa.String(200), nullable=False, index=True),
        sa.Column('cid', sa.String(200), nullable=False, index=True),
        sa.Column('transport', sa.String(200), nullable=False, index=True),
        sa.Column('connection', sa.String(200), nullable=False, index=True),
        sa.Column('req_time', sa.DateTime(), nullable=False),
        sa.Column('resp_time', sa.DateTime(), nullable=True),
        sa.Column('user_token', sa.String(200), nullable=True, index=True),
        sa.Column('invoke_ok', sa.Boolean, nullable=True),
        sa.Column('auth_ok', sa.Boolean, nullable=True),
        sa.Column('remote_addr', sa.String(200), nullable=False, index=True),
        sa.Column('req_headers', sa.LargeBinary(), nullable=True),
        sa.Column('req_payload', sa.LargeBinary(), nullable=True),
        sa.Column('resp_headers', sa.LargeBinary(), nullable=True),
        sa.Column('resp_payload', sa.LargeBinary(), nullable=True),
        sa.Column('cluster_id', sa.Integer(), sa.ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False),
        sa.Column('conn_id', sa.Integer(), sa.ForeignKey('http_soap.id', ondelete='CASCADE'), nullable=False),
        )

    op.execute(CreateSequence(sa.Sequence('htp_sp_ad_rpl_p_jp_seq')))    
    op.create_table(
        model.HTTSOAPAuditReplacePatternsJSONPointer.__tablename__,
        sa.Column('id', sa.Integer(), sa.Sequence('htp_sp_ad_rpl_p_jp_seq'), primary_key=True),
        sa.Column('conn_id', sa.Integer, sa.ForeignKey('http_soap.id', ondelete='CASCADE'), nullable=False),
        sa.Column('pattern_id', sa.Integer, sa.ForeignKey('msg_json_pointer.id', ondelete='CASCADE'), nullable=False),
        sa.Column('cluster_id', sa.Integer, sa.ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False),
        sa.UniqueConstraint('conn_id','pattern_id')
        )

    op.execute(CreateSequence(sa.Sequence('htp_sp_ad_rpl_p_xp_seq')))
    op.create_table(
        model.HTTSOAPAuditReplacePatternsXPath.__tablename__,
        sa.Column('id', sa.Integer(), sa.Sequence('htp_sp_ad_rpl_p_xp_seq'), primary_key=True),
        sa.Column('conn_id', sa.Integer(), sa.ForeignKey('http_soap.id', ondelete='CASCADE'), nullable=False),
        sa.Column('pattern_id', sa.Integer(), sa.ForeignKey('msg_xpath.id', ondelete='CASCADE'), nullable=False),
        sa.Column('cluster_id', sa.Integer(), sa.ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False),
        sa.UniqueConstraint('conn_id','pattern_id')
        )

    op.execute(CreateSequence(sa.Sequence('pub_sub_topic_seq')))
    op.create_table(
        model.PubSubTopic.__tablename__,
        sa.Column('id', sa.Integer(), sa.Sequence('pub_sub_topic_seq'), primary_key=True),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('is_active', sa.Boolean, nullable=False),
        sa.Column('max_depth', sa.Integer(), nullable=False),
        sa.Column('cluster_id', sa.Integer(), sa.ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False),
        sa.UniqueConstraint('name','cluster_id')
        )

    op.execute(CreateSequence(sa.Sequence('pub_sub_cons_seq')))
    op.create_table(
        model.PubSubConsumer.__tablename__,
        sa.Column('id', sa.Integer(), sa.Sequence('pub_sub_cons_seq'), primary_key=True),
        sa.Column('is_active', sa.Boolean, nullable=False),
        sa.Column('sub_key', sa.String(200), nullable=False),
        sa.Column('max_backlog', sa.Integer(), nullable=False),
        sa.Column('delivery_mode', sa.String(200), nullable=False),
        sa.Column('callback_id', sa.Integer(), sa.ForeignKey('http_soap.id', ondelete='CASCADE'), nullable=True),
        sa.Column('callback_type', sa.String(20), nullable=True, default=PUB_SUB.CALLBACK_TYPE.OUTCONN_PLAIN_HTTP),
        sa.Column('topic_id', sa.Integer(), sa.ForeignKey('pub_sub_topic.id', ondelete='CASCADE'), nullable=False),
        sa.Column('sec_def_id', sa.Integer(), sa.ForeignKey('sec_base.id', ondelete='CASCADE'), nullable=False),
        sa.Column('cluster_id', sa.Integer(), sa.ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False),
        sa.UniqueConstraint('sec_def_id','topic_id','cluster_id')
        )

    op.create_table(
        model.PubSubProducer.__tablename__,
        sa.Column('id', sa.Integer(), sa.Sequence('pub_sub_cons_seq'), primary_key=True),
        sa.Column('is_active', sa.Boolean, nullable=False),
        sa.Column('topic_id', sa.Integer(), sa.ForeignKey('pub_sub_topic.id', ondelete='CASCADE'), nullable=False),
        sa.Column('sec_def_id', sa.Integer(), sa.ForeignKey('sec_base.id', ondelete='CASCADE'), nullable=False),
        sa.Column('cluster_id', sa.Integer(), sa.ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False),
        sa.UniqueConstraint('sec_def_id','topic_id','cluster_id')
        )

    op.execute(CreateSequence(sa.Sequence('os_swift_seq')))
    op.create_table(
        model.OpenStackSwift.__tablename__,
        sa.Column('id', sa.Integer(), sa.Sequence('os_swift_seq'), primary_key=True),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('is_active', sa.Boolean, nullable=False),
        sa.Column('auth_url', sa.String(200), nullable=False),
        sa.Column('auth_version', sa.String(200), nullable=False, default=CLOUD.OPENSTACK.SWIFT.DEFAULTS.AUTH_VERSION),
        sa.Column('user', sa.String(200), nullable=True),
        sa.Column('key', sa.String(200), nullable=True),
        sa.Column('retries', sa.Integer, nullable=False, default=CLOUD.OPENSTACK.SWIFT.DEFAULTS.RETRIES),
        sa.Column('is_snet', sa.Boolean, nullable=False),
        sa.Column('starting_backoff', sa.Integer(), nullable=False, default=CLOUD.OPENSTACK.SWIFT.DEFAULTS.BACKOFF_STARTING),
        sa.Column('max_backoff', sa.Integer(), nullable=False, default=CLOUD.OPENSTACK.SWIFT.DEFAULTS.BACKOFF_MAX),
        sa.Column('tenant_name', sa.String(200), nullable=True),
        sa.Column('should_validate_cert', sa.Boolean, nullable=False),
        sa.Column('cacert', sa.String(200), nullable=True),
        sa.Column('should_retr_ratelimit', sa.Boolean, nullable=False),
        sa.Column('needs_tls_compr', sa.Boolean, nullable=False),
        sa.Column('custom_options', sa.String(2000), nullable=True),
        sa.Column('cluster_id', sa.Integer(), sa.ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False),
        sa.UniqueConstraint('name','cluster_id')
        )

    op.execute(CreateSequence(sa.Sequence('aws_s3_seq')))
    op.create_table(
        model.AWSS3.__tablename__,
        sa.Column('id', sa.Integer, sa.Sequence('aws_s3_seq'), primary_key=True),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('is_active', sa.Boolean, nullable=False),
        sa.Column('pool_size', sa.Integer(), nullable=False, default=CLOUD.AWS.S3.DEFAULTS.POOL_SIZE),
        sa.Column('address', sa.String(200), nullable=False, default=CLOUD.AWS.S3.DEFAULTS.ADDRESS),
        sa.Column('debug_level', sa.Integer, nullable=False, default=CLOUD.AWS.S3.DEFAULTS.DEBUG_LEVEL),
        sa.Column('suppr_cons_slashes', sa.Boolean, nullable=False, default=True),
        sa.Column('content_type', sa.String(200), nullable=False, default=CLOUD.AWS.S3.DEFAULTS.CONTENT_TYPE),
        sa.Column('metadata_', sa.String(2000), nullable=True),
        sa.Column('bucket', sa.String(2000), nullable=True),
        sa.Column('encrypt_at_rest', sa.Boolean, nullable=False, default=False),
        sa.Column('storage_class', sa.String(200), nullable=False, default=CLOUD.AWS.S3.STORAGE_CLASS.DEFAULT),
        sa.Column('security_id', sa.Integer(), sa.ForeignKey('sec_base.id', ondelete='CASCADE'), nullable=False),
        sa.Column('cluster_id', sa.Integer(), sa.ForeignKey('cluster.id', ondelete='CASCADE'), nullable=False),
        sa.UniqueConstraint('name','cluster_id')
        )

    op.alter_column(model.Cluster.__tablename__, 'odb_host', nullable=True)
    op.alter_column(model.Cluster.__tablename__, 'odb_port', nullable=True)
    op.alter_column(model.Cluster.__tablename__, 'odb_user', nullable=True)
    op.alter_column(model.Cluster.__tablename__, 'odb_db_name', nullable=True)

def downgrade():
    op.drop_constraint('sec_base_cluster_id_username_sec_type_key', model.SecurityBase.__tablename__)
    op.drop_table(model.NTLM.__tablename__)
    op.drop_table(model.AWSSecurity.__tablename__)
    op.drop_table(model.APIKeySecurity.__tablename__)
    op.drop_table(model.XPathSecurity.__tablename__)
    op.execute(DropSequence(sa.Sequence('deliv_payl_seq')))
    op.execute(DropSequence(sa.Sequence('msg_ns_seq')))
    op.drop_table(model.HTTSOAPAudit.__tablename__)
    op.execute(DropSequence(sa.Sequence('http_soap_audit_seq')))
    op.drop_table(model.HTTSOAPAuditReplacePatternsJSONPointer.__tablename__)
    op.execute(DropSequence(sa.Sequence('htp_sp_ad_rpl_p_jp_seq')))
    op.drop_table(model.HTTSOAPAuditReplacePatternsXPath.__tablename__)
    op.execute(DropSequence(sa.Sequence('htp_sp_ad_rpl_p_xp_seq')))
    op.drop_table(model.PubSubConsumer.__tablename__)
    op.execute(DropSequence(sa.Sequence('pub_sub_cons_seq')))
    op.drop_table(model.PubSubProducer.__tablename__)
    op.drop_table(model.OpenStackSwift.__tablename__)
    op.execute(DropSequence(sa.Sequence('os_swift_seq')))
    op.drop_table(model.AWSS3.__tablename__)
    op.execute(DropSequence(sa.Sequence('aws_s3_seq')))
    op.execute(DropSequence(sa.Sequence('deliv_seq')))
    op.drop_table(model.PubSubTopic.__tablename__)
    op.execute(DropSequence(sa.Sequence('pub_sub_topic_seq')))
    op.execute(DropSequence(sa.Sequence('deliv_def_seq')))
    op.drop_column(model.HTTPSOAP.__tablename__, 'serialization_type')
    op.drop_column(model.HTTPSOAP.__tablename__, 'timeout')

    op.alter_column(model.Cluster.__tablename__, 'odb_host', nullable=False)
    op.alter_column(model.Cluster.__tablename__, 'odb_port', nullable=False)
    op.alter_column(model.Cluster.__tablename__, 'odb_user', nullable=False)
    op.alter_column(model.Cluster.__tablename__, 'odb_db_name', nullable=False)
