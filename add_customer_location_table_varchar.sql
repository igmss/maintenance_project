-- Migration: Add CustomerLocation table for customer live location tracking (PostgreSQL/Supabase)
-- This version uses VARCHAR(36) to match SQLAlchemy models
-- Use this if you want to keep string-based UUIDs

-- First, let's check what type the users.id column actually is
SELECT column_name, data_type, character_maximum_length 
FROM information_schema.columns 
WHERE table_name = 'users' AND column_name = 'id';

-- Option 1: If users.id is UUID, we need to convert customer_id to UUID type
-- Use the main add_customer_location_table.sql file

-- Option 2: If users.id should be VARCHAR(36), modify users table first
-- This would require checking if the users table can be safely modified

-- For now, create the table with UUID to match the error message
CREATE TABLE IF NOT EXISTS customer_locations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    latitude NUMERIC(10, 8) NOT NULL,
    longitude NUMERIC(11, 8) NOT NULL,
    accuracy NUMERIC(6, 2),
    address_components JSONB,
    formatted_address TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_updated TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_customer_locations_customer_id ON customer_locations (customer_id);
CREATE INDEX IF NOT EXISTS idx_customer_locations_active ON customer_locations (is_active);
CREATE INDEX IF NOT EXISTS idx_customer_locations_updated ON customer_locations (last_updated DESC);

-- Trigger for auto-update
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

COMMENT ON TABLE customer_locations IS 'Customer live location tracking for better service provider matching';

SELECT 'customer_locations table created successfully with UUID type' AS status;