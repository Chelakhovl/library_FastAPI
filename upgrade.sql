BEGIN;

CREATE TABLE public.alembic_version (
    version_num VARCHAR(32) NOT NULL, 
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

-- Running upgrade  -> 0001_create_core

CREATE TABLE public.users (
    id BIGSERIAL NOT NULL, 
    email TEXT NOT NULL, 
    hashed_password TEXT NOT NULL, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL, 
    PRIMARY KEY (id), 
    UNIQUE (email)
);

CREATE TABLE public.authors (
    id BIGSERIAL NOT NULL, 
    name TEXT NOT NULL, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL, 
    PRIMARY KEY (id), 
    UNIQUE (name)
);

CREATE TABLE public.books (
    id BIGSERIAL NOT NULL, 
    title TEXT NOT NULL, 
    author_id BIGINT NOT NULL, 
    genre TEXT NOT NULL, 
    published_year INTEGER NOT NULL, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL, 
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL, 
    PRIMARY KEY (id), 
    CONSTRAINT books_genre_check CHECK (genre IN ('Fiction','Non-Fiction','Science','History')), 
    CONSTRAINT books_year_check CHECK (published_year BETWEEN 1800 AND EXTRACT(YEAR FROM CURRENT_DATE)::INT), 
    FOREIGN KEY(author_id) REFERENCES public.authors (id) ON DELETE RESTRICT
);

CREATE INDEX idx_books_lower_title ON public.books (lower(title));

CREATE INDEX idx_authors_lower_name ON public.authors (lower(name));

CREATE INDEX idx_books_published_year ON public.books (published_year);

CREATE INDEX idx_books_author_id ON public.books (author_id);

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
    $$ LANGUAGE plpgsql;;

INSERT INTO public.alembic_version (version_num) VALUES ('0001_create_core') RETURNING public.alembic_version.version_num;

-- Running upgrade 0001_create_core -> 0002_dedupe_books

ALTER TABLE public.books ADD COLUMN title_norm TEXT GENERATED ALWAYS AS (lower(title)) STORED;

CREATE UNIQUE INDEX uniq_books_title_author_year ON public.books (title_norm, author_id, published_year);

UPDATE public.alembic_version SET version_num='0002_dedupe_books' WHERE public.alembic_version.version_num = '0001_create_core';

COMMIT;

