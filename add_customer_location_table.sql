-- Migration: Add CustomerLocation table for customer live location tracking (PostgreSQL/Supabase)
-- This enables customers to share their location for better provider matching

-- 1) Create customer_locations table (PostgreSQL-safe)
CREATE TABLE IF NOT EXISTS customer_locations (
    id VARCHAR(36) PRIMARY KEY,
    customer_id VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    latitude NUMERIC(10, 8) NOT NULL,
    longitude NUMERIC(11, 8) NOT NULL,
    accuracy NUMERIC(6, 2),
    address_components JSONB,
    formatted_address TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_updated TIMESTAMPTZ DEFAULT NOW()
);

-- 2) Indexes (PostgreSQL creates indexes outside CREATE TABLE)
CREATE INDEX IF NOT EXISTS idx_customer_locations_customer_id ON customer_locations (customer_id);
CREATE INDEX IF NOT EXISTS idx_customer_locations_active ON customer_locations (is_active);
CREATE INDEX IF NOT EXISTS idx_customer_locations_updated ON customer_locations (last_updated DESC);
-- Optional JSONB GIN index for searching address components
-- CREATE INDEX IF NOT EXISTS idx_customer_locations_address_gin ON customer_locations USING GIN (address_components);

-- 3) Trigger to auto-update last_updated on row update (PostgreSQL alternative to MySQL ON UPDATE)
CREATE OR REPLACE FUNCTION set_customer_locations_last_updated() RETURNS TRIGGER AS $$
BEGIN
  NEW.last_updated := NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_customer_locations_last_updated ON customer_locations;
CREATE TRIGGER trg_customer_locations_last_updated
BEFORE UPDATE ON customer_locations
FOR EACH ROW
EXECUTE FUNCTION set_customer_locations_last_updated();

-- 4) Comment (PostgreSQL syntax)
COMMENT ON TABLE customer_locations IS 'Customer live location tracking for better service provider matching';

-- 5) Verify
SELECT 'customer_locations table created successfully' AS status;