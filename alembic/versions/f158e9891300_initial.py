"""initial

Revision ID: f158e9891300
Revises:
Create Date: 2026-01-22 22:28:13.379347

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f158e9891300"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("links", sa.Column("note1_id", sa.String(), nullable=False))
    op.add_column("links", sa.Column("note2_id", sa.String(), nullable=False))
    op.alter_column(
        "links", "id", existing_type=sa.TEXT(), type_=sa.String(), nullable=False
    )
    op.drop_column("links", "node2_id")
    op.drop_column("links", "node1_id")
    op.alter_column(
        "nodes", "id", existing_type=sa.TEXT(), type_=sa.String(), nullable=False
    )
    op.alter_column(
        "nodes", "x", existing_type=sa.INTEGER(), type_=sa.Float(), nullable=False
    )
    op.alter_column(
        "nodes", "y", existing_type=sa.INTEGER(), type_=sa.Float(), nullable=False
    )
    op.alter_column(
        "nodes", "color", existing_type=sa.TEXT(), type_=sa.String(), nullable=False
    )
    op.alter_column(
        "nodes",
        "text",
        existing_type=sa.TEXT(),
        type_=sa.String(),
        existing_nullable=False,
    )
    op.alter_column(
        "regions", "id", existing_type=sa.TEXT(), type_=sa.String(), nullable=False
    )
    op.alter_column(
        "regions", "x", existing_type=sa.INTEGER(), type_=sa.Float(), nullable=False
    )
    op.alter_column(
        "regions", "y", existing_type=sa.INTEGER(), type_=sa.Float(), nullable=False
    )
    op.alter_column(
        "regions",
        "height",
        existing_type=sa.INTEGER(),
        type_=sa.Float(),
        nullable=False,
    )
    op.alter_column(
        "regions", "width", existing_type=sa.INTEGER(), type_=sa.Float(), nullable=False
    )
    op.alter_column(
        "regions", "color", existing_type=sa.TEXT(), type_=sa.String(), nullable=False
    )
    op.alter_column(
        "regions",
        "name",
        existing_type=sa.TEXT(),
        type_=sa.String(),
        existing_nullable=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        "regions",
        "name",
        existing_type=sa.String(),
        type_=sa.TEXT(),
        existing_nullable=False,
    )
    op.alter_column(
        "regions", "color", existing_type=sa.String(), type_=sa.TEXT(), nullable=True
    )
    op.alter_column(
        "regions", "width", existing_type=sa.Float(), type_=sa.INTEGER(), nullable=True
    )
    op.alter_column(
        "regions", "height", existing_type=sa.Float(), type_=sa.INTEGER(), nullable=True
    )
    op.alter_column(
        "regions", "y", existing_type=sa.Float(), type_=sa.INTEGER(), nullable=True
    )
    op.alter_column(
        "regions", "x", existing_type=sa.Float(), type_=sa.INTEGER(), nullable=True
    )
    op.alter_column(
        "regions", "id", existing_type=sa.String(), type_=sa.TEXT(), nullable=True
    )
    op.alter_column(
        "nodes",
        "text",
        existing_type=sa.String(),
        type_=sa.TEXT(),
        existing_nullable=False,
    )
    op.alter_column(
        "nodes", "color", existing_type=sa.String(), type_=sa.TEXT(), nullable=True
    )
    op.alter_column(
        "nodes", "y", existing_type=sa.Float(), type_=sa.INTEGER(), nullable=True
    )
    op.alter_column(
        "nodes", "x", existing_type=sa.Float(), type_=sa.INTEGER(), nullable=True
    )
    op.alter_column(
        "nodes", "id", existing_type=sa.String(), type_=sa.TEXT(), nullable=True
    )
    op.add_column("links", sa.Column("node1_id", sa.INTEGER(), nullable=True))
    op.add_column("links", sa.Column("node2_id", sa.INTEGER(), nullable=True))
    op.alter_column(
        "links", "id", existing_type=sa.String(), type_=sa.TEXT(), nullable=True
    )
    op.drop_column("links", "note2_id")
    op.drop_column("links", "note1_id")
