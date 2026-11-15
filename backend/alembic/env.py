"""
Alembic Environment Configuration.
Configures database migrations for PostgreSQL and SQLite models.
"""

import sys
import os
from logging.config import fileConfig
from sqlalchemy import pool
from alembic import context

# Ensure backend root is in python path
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.abspath(os.path.join(current_dir, ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.core.config import settings
from app.database.base import Base
import app.models  # Ensure all models are registered with Base.metadata

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def get_db_url() -> str:
    """Retrieves target database URL from application settings or environment."""
    return os.environ.get("DATABASE_URL") or settings.SQLALCHEMY_DATABASE_URI


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode without an active DB connection."""
    url = get_db_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode with a live DB connection."""
    from app.database.session import create_app_engine
    
    url = get_db_url()
    connectable = create_app_engine(url)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
