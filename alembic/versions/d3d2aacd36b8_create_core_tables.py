from alembic import op
import sqlalchemy as sa

revision = "0001_create_core"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        "users",
        sa.Column("id", sa.BigInteger, primary_key=True),
        sa.Column("email", sa.Text, nullable=False, unique=True),
        sa.Column("hashed_password", sa.Text, nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        schema="public",
    )

    op.create_table(
        "authors",
        sa.Column("id", sa.BigInteger, primary_key=True),
        sa.Column("name", sa.Text, nullable=False, unique=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        schema="public",
    )

    op.create_table(
        "books",
        sa.Column("id", sa.BigInteger, primary_key=True),
        sa.Column("title", sa.Text, nullable=False),
        sa.Column("author_id", sa.BigInteger, sa.ForeignKey("public.authors.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("genre", sa.Text, nullable=False),
        sa.Column("published_year", sa.Integer, nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.CheckConstraint("genre IN ('Fiction','Non-Fiction','Science','History')", name="books_genre_check"),
        sa.CheckConstraint("published_year BETWEEN 1800 AND EXTRACT(YEAR FROM CURRENT_DATE)::INT", name="books_year_check"),
        schema="public",
    )

    # Індекси
    op.create_index("idx_books_lower_title", "books", [sa.text("lower(title)")], schema="public")
    op.create_index("idx_authors_lower_name", "authors", [sa.text("lower(name)")], schema="public")
    op.create_index("idx_books_published_year", "books", ["published_year"], schema="public")
    op.create_index("idx_books_author_id", "books", ["author_id"], schema="public")

    # Функція author_get_or_create
    op.execute("""
    CREATE OR REPLACE FUNCTION public.author_get_or_create(p_name TEXT)
    RETURNS BIGINT AS $$
    DECLARE v_id BIGINT;
    BEGIN
        SELECT id INTO v_id FROM public.authors WHERE lower(name) = lower(trim(p_name));
        IF v_id IS NOT NULL THEN
            RETURN v_id;
        END IF;
        INSERT INTO public.authors(name) VALUES (trim(p_name)) RETURNING id INTO v_id;
        RETURN v_id;
    END;
    $$ LANGUAGE plpgsql;
    """)

def downgrade():
    op.execute("DROP FUNCTION IF EXISTS public.author_get_or_create(TEXT)")
    op.drop_index("idx_books_author_id", table_name="books", schema="public")
    op.drop_index("idx_books_published_year", table_name="books", schema="public")
    op.drop_index("idx_authors_lower_name", table_name="authors", schema="public")
    op.drop_index("idx_books_lower_title", table_name="books", schema="public")
    op.drop_table("books", schema="public")
    op.drop_table("authors", schema="public")
    op.drop_table("users", schema="public")
