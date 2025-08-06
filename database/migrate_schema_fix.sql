-- Database Migration Script to Fix Schema Mismatch
-- Run this script on your deployed database to add missing columns

-- Add missing columns to users table
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT true,
ADD COLUMN IF NOT EXISTS is_verified BOOLEAN DEFAULT false,
ADD COLUMN IF NOT EXISTS email_verified_at TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS phone_verified_at TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS last_login_at TIMESTAMP WITH TIME ZONE;

-- Add missing columns to services table
ALTER TABLE services 
ADD COLUMN IF NOT EXISTS price_unit VARCHAR(20) DEFAULT 'fixed' CHECK (price_unit IN ('fixed', 'hourly', 'per_item', 'per_sqm')),
ADD COLUMN IF NOT EXISTS estimated_duration INTEGER,
ADD COLUMN IF NOT EXISTS is_emergency_service BOOLEAN DEFAULT false,
ADD COLUMN IF NOT EXISTS emergency_surcharge_percentage DECIMAL(5,2) DEFAULT 0.00,
ADD COLUMN IF NOT EXISTS requires_materials BOOLEAN DEFAULT false;

-- Add missing columns to provider_services table if needed
ALTER TABLE provider_services 
ADD COLUMN IF NOT EXISTS experience_years INTEGER DEFAULT 0;

-- Update existing records with default values
UPDATE services 
SET price_unit = 'fixed' 
WHERE price_unit IS NULL;

UPDATE services 
SET is_emergency_service = false 
WHERE is_emergency_service IS NULL;

UPDATE services 
SET emergency_surcharge_percentage = 0.00 
WHERE emergency_surcharge_percentage IS NULL;

UPDATE services 
SET requires_materials = false 
WHERE requires_materials IS NULL;

-- Update existing users with default values
UPDATE users 
SET is_active = true 
WHERE is_active IS NULL;

UPDATE users 
SET is_verified = false 
WHERE is_verified IS NULL;

-- Verify the changes
SELECT 'users' as table_name, column_name, data_type, is_nullable, column_default 
FROM information_schema.columns 
WHERE table_name = 'users' 
ORDER BY ordinal_position

UNION ALL

SELECT 'services' as table_name, column_name, data_type, is_nullable, column_default 
FROM information_schema.columns 
WHERE table_name = 'services' 
ORDER BY ordinal_position;