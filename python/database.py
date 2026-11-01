"""MySQL connection helpers for Mail Workbench.

Configuration is read from environment variables, with an optional project
``.env`` file loaded by :mod:`python-dotenv`.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parent.parent


def connect() -> Any:
    """Create and return a MySQL connection using the project environment.

    ``DB_NAME``, ``DB_USER`` and ``DB_PASSWORD`` are required. ``DB_HOST`` and
    ``DB_PORT`` default to ``localhost`` and ``3306`` respectively.

    :returns: An open ``mysql.connector`` connection.
    :raises RuntimeError: If required configuration or the driver is missing.
    :raises mysql.connector.Error: If the server rejects the connection.
    """
    load_dotenv(PROJECT_ROOT / ".env")
    required = ("DB_NAME", "DB_USER", "DB_PASSWORD")
    missing = [key for key in required if not os.getenv(key)]
    if missing:
        raise RuntimeError("Missing required database settings: " + ", ".join(missing))

    try:
        import mysql.connector
    except ImportError as error:
        raise RuntimeError(
            "MySQL driver is missing. Install dependencies with: "
            "python -m pip install -r requirements.txt"
        ) from error

    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "3306")),
        database=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
    )
