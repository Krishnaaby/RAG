# model and db url are hardcoded, check them and any other hardcoded values later for integration
# important to know before hand what schemas to include and exclude (if specific). Else, we could vectorize all of them.

from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import ENUM
from sentence_transformers import SentenceTransformer
from create_vector_table import Base, embedded_table  # Your ORM model

# Connect to Postgres
engine = create_engine("postgresql+psycopg2://user:password@host:port/dbname") #------------------CHECK hardcoded values
Session = sessionmaker(bind=engine)
session = Session()
inspector = inspect(engine)

# Load embedding model -----------------CHECK hardcoded values
model = SentenceTransformer("nomic-ai/nomic-embed-text-v1.5")

embeddings_data = [] # to store all the embeddings here before inserting them into the vector table

# Iterate schemas & tables
for schema in inspector.get_schema_names():
    if schema.startswith('pg_') or schema == 'information_schema':
        continue

    for table_name in inspector.get_table_names(schema=schema):
        columns = inspector.get_columns(table_name, schema=schema)
        fks = inspector.get_foreign_keys(table_name, schema=schema)

        # --- Table-level document ---
        table_level_doc = f"Schema: {schema}, Table: {table_name}\nColumns:\n"

        for column in columns:
            col_info = f"- Name: {column['name']}, Type: {column['type']}"

            # Enum info
            if isinstance(column['type'], ENUM):
                enum_values = ", ".join(f"'{val}'" for val in column['type'].enums)
                col_info += f", Possible values: {enum_values}"

            # Foreign key info
            for fk in fks:
                if column['name'] in fk['constrained_columns']:
                    ref_table = fk['referred_table']
                    ref_column = fk['referred_columns'][0]
                    col_info += f", FK -> {ref_table}.{ref_column}"
                    break

            table_level_doc += col_info + "\n"

        # Encode table-level document
        table_vector_embedding = model.encode(table_level_doc).tolist()
        embeddings_data.append((schema, table_name, None, table_level_doc, table_vector_embedding))



# Insert into PGVector table
for schema_name, table_name, column_name, description, embedding in embeddings_data:
    row = embedded_table(
        schema=schema_name,
        table=table_name,
        column=column_name,           # None for table-level
        description=description,
        embedding=embedding
    )
    session.add(row)

session.commit()
print(f"✅ Inserted {len(embeddings_data)} table level embeddings into PGVector")
