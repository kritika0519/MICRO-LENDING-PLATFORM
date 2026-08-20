from __future__ import annotations

from pathlib import Path

import pandas as pd
from sqlalchemy import text

from src.database import DEFAULT_DATABASE_URL, create_database_engine

ROOT_DIR = Path(__file__).resolve().parents[1]
QUERIES_PATH = ROOT_DIR / 'sql' / 'business_queries.sql'


def read_business_queries(path: Path = QUERIES_PATH) -> list[str]:
    """Read semicolon-separated SQL statements while ignoring comment lines."""
    sql_text = path.read_text(encoding='utf-8')
    sql_text = sql_text.split('-- VERIFICATION QUERIES', 1)[0]
    statements = []
    for block in sql_text.split(';'):
        statement = '\n'.join(
            line for line in block.splitlines()
            if not line.strip().startswith('--') and line.strip().upper() != 'USE MICRO_LENDING'
        ).strip()
        if statement:
            statements.append(statement)
    return statements


def run_business_queries(database_url: str = DEFAULT_DATABASE_URL) -> list[pd.DataFrame]:
    """Execute every documented business query and return the result frames."""
    engine = create_database_engine(database_url)
    with engine.connect() as connection:
        return [pd.read_sql_query(text(query), connection) for query in read_business_queries()]


if __name__ == '__main__':
    for number, result in enumerate(run_business_queries(), start=1):
        print(f'query_{number}_rows: {len(result)}')