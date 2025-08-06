-- Fix Provider Services Table Schema
-- Add all missing columns that the backend ProviderService model expects

-- Add missing columns to provider_services table
ALTER TABLE provider_services 
ADD COLUMN IF NOT EXISTS custom_price DECIMAL(10,2),
ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT true,
ADD COLUMN IF NOT EXISTS is_available BOOLEAN DEFAULT true,
ADD COLUMN IF NOT EXISTS experience_years INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;

-- Set default values for existing records
UPDATE provider_services 
SET 
    is_active = COALESCE(is_active, true),
    is_available = COALESCE(is_available, true),
    experience_years = COALESCE(experience_years, 0),
    created_at = COALESCE(created_at, CURRENT_TIMESTAMP),
    updated_at = COALESCE(updated_at, CURRENT_TIMESTAMP)
WHERE 
    is_active IS NULL 
    OR is_available IS NULL
    OR experience_years IS NULL
    OR created_at IS NULL
    OR updated_at IS NULL;

-- Add unique constraint if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE table_name = 'provider_services' 
        AND constraint_name = 'unique_provider_service'
    ) THEN
        ALTER TABLE provider_services 
        ADD CONSTRAINT unique_provider_service 
        UNIQUE (provider_id, service_id);
    END IF;
END $$;

-- Verify the table structure
SELECT 'PROVIDER_SERVICES - ALL COLUMNS' as info;
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns 
WHERE table_name = 'provider_services' 
ORDER BY ordinal_position;