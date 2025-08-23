from alembic import op

revision = "0001_create_core"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id BIGSERIAL PRIMARY KEY,
        email TEXT NOT NULL UNIQUE,
        hashed_password TEXT NOT NULL,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );
    """)

    op.execute("""
    CREATE TABLE IF NOT EXISTS authors (
        id BIGSERIAL PRIMARY KEY,
        name TEXT NOT NULL UNIQUE,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );
    """)

    op.execute("""
    CREATE TABLE IF NOT EXISTS books (
        id BIGSERIAL PRIMARY KEY,
        title TEXT NOT NULL,
        author_id BIGINT NOT NULL REFERENCES authors(id) ON DELETE RESTRICT,
        genre TEXT NOT NULL,
        published_year INT NOT NULL,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        CONSTRAINT books_genre_check CHECK (genre IN ('Fiction','Non-Fiction','Science','History')),
        CONSTRAINT books_year_check CHECK (published_year BETWEEN 1800 AND EXTRACT(YEAR FROM CURRENT_DATE)::INT)
    );

    -- для пошуку / сортування
    CREATE INDEX IF NOT EXISTS idx_books_lower_title ON books (lower(title));
    CREATE INDEX IF NOT EXISTS idx_authors_lower_name ON authors (lower(name));
    CREATE INDEX IF NOT EXISTS idx_books_published_year ON books (published_year);
    CREATE INDEX IF NOT EXISTS idx_books_author_id ON books (author_id);
    """)

    
    op.execute("""
    CREATE OR REPLACE FUNCTION author_get_or_create(p_name TEXT)
    RETURNS BIGINT
    LANGUAGE plpgsql
    AS $$
    DECLARE v_id BIGINT;
    BEGIN
        SELECT id INTO v_id FROM authors WHERE lower(name) = lower(trim(p_name));
        IF v_id IS NOT NULL THEN
            RETURN v_id;
        END IF;
        INSERT INTO authors(name) VALUES (trim(p_name)) RETURNING id INTO v_id;
        RETURN v_id;
    END; $$;
    """)

def downgrade():
    op.execute("DROP FUNCTION IF EXISTS author_get_or_create(TEXT);")
    op.execute("DROP TABLE IF EXISTS books;")
    op.execute("DROP TABLE IF EXISTS authors;")
    op.execute("DROP TABLE IF EXISTS users;")

