CREATE TABLE warehouse.etl_batch_history (
    batch_id UUID PRIMARY KEY,
    load_mode VARCHAR(50) NOT NULL,
    started_at TIMESTAMP NOT NULL,
    finished_at TIMESTAMP,
    status VARCHAR(20) NOT NULL,
    rows_inserted INTEGER DEFAULT 0,
    message TEXT
);