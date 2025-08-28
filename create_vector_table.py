# please note that the vector embedding size depends on the choosen model and we may need to change the table's definition
# according to the models output size

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base
from sqlalchemy.dialects.postgresql import VECTOR  # comes from pgvector extension


Base = declarative_base()

class embedded_table(Base):
    __tablename__ = "embedded_table" # name of the table where embedding will be stored
    id = Column(Integer, primary_key=True, autoincrement=True)
    schema = Column(String, nullable=False)   # Useful if there are multiple schemas
    table = Column(String, nullable=False) # table name
    column = Column(String, nullable=False) # may be used when if and when we do column level embeddings
    description = Column(Text, nullable=False)  # The original text we embedded
    embedding = Column(Vector(768), nullable=False)  # 768 for nomic v1.5 - the embedding itself
