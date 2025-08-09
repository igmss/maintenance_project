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

-- Fix foreign keys to reference service_provider_profiles instead of users
-- Safe to run multiple times

DO $$
BEGIN
    -- provider_locations.provider_id fk
    IF EXISTS (
        SELECT 1 FROM information_schema.table_constraints c
        WHERE c.constraint_type = 'FOREIGN KEY'
          AND c.table_name = 'provider_locations'
          AND c.constraint_name = 'provider_locations_provider_id_fkey'
    ) THEN
        ALTER TABLE provider_locations
        DROP CONSTRAINT provider_locations_provider_id_fkey;
    END IF;

    ALTER TABLE provider_locations
    ADD CONSTRAINT provider_locations_provider_id_fkey
    FOREIGN KEY (provider_id) REFERENCES service_provider_profiles(id) ON DELETE CASCADE;

    -- provider_service_areas.provider_id fk
    IF EXISTS (
        SELECT 1 FROM information_schema.table_constraints c
        WHERE c.constraint_type = 'FOREIGN KEY'
          AND c.table_name = 'provider_service_areas'
          AND c.constraint_name = 'provider_service_areas_provider_id_fkey'
    ) THEN
        ALTER TABLE provider_service_areas
        DROP CONSTRAINT provider_service_areas_provider_id_fkey;
    END IF;

    ALTER TABLE provider_service_areas
    ADD CONSTRAINT provider_service_areas_provider_id_fkey
    FOREIGN KEY (provider_id) REFERENCES service_provider_profiles(id) ON DELETE CASCADE;

    -- provider_documents.provider_id fk
    IF EXISTS (
        SELECT 1 FROM information_schema.table_constraints c
        WHERE c.constraint_type = 'FOREIGN KEY'
          AND c.table_name = 'provider_documents'
          AND c.constraint_name = 'provider_documents_provider_id_fkey'
    ) THEN
        ALTER TABLE provider_documents
        DROP CONSTRAINT provider_documents_provider_id_fkey;
    END IF;

    ALTER TABLE provider_documents
    ADD CONSTRAINT provider_documents_provider_id_fkey
    FOREIGN KEY (provider_id) REFERENCES service_provider_profiles(id) ON DELETE CASCADE;

    -- booking_reviews.provider_id fk (if present in this schema)
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'booking_reviews' AND column_name = 'provider_id'
    ) THEN
        IF EXISTS (
            SELECT 1 FROM information_schema.table_constraints c
            WHERE c.constraint_type = 'FOREIGN KEY'
              AND c.table_name = 'booking_reviews'
              AND c.constraint_name = 'booking_reviews_provider_id_fkey'
        ) THEN
            ALTER TABLE booking_reviews
            DROP CONSTRAINT booking_reviews_provider_id_fkey;
        END IF;

        ALTER TABLE booking_reviews
        ADD CONSTRAINT booking_reviews_provider_id_fkey
        FOREIGN KEY (provider_id) REFERENCES service_provider_profiles(id) ON DELETE CASCADE;
    END IF;
END $$;