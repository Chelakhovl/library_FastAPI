from alembic import op
import sqlalchemy as sa

revision = "0002_dedupe_books"
down_revision = "0001_create_core"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "books",
        sa.Column("title_norm", sa.Text, sa.Computed("lower(title)", persisted=True)),
        schema="public",
    )
    op.create_index(
        "uniq_books_title_author_year",
        "books",
        ["title_norm", "author_id", "published_year"],
        unique=True,
        schema="public",
    )


def downgrade():
    op.drop_index("uniq_books_title_author_year", table_name="books", schema="public")
    op.drop_column("books", "title_norm", schema="public")
