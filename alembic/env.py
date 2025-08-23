from __future__ import annotations
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool, text
from alembic import context
import os, sys


sys.path.append(os.getcwd())

config = context.config
fileConfig(config.config_file_name)

# Якщо колись захочеш підхоплювати URL з app.settings:
# from app.core.config import settings
# config.set_main_option("sqlalchemy.url", settings.DATABASE_URL.replace("+asyncpg", "+psycopg2"))

target_metadata = None


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
        version_table_schema="public",
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        # гарантуємо потрібну схему
        connection.execute(text("SET search_path TO public"))
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            version_table_schema="public",
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
