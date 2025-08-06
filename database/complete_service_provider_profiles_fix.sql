-- Complete Fix for Service Provider Profiles Table
-- Add ALL missing columns that the backend model expects

-- Add all missing columns to service_provider_profiles table
ALTER TABLE service_provider_profiles 
ADD COLUMN IF NOT EXISTS national_id VARCHAR(14),
ADD COLUMN IF NOT EXISTS date_of_birth DATE,
ADD COLUMN IF NOT EXISTS preferred_language VARCHAR(5) DEFAULT 'ar',
ADD COLUMN IF NOT EXISTS profile_image_url TEXT,
ADD COLUMN IF NOT EXISTS bio_ar TEXT,
ADD COLUMN IF NOT EXISTS bio_en TEXT,
ADD COLUMN IF NOT EXISTS business_description TEXT,
ADD COLUMN IF NOT EXISTS years_of_experience INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS verification_status VARCHAR(20) DEFAULT 'pending',
ADD COLUMN IF NOT EXISTS verification_date TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS verification_notes TEXT,
ADD COLUMN IF NOT EXISTS verified_at TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS verified_by VARCHAR(36),
ADD COLUMN IF NOT EXISTS is_available BOOLEAN DEFAULT true,
ADD COLUMN IF NOT EXISTS average_rating DECIMAL(3,2) DEFAULT 0.00,
ADD COLUMN IF NOT EXISTS rating DECIMAL(3,2) DEFAULT 0.00,
ADD COLUMN IF NOT EXISTS total_reviews INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS total_bookings INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS total_completed_jobs INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS total_earnings DECIMAL(12,2) DEFAULT 0.00,
ADD COLUMN IF NOT EXISTS commission_rate DECIMAL(5,2) DEFAULT 15.00,
ADD COLUMN IF NOT EXISTS service_radius INTEGER DEFAULT 10,
ADD COLUMN IF NOT EXISTS hourly_rate DECIMAL(10,2),
ADD COLUMN IF NOT EXISTS emergency_rate_multiplier DECIMAL(3,2) DEFAULT 1.50,
ADD COLUMN IF NOT EXISTS business_license VARCHAR(100),
ADD COLUMN IF NOT EXISTS tax_id VARCHAR(50);

-- Make business_name nullable since registration might not provide it initially
ALTER TABLE service_provider_profiles 
ALTER COLUMN business_name DROP NOT NULL;

-- Set default values for existing records
UPDATE service_provider_profiles 
SET 
    years_of_experience = COALESCE(years_of_experience, 0),
    verification_status = COALESCE(verification_status, 'pending'),
    is_available = COALESCE(is_available, true),
    average_rating = COALESCE(average_rating, 0.00),
    rating = COALESCE(rating, 0.00),
    total_reviews = COALESCE(total_reviews, 0),
    total_bookings = COALESCE(total_bookings, 0),
    total_completed_jobs = COALESCE(total_completed_jobs, 0),
    total_earnings = COALESCE(total_earnings, 0.00),
    commission_rate = COALESCE(commission_rate, 15.00),
    service_radius = COALESCE(service_radius, 10),
    emergency_rate_multiplier = COALESCE(emergency_rate_multiplier, 1.50),
    preferred_language = COALESCE(preferred_language, 'ar')
WHERE 
    years_of_experience IS NULL 
    OR verification_status IS NULL 
    OR is_available IS NULL
    OR average_rating IS NULL
    OR rating IS NULL
    OR total_reviews IS NULL
    OR total_bookings IS NULL
    OR total_completed_jobs IS NULL
    OR total_earnings IS NULL
    OR commission_rate IS NULL
    OR service_radius IS NULL
    OR emergency_rate_multiplier IS NULL
    OR preferred_language IS NULL;

-- Add foreign key constraint for verified_by if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE table_name = 'service_provider_profiles' 
        AND constraint_name = 'service_provider_profiles_verified_by_fkey'
    ) THEN
        ALTER TABLE service_provider_profiles 
        ADD CONSTRAINT service_provider_profiles_verified_by_fkey 
        FOREIGN KEY (verified_by) REFERENCES users(id);
    END IF;
END $$;

-- Verify all columns exist
SELECT 'SERVICE_PROVIDER_PROFILES - ALL COLUMNS' as info;
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns 
WHERE table_name = 'service_provider_profiles' 
ORDER BY ordinal_position;