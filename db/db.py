from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os 
import dotenv

dotenv.load_dotenv()


# Replace the placeholders with your PostgreSQL connection details
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_host = os.getenv('DB_HOST')
db_port = os.getenv('DB_PORT')
db_name = os.getenv('DB_NAME')

# Create the connection string
db_url = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'

# Create the engine

engine = create_engine(db_url)
SessionLocal = sessionmaker(autocommit=False , autoflush=False, bind=engine)

Base = declarative_base()