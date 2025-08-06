-- Fix Provider Service Areas Table Schema
-- Add all missing columns that the backend ProviderServiceArea model expects

-- Add missing columns to provider_service_areas table
ALTER TABLE provider_service_areas 
ADD COLUMN IF NOT EXISTS area_name VARCHAR(100),
ADD COLUMN IF NOT EXISTS center_latitude DECIMAL(10,8),
ADD COLUMN IF NOT EXISTS center_longitude DECIMAL(11,8),
ADD COLUMN IF NOT EXISTS radius_km DECIMAL(5,2),
ADD COLUMN IF NOT EXISTS is_primary_area BOOLEAN DEFAULT false,
ADD COLUMN IF NOT EXISTS travel_time_minutes INTEGER DEFAULT 30,
ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;

-- Set default values for existing records where columns are NULL
UPDATE provider_service_areas 
SET 
    area_name = COALESCE(area_name, 'Service Area'),
    center_latitude = COALESCE(center_latitude, 30.0444),  -- Default Cairo coordinates
    center_longitude = COALESCE(center_longitude, 31.2357),
    radius_km = COALESCE(radius_km, 10.0),
    is_primary_area = COALESCE(is_primary_area, false),
    travel_time_minutes = COALESCE(travel_time_minutes, 30),
    created_at = COALESCE(created_at, CURRENT_TIMESTAMP)
WHERE 
    area_name IS NULL 
    OR center_latitude IS NULL
    OR center_longitude IS NULL
    OR radius_km IS NULL
    OR is_primary_area IS NULL
    OR travel_time_minutes IS NULL
    OR created_at IS NULL;

-- Make required columns NOT NULL after setting defaults
ALTER TABLE provider_service_areas 
ALTER COLUMN area_name SET NOT NULL,
ALTER COLUMN center_latitude SET NOT NULL,
ALTER COLUMN center_longitude SET NOT NULL,
ALTER COLUMN radius_km SET NOT NULL;

-- Verify the table structure
SELECT 'PROVIDER_SERVICE_AREAS - ALL COLUMNS' as info;
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns 
WHERE table_name = 'provider_service_areas' 
ORDER BY ordinal_position;