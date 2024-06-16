"""auth-history

Revision ID: 248b576f9bd4
Revises: 92e0bece0dd9
Create Date: 2024-06-16 14:57:58.546189

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '248b576f9bd4'
down_revision: Union[str, None] = '92e0bece0dd9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_authentication_histories_id', table_name='authentication_histories')
    op.create_unique_constraint(None, 'authentication_histories', ['id', 'user_id'])
    op.create_unique_constraint(None, 'oauth_account', ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'oauth_account', type_='unique')
    op.drop_constraint(None, 'authentication_histories', type_='unique')
    op.create_index('ix_authentication_histories_id', 'authentication_histories', ['id'], unique=True)
    # ### end Alembic commands ###
