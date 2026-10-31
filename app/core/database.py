import logging
import os
import certifi
import psycopg
from psycopg.rows import dict_row
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.checkpoint.memory import MemorySaver
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

# SSL certificate configuration
os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()


def get_database_url() -> str:
    """Retrieves and formats PostgreSQL connection URL from environment, normalizing for cloud providers like Render."""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        return ""
    # Render and Heroku often provide URLs starting with postgres://, which psycopg expects as postgresql://
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    if "sslmode" not in database_url:
        separator = "&" if "?" in database_url else "?"
        database_url = f"{database_url}{separator}sslmode=require"
    return database_url


def get_postgres_checkpointer():
    """Initializes PostgreSQL checkpointer, falling back to MemorySaver if unreachable."""
    database_url = get_database_url()
    if not database_url:
        logger.warning("DATABASE_URL is not set. Using in-memory checkpointer.")
        return MemorySaver()

    try:
        conn = psycopg.connect(database_url, autocommit=True, row_factory=dict_row, connect_timeout=5)
        checkpointer = PostgresSaver(conn=conn)
        checkpointer.setup()
        logger.info("Connected to PostgreSQL checkpointer.")
        return checkpointer
    except Exception as e:
        logger.warning(f"Could not connect to PostgreSQL ({e}). Using resilient MemorySaver.")
        return MemorySaver()
