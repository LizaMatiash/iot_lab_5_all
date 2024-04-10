CREATE TABLE processed_agent_data (
    id SERIAL PRIMARY KEY,
    road_state VARCHAR(255) NOT NULL,
    x FLOAT,
    y FLOAT,
    z FLOAT,
    latitude DECIMAL(20, 17),
    longitude DECIMAL(20, 17),
    timestamp TIMESTAMP
);
