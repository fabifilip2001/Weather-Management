DROP TABLE IF EXISTS countries, cities, Temperatures;

CREATE TABLE IF NOT EXISTS Countries (
    id SERIAL PRIMARY KEY NOT NULL,
    country_name VARCHAR(50) UNIQUE,
    lat DOUBLE PRECISION NOT NULL,
    lon DOUBLE PRECISION NOT NULL
);

CREATE TABLE IF NOT EXISTS Cities (
    id SERIAL PRIMARY KEY NOT NULL,
    country_id INT REFERENCES Countries (id) ON DELETE CASCADE,
    city_name VARCHAR(50),
    lat DOUBLE PRECISION NOT NULL,
    lon DOUBLE PRECISION NOT NULL,
    UNIQUE(country_id, city_name)
);

CREATE TABLE IF NOT EXISTS Temperatures (
    id SERIAL PRIMARY KEY NOT NULL,
    val DOUBLE PRECISION NOT NULL,
    timesstamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    city_id INT REFERENCES Cities (id) ON DELETE CASCADE,
    UNIQUE (city_id, timesstamp)
);