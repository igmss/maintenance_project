-- PRECISE Database Migration Based on Actual Current Schema
-- This script adds ONLY the missing columns that are causing API errors

-- 🔧 FIX 1: Add missing columns to SERVICES table
-- Current services table has: id, category_id, name_en, name_ar, description_en, description_ar, base_price, is_active, created_at, updated_at
-- Backend expects these additional columns:
ALTER TABLE services 
ADD COLUMN IF NOT EXISTS price_unit VARCHAR(20) DEFAULT 'fixed' CHECK (price_unit IN ('fixed', 'hourly', 'per_item', 'per_sqm')),
ADD COLUMN IF NOT EXISTS estimated_duration INTEGER,
ADD COLUMN IF NOT EXISTS is_emergency_service BOOLEAN DEFAULT false,
ADD COLUMN IF NOT EXISTS emergency_surcharge_percentage DECIMAL(5,2) DEFAULT 0.00,
ADD COLUMN IF NOT EXISTS requires_materials BOOLEAN DEFAULT false;

-- 🔧 FIX 2: Add missing columns to PROVIDER_SERVICES table  
-- Current has: id, provider_id, service_id, custom_price, is_available, created_at
-- Backend expects this additional column:
ALTER TABLE provider_services 
ADD COLUMN IF NOT EXISTS experience_years INTEGER DEFAULT 0;

-- 🔧 FIX 3: Add missing columns to CUSTOMER_PROFILES table
-- Current customer_profiles is missing first_name, last_name (has user full_name instead)
-- Backend expects separate first_name and last_name columns:
ALTER TABLE customer_profiles 
ADD COLUMN IF NOT EXISTS first_name VARCHAR(100),
ADD COLUMN IF NOT EXISTS last_name VARCHAR(100),
ADD COLUMN IF NOT EXISTS profile_image_url TEXT,
ADD COLUMN IF NOT EXISTS preferred_language VARCHAR(5) DEFAULT 'ar',
ADD COLUMN IF NOT EXISTS notification_preferences JSONB DEFAULT '{"push": true, "sms": true, "email": true}';

-- 🔧 FIX 4: Add missing columns to USERS table (main issue!)
-- The current users table appears to be Supabase's auth.users table
-- But backend expects a custom users table with these columns:
-- We need to check if there's a conflict with Supabase auth.users
-- Let's add the missing columns that backend expects:
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT true,
ADD COLUMN IF NOT EXISTS is_verified BOOLEAN DEFAULT false;

-- Note: email_verified_at, phone_verified_at, last_login_at already exist in current schema

-- 🔧 FIX 5: Update existing records with default values
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

UPDATE users 
SET is_active = true 
WHERE is_active IS NULL;

UPDATE users 
SET is_verified = false 
WHERE is_verified IS NULL;

-- 🔍 VERIFY: Check that all required columns now exist
SELECT 'SERVICES TABLE' as table_name, column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'services' 
AND column_name IN ('price_unit', 'estimated_duration', 'is_emergency_service', 'emergency_surcharge_percentage', 'requires_materials')

UNION ALL

SELECT 'PROVIDER_SERVICES TABLE' as table_name, column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'provider_services' 
AND column_name IN ('experience_years')

UNION ALL

SELECT 'USERS TABLE' as table_name, column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'users' 
AND column_name IN ('is_active', 'is_verified')

UNION ALL

SELECT 'CUSTOMER_PROFILES TABLE' as table_name, column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'customer_profiles' 
AND column_name IN ('first_name', 'last_name', 'profile_image_url', 'preferred_language', 'notification_preferences')

ORDER BY table_name, column_name;