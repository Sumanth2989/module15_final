from __future__ import annotations
from sqlalchemy import engine_from_config, pool
import sys
import os
from logging.config import fileConfig
from sqlalchemy import pool
from pathlib import Path
from alembic import context

# add your app directory to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.models import Base  # import your models' Base


# Alembic Config object
config = context.config

# Logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Make sure project root is on sys.path so "import app" works
project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import your SQLAlchemy Base and models
from app.db import Base  # adjust if your Base is in a different module
from app.models import calculation  # noqa: F401  this import ensures the model is registered

# Target metadata for autogenerate
target_metadata = Base.metadata


def get_url() -> str:
    """
    Get database URL.

    Priority:
    1. DATABASE_URL environment variable
    2. sqlalchemy.url from alembic.ini
    """
    url = os.getenv("DATABASE_URL")
    if url:
        return url
    return config.get_main_option("sqlalchemy.url")


def run_migrations_offline() -> None:
    """Run migrations in offline mode."""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in online mode."""
    configuration = config.get_section(config.config_ini_section, {}) or {}
    configuration["sqlalchemy.url"] = get_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

