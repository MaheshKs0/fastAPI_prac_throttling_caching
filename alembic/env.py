import asyncio
from logging.config import fileConfig
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import pool
from alembic import context

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import your app's config and models
from src.db.config import DATABASE_URL
from src.school.models import Base  # Base must be defined in models.py


# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config
fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = create_async_engine(
        DATABASE_URL,
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        # First: Configure Alembic using sync-compatible function
        def do_migrations(sync_connection):
            context.configure(
                connection=sync_connection,
                target_metadata=target_metadata,
            )
            with context.begin_transaction():
                context.run_migrations()

        # Then: Run the above with sync-style handling
        await connection.run_sync(do_migrations)

    await connectable.dispose()


def main():
    if context.is_offline_mode():
        run_migrations_offline()
    else:
        asyncio.run(run_migrations_online())

main()