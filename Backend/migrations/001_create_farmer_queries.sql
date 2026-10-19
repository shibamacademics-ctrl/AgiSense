CREATE TABLE IF NOT EXISTS farmer_queries (
    id BIGSERIAL PRIMARY KEY,
    farmer_id VARCHAR(128),
    query_type VARCHAR(64) NOT NULL,
    request_payload JSONB NOT NULL,
    response_payload JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_farmer_queries_farmer_id
    ON farmer_queries (farmer_id);

CREATE INDEX IF NOT EXISTS ix_farmer_queries_query_type
    ON farmer_queries (query_type);

CREATE INDEX IF NOT EXISTS ix_farmer_queries_created_at
    ON farmer_queries (created_at DESC);
