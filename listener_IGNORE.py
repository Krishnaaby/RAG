# Listener - listens to the channel mentioned in the DB trigger
# pls note that we cant use SQLAlchemy/Higher level objects like create_engine(url)
# as listeners arent supported via Higher level objects of SQLalchemy!

import psycopg2
import select
import json

# connect to your database
conn = psycopg2.connect(connection_url)
conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)

cur = conn.cursor()
cur.execute("LISTEN ddl_changes;")  # listen to the channel

print("👂 Listening for DDL changes...")

while True:
    if select.select([conn], [], [], 5) == ([], [], []):
        # timeout just so it doesn’t hang forever
        continue
    conn.poll()
    while conn.notifies:
        notify = conn.notifies.pop(0)
        payload = json.loads(notify.payload)
        print(f"📌 DDL Change -> Table: {payload['table_name']} | Type: {payload['object_type']} | Command: {payload['command']}")
