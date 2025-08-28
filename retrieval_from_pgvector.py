from sentence_transformers import SentenceTransformer


# Step 1 - to embed the user query to do a vector search
model = SentenceTransformer("nomic-ai/nomic-embed-text-v1.5")

user_query = "Show me the total sales by customer region last year"


# Embeddings generate numpy arrays/tensors they arent compatible to be stored as those data types
# Hence the type conversion to list
query_vector = model.encode(user_query).tolist()

# Step 2: Retrieve top-k similar tables from PGVector
from sqlalchemy import select
from sqlalchemy.orm import Session
from your_models import SchemaEmbedding

session = Session()

# PGVector similarity query
k = 5  # number of tables to retrieve

stmt = select(
    SchemaEmbedding.table,
    SchemaEmbedding.schema,
    SchemaEmbedding.description,
    SchemaEmbedding.embedding
).order_by(
    SchemaEmbedding.embedding.cosine_distance(query_vector)  # PGVector extension
).limit(k)

results = session.execute(stmt).all() # Please note that this is a row object and we may use either an Index or Name

# Each result contains the table name and the stored description
for r in results:
    print(r.table, r.schema)
    print(r.description)
