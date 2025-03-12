"""create account table

Revision ID: a12140cd0373
Revises: ef1dcb0ae1e1
Create Date: 2025-03-12 06:09:16.983222

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a12140cd0373"
down_revision: Union[str, None] = "ef1dcb0ae1e1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
