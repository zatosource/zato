"""mass update_2 0014

Revision ID: 0014_50465d9c19e0
Revises: 0013_6e651e7a3c38
Create Date: 2014-07-08 10:14:32

"""

# revision identifiers, used by Alembic.
revision = '0014_50465d9c19e0'
down_revision = '0013_6e651e7a3c38'

from alembic import op, context
import sqlalchemy as sa
from sqlalchemy.schema import CreateSequence, DropSequence

# Zato
from zato.common.odb import model
from zato.common import CLOUD

# ################################################################################################################################

def is_postgresql():
    config = context.config.get_section('alembic')
    return config.get('sqlalchemy.url').startswith('postgresa')

def upgrade():
    op.drop_constraint('http_soap_url_path_connection_soap_action_cluster_id_key', model.HTTPSOAP.__tablename__)
    op.execute(CreateSequence(sa.Sequence('conn_def_cassandra_seq')))
    op.execute(CreateSequence(sa.Sequence('django_openid_auth_association_id_seq')))
    op.execute(CreateSequence(sa.Sequence('django_openid_auth_nonce_id_seq')))
    op.execute(CreateSequence(sa.Sequence('django_openid_auth_useropenid_id_seq')))
    op.execute(CreateSequence(sa.Sequence('query_cassandra_seq')))
    op.execute(CreateSequence(sa.Sequence('search_es_seq')))
    
    op.create_table(
        'django_openid_auth_association',
        sa.Column('id', sa.INTEGER(), server_default=sa.text("nextval('django_openid_auth_association_id_seq'::regclass)"), nullable=False),
        sa.Column('server_url', sa.Text(), nullable=False),
        sa.Column('handle', sa.String(255), nullable=False),
        sa.Column('secret', sa.Text(), nullable=False),
        sa.Column('issued', sa.Integer(), nullable=False),
        sa.Column('lifetime', sa.Integer(), nullable=False),
        sa.Column('assoc_type', sa.Text(), nullable=False),
        )
    op.create_primary_key('django_openid_auth_association_pkey', 'django_openid_auth_association', ['id'])
        
    op.create_table(
        'django_openid_auth_nonce',
        sa.Column('id', sa.INTEGER(), server_default=sa.text("nextval('django_openid_auth_nonce_id_seq'::regclass)"), nullable=False),
        sa.Column('server_url', sa.String(2047), nullable=False),
        sa.Column('timestamp', sa.Integer(), nullable=False),
        sa.Column('salt', sa.String(40), nullable=False),
        )
    op.create_primary_key('django_openid_auth_nonce_pkey', 'django_openid_auth_nonce', ['id'])
    
    op.create_table(
        'django_openid_auth_useropenid',
        sa.Column('id', sa.INTEGER(), server_default=sa.text("nextval('django_openid_auth_useropenid_id_seq'::regclass)"), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('claimed_id', sa.String(255), nullable=False),
        sa.Column('display_id', sa.Text(), nullable=False),
        )
    op.create_primary_key('django_openid_auth_useropenid_pkey', 'django_openid_auth_useropenid', ['id'])
        
    op.create_table(
        model.Notification.__tablename__,
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('notif_type', sa.String(45), nullable=False),
        sa.Column('interval', sa.Integer(), nullable=False),
        sa.Column('name_pattern', sa.String(2000), nullable=False),
        sa.Column('name_pattern_neg', sa.Boolean(), nullable=False),
        sa.Column('get_data', sa.Boolean(), nullable=False),
        sa.Column('get_data_patt', sa.String(2000), nullable=False),
        sa.Column('get_data_patt_neg', sa.Boolean(), nullable=False),
        sa.Column('service_id', sa.Integer(), nullable=False),
        sa.Column('cluster_id', sa.Integer(), nullable=False),
        )
    op.create_primary_key('notif_pkey', model.Notification.__tablename__, ['id'])
        
    op.create_table(
        model.NotificationOpenStackSwift.__tablename__,
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('containers', sa.String(20000), nullable=False),
        sa.Column('def_id', sa.Integer(), nullable=False)
        )
    op.create_primary_key('notif_os_swift_pkey', model.NotificationOpenStackSwift.__tablename__, ['id', 'def_id'])
        
    op.create_table(
        model.ElasticSearch.__tablename__,
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('hosts', sa.String(400), nullable=False),
        sa.Column('timeout', sa.Integer(), nullable=False),
        sa.Column('body_as', sa.String(45), nullable=False),
        sa.Column('cluster_id', sa.Integer(), nullable=False)
        )
    op.create_primary_key('search_es_pkey', model.ElasticSearch.__tablename__, ['id'])
        
    op.create_table(
        model.OpenStackSecurity.__tablename__,
        sa.Column('id', sa.Integer, nullable=False)
        )
    op.create_primary_key('sec_openstack_pkey', model.OpenStackSecurity.__tablename__, ['id'])
        
    op.add_column(
        model.OpenStackSwift.__tablename__, sa.Column('pool_size', sa.Integer(), nullable=False, \
            default=CLOUD.OPENSTACK.SWIFT.DEFAULTS.POOL_SIZE)
        )
    
    op.create_unique_constraint(
        'conn_def_cassandra_name_cluster_id_key', 'conn_def_cassandra', ['name', 'cluster_id']
        )
        
    op.create_unique_constraint(
        'django_openid_auth_useropenid_claimed_id_key', 'django_openid_auth_useropenid', ['claimed_id']
        )
        
    op.create_foreign_key(
        'django_openid_auth_useropenid_user_id_fkey', 'django_openid_auth_useropenid', 'auth_user', ['user_id'], ['id'], \
         deferrable=True, initially='DEFERRED'
        )
        
    op.create_foreign_key('notif_cluster_id_fkey', model.Notification.__tablename__, 'cluster', ['cluster_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('notif_service_id_fkey', model.Notification.__tablename__, 'service', ['service_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('notif_os_swift_def_id_fkey', model.NotificationOpenStackSwift.__tablename__, 'os_swift', ['def_id'], ['id'])
    op.create_foreign_key('notif_os_swift_id_fkey', model.NotificationOpenStackSwift.__tablename__, model.Notification.__tablename__, \
        ['id'], ['id'])
    op.create_foreign_key('search_es_cluster_id_fkey', model.ElasticSearch.__tablename__, 'cluster', ['cluster_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('sec_openstack_id_fkey', model.OpenStackSecurity.__tablename__, 'sec_base', ['id'], ['id'])
    op.create_unique_constraint('http_soap_url_path_host_connection_soap_action_cluster_id_key', model.HTTPSOAP.__tablename__, \
        ['url_path', 'host', 'connection', 'soap_action', 'cluster_id'])
    
    op.create_unique_constraint('notif_name_cluster_id_key', model.Notification.__tablename__, ['name', 'cluster_id'])
    op.create_unique_constraint('query_cassandra_name_cluster_id_key', 'query_cassandra', ['name', 'cluster_id'])
    op.create_unique_constraint('search_es_name_cluster_id_key', model.ElasticSearch.__tablename__, ['name', 'cluster_id'])
    op.create_index('django_openid_auth_useropenid_user_id', 'django_openid_auth_useropenid', ['user_id'])
    
    op.create_primary_key('alembic_version_pkey', 'alembic_version', ['version_num'])
    
    if is_postgresql():
        op.execute(
            '''ALTER TABLE django_openid_auth_association ALTER COLUMN id SET DEFAULT nextval
            (\'django_openid_auth_association_id_seq\'::regclass)'''
            )
        op.execute(
            '''ALTER TABLE django_openid_auth_nonce ALTER COLUMN id SET DEFAULT nextval
            (\'django_openid_auth_nonce_id_seq\'::regclass)'''
            )
        op.execute(
            '''ALTER TABLE django_openid_auth_useropenid ALTER COLUMN id SET DEFAULT nextval
            (\'django_openid_auth_useropenid_id_seq\'::regclass)'''
            )
     
          
def downgrade():
    op.create_unique_constraint(
        'http_soap_url_path_connection_soap_action_cluster_id_key', model.HTTPSOAP.__tablename__, \
        ['url_path', 'connection', 'soap_action', 'cluster_id']
        )
    op.drop_table('django_openid_auth_association')
    op.drop_table('django_openid_auth_nonce')
    op.drop_table('django_openid_auth_useropenid')
    op.drop_table(model.NotificationOpenStackSwift.__tablename__)
    op.drop_table(model.Notification.__tablename__)
    op.drop_table(model.ElasticSearch.__tablename__)
    op.drop_table(model.OpenStackSecurity.__tablename__)
    op.drop_column(model.OpenStackSwift.__tablename__, 'pool_size')
    op.execute(DropSequence(sa.Sequence('conn_def_cassandra_seq')))
    op.execute(DropSequence(sa.Sequence('django_openid_auth_association_id_seq')))
    op.execute(DropSequence(sa.Sequence('django_openid_auth_nonce_id_seq')))
    op.execute(DropSequence(sa.Sequence('django_openid_auth_useropenid_id_seq')))
    op.execute(DropSequence(sa.Sequence('query_cassandra_seq')))
    op.execute(DropSequence(sa.Sequence('search_es_seq')))
    op.drop_constraint('conn_def_cassandra_name_cluster_id_key', 'conn_def_cassandra')
    op.drop_constraint('http_soap_url_path_host_connection_soap_action_cluster_id_key', model.HTTPSOAP.__tablename__)
    op.drop_constraint('query_cassandra_name_cluster_id_key', 'query_cassandra')
    op.drop_constraint('alembic_version_pkey', 'alembic_version')
