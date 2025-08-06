-- Fix Service Provider Profiles Table Schema
-- Add missing columns for service provider registration

-- Add missing columns to service_provider_profiles table
ALTER TABLE service_provider_profiles 
ADD COLUMN IF NOT EXISTS national_id VARCHAR(14),
ADD COLUMN IF NOT EXISTS date_of_birth DATE,
ADD COLUMN IF NOT EXISTS preferred_language VARCHAR(5) DEFAULT 'ar';

-- Make business_name nullable since registration might not provide it initially
ALTER TABLE service_provider_profiles 
ALTER COLUMN business_name DROP NOT NULL;

-- Verify the changes
SELECT 'SERVICE_PROVIDER_PROFILES - NEW COLUMNS' as info;
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns 
WHERE table_name = 'service_provider_profiles' 
AND column_name IN ('national_id', 'date_of_birth', 'preferred_language', 'business_name')
ORDER BY column_name;