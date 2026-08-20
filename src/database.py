from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import Engine


ROOT_DIR = Path(__file__).resolve().parents[1]

PROCESSED_DIR = ROOT_DIR / "data" / "processed"

DEFAULT_DATABASE_URL = (
    f"sqlite:///{(PROCESSED_DIR / 'micro_lending.db').as_posix()}"
)

MYSQL_DATABASE_URL = os.getenv("MICRO_LENDING_MYSQL_URL", "")


def create_database_engine(
    database_url: str = DEFAULT_DATABASE_URL,
) -> Engine:
    """Create a SQLAlchemy engine for SQLite or a configured relational database."""
    return create_engine(database_url, future=True)


def load_tables_to_database(
    customers: pd.DataFrame,
    loans: pd.DataFrame,
    database_url: str = DEFAULT_DATABASE_URL,
) -> Engine:
    """
    Write processed customer and loan tables to the configured database.

    SQLite:
        Replaces local tables for development/testing.

    MySQL:
        Appends data into the tables created by sql/schema.sql.
        Data is inserted in chunks to safely handle the large Lending Club dataset.
    """

    engine = create_database_engine(database_url)

    if engine.dialect.name == "mysql":
        with engine.connect() as connection:
            existing_counts = connection.execute(
                text(
                    "SELECT "
                    "(SELECT COUNT(*) FROM customers), "
                    "(SELECT COUNT(*) FROM loans)"
                )
            ).one()

        expected_counts = (len(customers), len(loans))
        if existing_counts == expected_counts:
            return engine
        if any(existing_counts):
            raise RuntimeError(
                "MySQL tables are already partially populated. "
                "Refusing to append because the load is not idempotent. "
                "Verify the existing rows before loading."
            )

        # Insert customers in manageable batches.
        customers.to_sql(
            "customers",
            engine,
            if_exists="append",
            index=False,
            chunksize=10_000,
        )

        # Insert loans in manageable batches.
        loans.to_sql(
            "loans",
            engine,
            if_exists="append",
            index=False,
            chunksize=10_000,
        )

    else:

        customers.to_sql(
            "customers",
            engine,
            if_exists="replace",
            index=False,
        )

        loans.to_sql(
            "loans",
            engine,
            if_exists="replace",
            index=False,
        )

    return engine


def load_processed_tables_to_database(
    database_url: str = DEFAULT_DATABASE_URL,
) -> Engine:
    """Load ETL-generated CSV tables into the configured database."""

    customers = pd.read_csv(
        PROCESSED_DIR / "customers.csv"
    )

    loans = pd.read_csv(
        PROCESSED_DIR / "loans.csv"
    )

    return load_tables_to_database(
        customers,
        loans,
        database_url,
    )


def read_table_from_database(
    table_name: str,
    database_url: str = DEFAULT_DATABASE_URL,
) -> pd.DataFrame:
    """Read a database table into Pandas after validating that it exists."""

    engine = create_database_engine(database_url)

    if table_name not in inspect(engine).get_table_names():
        raise ValueError(
            f"Unknown database table: {table_name}"
        )

    return pd.read_sql_table(
        table_name,
        engine,
    )


if __name__ == "__main__":
    database_engine = load_processed_tables_to_database()

    print("Database:", database_engine.url)
    print(
        "Tables:",
        inspect(database_engine).get_table_names(),
    )