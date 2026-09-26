"""add gift table

Revision ID: ff6ca4f001fc
Revises: 1a31ce608336
Create Date: 2026-09-26 17:49:55.299304

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = 'ff6ca4f001fc'
down_revision = '1a31ce608336'
branch_labels = None
depends_on = None


def upgrade():
    # The gift table was previously created out-of-band by
    # SQLModel.metadata.create_all and is not owned by any migration. Drop it
    # first (it carries no data) so a clean database and this one converge on
    # the same schema.
    op.execute("DROP TABLE IF EXISTS gift")
    op.create_table(
        "gift",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "name", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False
        ),
        sa.Column(
            "description",
            sqlmodel.sql.sqltypes.AutoString(length=255),
            nullable=True,
        ),
        sa.Column("approximate_price", sa.Float(), nullable=True),
        sa.Column(
            "photo_url", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True
        ),
        sa.Column(
            "product_link",
            sqlmodel.sql.sqltypes.AutoString(length=255),
            nullable=True,
        ),
        sa.Column("owner_id", sa.UUID(), nullable=False),
        sa.Column("reserved_by_id", sa.UUID(), nullable=True),
        sa.ForeignKeyConstraint(["owner_id"], ["user.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["reserved_by_id"], ["user.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    op.drop_table("gift")
