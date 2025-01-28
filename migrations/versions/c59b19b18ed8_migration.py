"""migration

Revision ID: c59b19b18ed8
Revises: 
Create Date: 2025-01-28 00:39:17.377562

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from src.shared .db.pg_sqlalchemy.connection import BaseSqlModel


# revision identifiers, used by Alembic.
revision: str = 'c59b19b18ed8'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('students', sa.Column('contact_id', sa.String(), nullable=False))
    op.create_unique_constraint(None, 'students', ['contact_id'])
    op.create_foreign_key(None, 'students', 'contacts', ['contact_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'students', type_='foreignkey')
    op.drop_constraint(None, 'students', type_='unique')
    op.drop_column('students', 'contact_id')
    # ### end Alembic commands ###
