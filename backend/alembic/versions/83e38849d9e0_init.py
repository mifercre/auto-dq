"""init

Revision ID: 83e38849d9e0
Revises: 
Create Date: 2021-04-07 08:19:21.169098

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy_utils import EncryptedType

# revision identifiers, used by Alembic.
revision = '83e38849d9e0'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('db',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('hostname', sa.String(), nullable=True),
        sa.Column('port', sa.Integer(), nullable=True),
        sa.Column('database', sa.String(), nullable=True),
        sa.Column('username', sa.String(), nullable=True),
        sa.Column('password', EncryptedType(), nullable=True),
        sa.Column('blacklist', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_db_id'), 'db', ['id'], unique=False)
    op.create_table('dbschema',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('database_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['database_id'], ['db.id'], name='dbschema_database_id_fkey'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_dbschema_id'), 'dbschema', ['id'], unique=False)
    op.create_table('dbtable',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('schema_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['schema_id'], ['dbschema.id'], name='dbtable_schema_id_fkey'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name', 'schema_id', name='unique_table_name_schema_id')
    )
    op.create_index(op.f('ix_dbtable_id'), 'dbtable', ['id'], unique=False)
    op.create_index(op.f('ix_dbtable_schema_id'), 'dbtable', ['schema_id'], unique=False)
    op.create_table('dbcolumn',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('type', sa.String(), nullable=True),
        sa.Column('is_partition_column', sa.Boolean(), nullable=True),
        sa.Column('table_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['table_id'], ['dbtable.id'], name='dbcolumn_table_id_fkey'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name', 'table_id', name='unique_column_name_table_id')
    )
    op.create_index(op.f('ix_dbcolumn_id'), 'dbcolumn', ['id'], unique=False)
    op.create_index(op.f('ix_dbcolumn_table_id'), 'dbcolumn', ['table_id'], unique=False)
    op.create_table('dbtablepartition',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('table_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['table_id'], ['dbtable.id'], name='dbtablepartition_table_id_fkey'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_dbtablepartition_id'), 'dbtablepartition', ['id'], unique=False)
    op.create_index(op.f('ix_dbtablepartition_table_id'), 'dbtablepartition', ['table_id'], unique=False)
    op.create_table('check',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('schedule', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('active', sa.Boolean(), nullable=True),
        sa.Column('check_class', sa.String(), nullable=True),
        sa.Column('database_id', sa.Integer(), nullable=False),
        sa.Column('type', sa.String(), nullable=True),
        sa.Column('source', sa.String(), nullable=True),
        sa.Column('false_positives', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('delta_threshold_seconds', sa.Integer(), nullable=True),
        sa.Column('schema_id', sa.Integer(), nullable=True),
        sa.Column('table_id', sa.Integer(), nullable=True),
        sa.Column('column_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['column_id'], ['dbcolumn.id'], name='check_column_id_fkey'),
        sa.ForeignKeyConstraint(['database_id'], ['db.id'], name='check_database_id_fkey'),
        sa.ForeignKeyConstraint(['schema_id'], ['dbschema.id'], name='check_schema_id_fkey'),
        sa.ForeignKeyConstraint(['table_id'], ['dbtable.id'], name='check_table_id_fkey'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_check_id'), 'check', ['id'], unique=False)
    op.create_table('checkexecution',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('exec_time', sa.TIMESTAMP(), nullable=False),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('results', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('logs', sa.Text(), nullable=True),
        sa.Column('check_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['check_id'], ['check.id'], name='checkexecution_check_id_fkey'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_checkexecution_id'), 'checkexecution', ['id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_checkexecution_id'), table_name='checkexecution')
    op.drop_table('checkexecution')
    op.drop_index(op.f('ix_check_id'), table_name='check')
    op.drop_table('check')
    op.drop_index(op.f('ix_dbtablepartition_table_id'), table_name='dbtablepartition')
    op.drop_index(op.f('ix_dbtablepartition_id'), table_name='dbtablepartition')
    op.drop_table('dbtablepartition')
    op.drop_index(op.f('ix_dbcolumn_table_id'), table_name='dbcolumn')
    op.drop_index(op.f('ix_dbcolumn_id'), table_name='dbcolumn')
    op.drop_table('dbcolumn')
    op.drop_index(op.f('ix_dbtable_schema_id'), table_name='dbtable')
    op.drop_index(op.f('ix_dbtable_id'), table_name='dbtable')
    op.drop_table('dbtable')
    op.drop_index(op.f('ix_dbschema_id'), table_name='dbschema')
    op.drop_table('dbschema')
    op.drop_index(op.f('ix_db_id'), table_name='db')
    op.drop_table('db')
