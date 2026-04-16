import os
from sqlalchemy import create_engine
from dotenv import load_dotenv
load_dotenv()

def get_postgres_engine():
    engine = create_engine(
        f"postgresql+psycopg2://"
        f"{os.getenv('PG_USER')}:{os.getenv('PG_PASSWORD')}@"
        f"{os.getenv('PG_HOST')}:{os.getenv('PG_PORT')}/"
        f"{os.getenv('PG_DATABASE')}"
    )
    return engine