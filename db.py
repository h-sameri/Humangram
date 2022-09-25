import psycopg2
from psycopg2.extras import DictCursor


def get_connection(db_url):
    conn = psycopg2.connect(db_url, cursor_factory=DictCursor)
    conn.autocommit = True
    return conn


def close_connection(conn):
    conn.cursor().close()
    conn.close()
