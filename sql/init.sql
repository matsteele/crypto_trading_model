-- This file creates the database user and database schema

DROP ROLE IF EXISTS datascience;
CREATE ROLE datascience WITH SUPERUSER LOGIN PASSWORD 'data';
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO datascience;

-- crypto database schema

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET row_security = off;

-- uuid-ossp extension to auto generate uuid-v4 id's

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- crypto table

DROP TABLE IF EXISTS crypto;

CREATE TABLE crypto (
    uuid uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    symbol character varying(6) NOT NULL,
    open numeric(10,2) NOT NULL,
    high numeric(10,2) NOT NULL,
    low numeric(10,2) NOT NULL,
    close numeric(10,2) NOT NULL,
    volume_btc numeric(12,2),
    volume_usd numeric(12,2),
    trade_date date NOT NULL
);

-- insert historical btc prices

COPY crypto(trade_date, symbol, open, high, low, close, volume_btc, volume_usd)
FROM '/btcusd.csv' DELIMITER ',' CSV HEADER;

-- insert historical eth prices

COPY crypto(trade_date, symbol, open, high, low, close, volume_btc, volume_usd)
FROM '/ethusd.csv' DELIMITER ',' CSV HEADER;

-- insert historical ltc prices

COPY crypto(trade_date, symbol, open, high, low, close, volume_btc, volume_usd)
FROM '/ltcusd.csv' DELIMITER ',' CSV HEADER;
