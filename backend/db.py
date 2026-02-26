# db.py
import os
from contextlib import contextmanager
import psycopg2
from psycopg2.pool import ThreadedConnectionPool

_pool = None

def init_db_pool(config):
    global _pool
    if _pool is not None:
        return

    dsn = (
        f"host={config['HOST']} "
        f"port={config['PORT']} "
        f"dbname={config['DBNAME']} "
        f"user={config['USER']} "
        f"password={config['PASSWORD']}"
    )

    _pool = ThreadedConnectionPool(
        minconn=1,
        maxconn=20,
        dsn=dsn,
    )


@contextmanager
def get_db():
    """
    在 route 里这样用：

    with get_db() as conn:
        ...
    """
    conn = _pool.getconn()
    try:
        conn.autocommit = False
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        _pool.putconn(conn)