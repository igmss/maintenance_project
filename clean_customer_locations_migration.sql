-- Clean migration script for customer_locations table
-- Run this script in your Supabase SQL Editor

-- Step 1: Drop existing table
DROP TABLE IF EXISTS customer_locations CASCADE;

-- Step 2: Create new table with correct schema
CREATE TABLE customer_locations (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    customer_id VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    latitude NUMERIC(10, 8) NOT NULL,
    longitude NUMERIC(11, 8) NOT NULL,
    accuracy NUMERIC(6, 2),
    address_components JSON,
    formatted_address TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Step 3: Create performance indexes
CREATE INDEX idx_customer_locations_customer_id ON customer_locations(customer_id);
CREATE INDEX idx_customer_locations_active ON customer_locations(is_active);
CREATE INDEX idx_customer_locations_coords ON customer_locations(latitude, longitude);

-- Step 4: Create auto-update trigger for last_updated
CREATE OR REPLACE FUNCTION update_customer_locations_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_updated = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_customer_locations_updated_at
    BEFORE UPDATE ON customer_locations
    FOR EACH ROW
    EXECUTE FUNCTION update_customer_locations_updated_at();