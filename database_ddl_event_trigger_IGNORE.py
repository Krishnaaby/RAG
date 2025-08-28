from sqlalchemy import create_engine, text


db_ddl_trigger_function = """

CREATE OR REPLACE FUNCTION audit_ddl()
RETURNS event_trigger AS $$
DECLARE
    tbl text;
BEGIN
    -- Get distinct table names affected by this DDL
    FOR tbl IN
        SELECT DISTINCT
            split_part(object_identity, '.', 2) AS table_name
        FROM pg_event_trigger_ddl_commands()
    LOOP
        -- Insert into schema_changes once per table
        INSERT INTO schema_changes(command_tag, table_name, changed_on)
        VALUES (TG_TAG, tbl, now());

        -- Send a notification to Python listener
        PERFORM pg_notify('ddl_changes', json_build_object(
            'table_name', tbl,
            'command', TG_TAG
        )::text);
    END LOOP;
END;
$$ LANGUAGE plpgsql;

DROP EVENT TRIGGER IF EXISTS ddl_audit;

CREATE EVENT TRIGGER ddl_audit
    ON ddl_command_end
    EXECUTE FUNCTION audit_ddl();
"""


engine = create_engine(connection_url)
with engine.connect() as con:
    conn.execute(text(db_ddl_trigger_function))
    conn.commit()