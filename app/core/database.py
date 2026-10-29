import os
import certifi
import psycopg
from psycopg.rows import dict_row
from langgraph.checkpoint.postgres import PostgresSaver
from dotenv import load_dotenv

load_dotenv()

# SSL certificate configuration
os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()


def get_database_url() -> str:
    """Retrieves and formats PostgreSQL connection URL from environment."""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL environment variable is not set")
    if "sslmode" not in database_url:
        separator = "&" if "?" in database_url else "?"
        database_url = f"{database_url}{separator}sslmode=require"
    return database_url


def get_postgres_checkpointer() -> PostgresSaver:
    """Initializes and sets up a PostgreSQL checkpointer for LangGraph memory."""
    database_url = get_database_url()
    conn = psycopg.connect(database_url, autocommit=True, row_factory=dict_row)
    checkpointer = PostgresSaver(conn=conn)
    checkpointer.setup()
    return checkpointer

