from alembic import context
from sqlalchemy import engine_from_config, pool
from logging.config import fileConfig
import os


AP_MYSQL_USER = "myadmin"
# the passord is "@Toshib12345678" but in the sqlalchemy its seen as url == @ => %40
AP_MYSQL_PWD = "Toshib123"
AP_MYSQL_HOST = "localhost"
AP_MYSQL_DB = "alumni_portal_v1"
AP_MYSQL_PORT = 4022
# Set up the Database URL
db_url = f"mysql+mysqldb://{AP_MYSQL_USER}:{AP_MYSQL_PWD}@{AP_MYSQL_HOST}:{AP_MYSQL_PORT}/{AP_MYSQL_DB}"

# Set up Alembic Config
config = context.config
config.set_main_option("sqlalchemy.url", db_url)

fileConfig(config.config_file_name)

# Import your models
from models.basemodel import Base  # Adjust the path as necessary

target_metadata = Base.metadata


def run_migrations_offline():
    context.configure(url=db_url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(
            config.config_ini_section
        ),  # This should contain the sqlalchemy.url option now
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
