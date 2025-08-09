-- FORCED VARCHAR MIGRATION - Prevents Supabase from auto-converting to UUID
-- Run each command individually in Supabase SQL Editor

-- Step 1: Drop existing table completely
DROP TABLE IF EXISTS customer_locations CASCADE;

-- Step 2: Create table with explicit VARCHAR types (not VARCHAR(36) which might auto-convert)
CREATE TABLE customer_locations (
    id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    customer_id TEXT NOT NULL,
    latitude NUMERIC(10, 8) NOT NULL,
    longitude NUMERIC(11, 8) NOT NULL,
    accuracy NUMERIC(6, 2),
    address_components JSONB,
    formatted_address TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Step 3: Add foreign key constraint AFTER table creation
ALTER TABLE customer_locations 
ADD CONSTRAINT fk_customer_locations_customer_id 
FOREIGN KEY (customer_id) REFERENCES users(id) ON DELETE CASCADE;

-- Step 4: Create indexes
CREATE INDEX idx_customer_locations_customer_id ON customer_locations(customer_id);
CREATE INDEX idx_customer_locations_active ON customer_locations(is_active);
CREATE INDEX idx_customer_locations_coords ON customer_locations(latitude, longitude);

-- Step 5: Create update trigger
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