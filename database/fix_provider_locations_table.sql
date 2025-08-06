-- Fix Provider Locations Table Schema
-- Add missing last_updated column that the backend ProviderLocation model expects

-- Add missing last_updated column to provider_locations table
ALTER TABLE provider_locations 
ADD COLUMN IF NOT EXISTS last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;

-- Set default values for existing records
UPDATE provider_locations 
SET last_updated = COALESCE(last_updated, created_at, CURRENT_TIMESTAMP)
WHERE last_updated IS NULL;

-- Add trigger to automatically update last_updated when location is modified
CREATE OR REPLACE FUNCTION update_provider_locations_last_updated()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_updated = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Drop trigger if it exists and create new one
DROP TRIGGER IF EXISTS trigger_update_provider_locations_last_updated ON provider_locations;
CREATE TRIGGER trigger_update_provider_locations_last_updated
    BEFORE UPDATE ON provider_locations
    FOR EACH ROW
    EXECUTE FUNCTION update_provider_locations_last_updated();

-- Verify the table structure
SELECT 'PROVIDER_LOCATIONS - ALL COLUMNS' as info;
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns 
WHERE table_name = 'provider_locations' 
ORDER BY ordinal_position;