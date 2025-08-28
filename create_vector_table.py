# please note that the vector embedding size depends on the choosen model and we may need to change the table's definition
# according to the models output size

from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import declarative_base
from pgvector.sqlalchemy import Vector  # comes from pgvector extension


Base = declarative_base()

class EmbeddedTable(Base):
    __tablename__ = "embeddedtable" # name of the table where embedding will be stored
    id = Column(Integer, primary_key=True, autoincrement=True)
    schema_name = Column(String, nullable=False)   # Useful if there are multiple schemas
    table_name = Column(String, nullable=False) # table name
    column_name = Column(String, nullable=True) # allow null for table-level embeddings
    description = Column(Text, nullable=False)  # The original text we embedded
    embedding = Column(Vector(768), nullable=False)  # 768 for nomic v1.5 - the embedding itself

# Create the table in the database

DATABASE_URL = "postgresql+psycopg2://user:password@localhost:5433/database_name"
engine = create_engine(DATABASE_URL)

# Only create the embedded_table table if it doesn't exist
EmbeddedTable.__table__.create(engine, checkfirst=True)

