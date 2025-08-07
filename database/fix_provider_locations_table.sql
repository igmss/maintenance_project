-- Fix Provider Locations Table Schema
-- Add ALL missing columns that the backend ProviderLocation model expects

-- Add missing columns to provider_locations table
ALTER TABLE provider_locations 
ADD COLUMN IF NOT EXISTS latitude DECIMAL(10,8),
ADD COLUMN IF NOT EXISTS longitude DECIMAL(11,8),
ADD COLUMN IF NOT EXISTS accuracy DECIMAL(6,2),
ADD COLUMN IF NOT EXISTS heading DECIMAL(5,2),
ADD COLUMN IF NOT EXISTS speed DECIMAL(5,2),
ADD COLUMN IF NOT EXISTS is_online BOOLEAN DEFAULT true,
ADD COLUMN IF NOT EXISTS battery_level INTEGER,
ADD COLUMN IF NOT EXISTS last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;

-- Set default values for existing records
UPDATE provider_locations 
SET 
    latitude = COALESCE(latitude, 30.0444),  -- Default Cairo coordinates
    longitude = COALESCE(longitude, 31.2357),
    accuracy = COALESCE(accuracy, 10.0),
    heading = COALESCE(heading, 0.0),
    speed = COALESCE(speed, 0.0),
    is_online = COALESCE(is_online, true),
    battery_level = COALESCE(battery_level, 100),
    last_updated = COALESCE(last_updated, created_at, CURRENT_TIMESTAMP)
WHERE 
    latitude IS NULL 
    OR longitude IS NULL
    OR accuracy IS NULL
    OR heading IS NULL
    OR speed IS NULL
    OR is_online IS NULL
    OR battery_level IS NULL
    OR last_updated IS NULL;

-- Make required columns NOT NULL after setting defaults
ALTER TABLE provider_locations 
ALTER COLUMN latitude SET NOT NULL,
ALTER COLUMN longitude SET NOT NULL;

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