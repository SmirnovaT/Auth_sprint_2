"""partitional-table

Revision ID: 2673d5d0dc6f
Revises: 248b576f9bd4
Create Date: 2024-06-16 14:58:58.957060

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '2673d5d0dc6f'
down_revision: Union[str, None] = '248b576f9bd4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('authentication_histories_hash',
                    sa.Column('id', sa.UUID(), nullable=False, comment='Идентификатор аутентификации'),
                    sa.Column('success', sa.Boolean(), nullable=False,
                              comment='Флаг, указывающий, был ли вход успешным (True) или нет (False)'),
                    sa.Column('user_agent', sa.String(), nullable=True,
                              comment='Информация о браузере и операционной системе пользователя'),
                    sa.Column('user_id', sa.UUID(), nullable=False,
                              comment='Идентификатор пользователя, связанного с этой записью о входе'),
                    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True,
                              comment='Дата создания записи'),
                    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True,
                              comment='Дата обновления записи'),
                    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
                    sa.UniqueConstraint('id', 'user_id'),

                    comment='История аутентификации пользователей',
                    postgresql_partition_by='HASH (user_id)'
                    )

    op.execute("""CREATE TABLE authentication_histories_000 PARTITION OF 
        authentication_histories_hash FOR VALUES WITH (MODULUS 4, REMAINDER 0);""")

    op.execute("""CREATE TABLE authentication_histories_001 PARTITION OF 
        authentication_histories_hash FOR VALUES WITH (MODULUS 4, REMAINDER 1);""")

    op.execute("""CREATE TABLE authentication_histories_002 PARTITION OF 
        authentication_histories_hash FOR VALUES WITH (MODULUS 4, REMAINDER 2);""")

    op.execute("""CREATE TABLE authentication_histories_003 PARTITION OF 
        authentication_histories_hash FOR VALUES WITH (MODULUS 4, REMAINDER 3);""")

    op.execute("""INSERT INTO authentication_histories_hash 
        SELECT * FROM authentication_histories""")

    op.drop_table('authentication_histories')
    op.rename_table('authentication_histories_hash', 'authentication_histories')


def downgrade() -> None:
    op.drop_table('authentication_histories_000')
    op.drop_table('authentication_histories_001')
    op.drop_table('authentication_histories_002')
    op.drop_table('authentication_histories_003')
