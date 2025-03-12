import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from app.database import Base, DATABASE_URL
from app.models import *

config = context.config
# Remove "+aiosqlite" from the URL for synchronous migrations
sync_url = DATABASE_URL.replace("+aiosqlite", "")
config.set_main_option("sqlalchemy.url", sync_url)
fileConfig(config.config_file_name or "")

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()