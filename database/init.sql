CREATE TABLE grids (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    deleted_at TIMESTAMPTZ
);

CREATE TABLE grid_regions (
    id SERIAL PRIMARY KEY,
    grid_id INTEGER NOT NULL REFERENCES grids(id),
    name TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    deleted_at TIMESTAMPTZ
);

CREATE TABLE grid_nodes (
    id SERIAL PRIMARY KEY,
    region_id INTEGER NOT NULL REFERENCES grid_regions(id),
    name TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    deleted_at TIMESTAMPTZ
);

CREATE TABLE measures (
    id SERIAL PRIMARY KEY,
    grid_node_id INTEGER NOT NULL REFERENCES grid_nodes(id),
    timestamp TIMESTAMPTZ NOT NULL,       
    collected_at TIMESTAMPTZ NOT NULL,
    value NUMERIC NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    deleted_at TIMESTAMPTZ
);

CREATE INDEX idx_measures_node_ts_collected_desc
    ON measures (grid_node_id, timestamp, collected_at DESC)
    WHERE deleted_at IS NULL;

CREATE INDEX idx_measures_collected_at
    ON measures (collected_at)
    WHERE deleted_at IS NULL;

CREATE INDEX idx_measures_timestamp
    ON measures (timestamp)
    WHERE deleted_at IS NULL;

INSERT INTO grids (name) VALUES 
('Grid1'), ('Grid2'), ('Grid3');

INSERT INTO grid_regions (grid_id, name)
SELECT g.id, 'Region' || r.n
FROM grids g
CROSS JOIN generate_series(1, 3) AS r(n);

INSERT INTO grid_nodes (region_id, name)
SELECT r.id, 'Node' || n.n
FROM grid_regions r
CROSS JOIN generate_series(1, 3) AS n(n);

DO $$
DECLARE
    node RECORD;
    ts TIMESTAMPTZ;
    collection_ts TIMESTAMPTZ;
    val NUMERIC;
BEGIN
    FOR node IN SELECT id FROM grid_nodes LOOP
        FOR ts IN SELECT generate_series(
            '2025-07-16 00:00:00'::TIMESTAMPTZ,
            '2025-07-23 00:00:00'::TIMESTAMPTZ,
            INTERVAL '1 hour'
        ) LOOP
            val := 95 + random() * 10;
            
            FOR i IN 0..23 LOOP
                collection_ts := ts - INTERVAL '1 day' + (i * INTERVAL '1 hour');
                
                INSERT INTO measures (grid_node_id, timestamp, collected_at, value)
                VALUES (
                    node.id,
                    ts,
                    collection_ts,
                    val + (random() * 2 - 1) * (i/24.0)
                );
            END LOOP;
        END LOOP;
    END LOOP;
END $$;
