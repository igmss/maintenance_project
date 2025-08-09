-- Migration script to fix customer_locations table schema
-- This script fixes the data type mismatch between users.id and customer_locations.customer_id

-- First, drop the existing table if it has UUID columns that conflict with varchar users.id
DROP TABLE IF EXISTS customer_locations CASCADE;

-- Recreate the customer_locations table with proper data types
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

-- Create indexes for better performance
CREATE INDEX idx_customer_locations_customer_id ON customer_locations(customer_id);
CREATE INDEX idx_customer_locations_active ON customer_locations(is_active);
CREATE INDEX idx_customer_locations_coords ON customer_locations(latitude, longitude);

-- Add a trigger to update last_updated timestamp
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

COMMIT;