"""add_user_id_and_created_at_to_messages

Revision ID: b3f2a1c8d9e0
Revises: 9e514feaaa08
Create Date: 2026-05-16 13:49:53.883000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'b3f2a1c8d9e0'
down_revision: Union[str, None] = '9e514feaaa08'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add user_id column
    op.add_column('messages', sa.Column('user_id', sa.Integer(), nullable=True))

    # Add created_at column
    op.add_column('messages', sa.Column('created_at', sa.DateTime(timezone=True), nullable=True))

    # Set default values for existing rows (SQLite compatible)
    op.execute("UPDATE messages SET user_id = 0 WHERE user_id IS NULL")
    op.execute("UPDATE messages SET created_at = datetime('now') WHERE created_at IS NULL")

    # Make columns non-nullable
    op.alter_column('messages', 'user_id', nullable=False)
    op.alter_column('messages', 'created_at', nullable=False)

    # Create index on user_id
    op.create_index(op.f('ix_messages_user_id'), 'messages', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_messages_user_id'), table_name='messages')
    op.drop_column('messages', 'created_at')
    op.drop_column('messages', 'user_id')
