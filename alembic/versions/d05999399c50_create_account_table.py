"""create account table

Revision ID: d05999399c50
Revises: 46a73302e6e1
Create Date: 2025-03-12 05:55:15.633962

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d05999399c50"
down_revision: Union[str, None] = "46a73302e6e1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
