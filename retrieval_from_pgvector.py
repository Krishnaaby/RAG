from sentence_transformers import SentenceTransformer


# Step 1 - to embed the user query to do a vector search
model = SentenceTransformer("nomic-ai/nomic-embed-text-v1.5", trust_remote_code=True)

user_query = "how much amount is yet to be paid?"


# Embeddings generate numpy arrays/tensors they arent compatible to be stored as those data types
# Hence the type conversion to list
query_vector = model.encode(user_query).tolist()

# Step 2: Retrieve top-k similar tables from PGVector
from sqlalchemy import select
from sqlalchemy.orm import Session
from create_vector_table import EmbeddedTable, engine  # Import engine

# Use a context manager for the session
with Session(engine) as session:
    k = 1  # number of tables to retrieve

    stmt = select(
        EmbeddedTable.table_name,
        EmbeddedTable.schema_name,
        EmbeddedTable.description,
        EmbeddedTable.embedding
    ).order_by(
        EmbeddedTable.embedding.cosine_distance(query_vector)  # Correct reference
    ).limit(k)

    results = session.execute(stmt).all()

    for r in results:
        print(r[0], r[1])  # table_name, schema_name
        print(r[2])        # description
