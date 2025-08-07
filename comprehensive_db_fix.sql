-- Comprehensive Database Fix for Maintenance Platform
-- Run this in Supabase SQL Editor

-- 1. Add missing status column to users table
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'suspended', 'inactive'));

-- Update existing users to have active status
UPDATE users 
SET status = 'active' 
WHERE status IS NULL;

-- 2. Add other missing columns to users table
ALTER TABLE users
ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT true,
ADD COLUMN IF NOT EXISTS is_verified BOOLEAN DEFAULT false,
ADD COLUMN IF NOT EXISTS email_verified_at TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS phone_verified_at TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS last_login_at TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS phone_verified BOOLEAN DEFAULT false,
ADD COLUMN IF NOT EXISTS email_verified BOOLEAN DEFAULT false;

-- 3. Fix services table
ALTER TABLE services
ADD COLUMN IF NOT EXISTS price_unit VARCHAR(20) DEFAULT 'fixed',
ADD COLUMN IF NOT EXISTS estimated_duration INTEGER,
ADD COLUMN IF NOT EXISTS is_emergency_service BOOLEAN DEFAULT false,
ADD COLUMN IF NOT EXISTS emergency_surcharge_percentage DECIMAL(5,2) DEFAULT 0.00,
ADD COLUMN IF NOT EXISTS requires_materials BOOLEAN DEFAULT false;

-- 4. Fix provider_services table
ALTER TABLE provider_services
ADD COLUMN IF NOT EXISTS experience_years INTEGER DEFAULT 0;

-- 5. Create or update admin user
-- First check if admin user exists
DO $$
DECLARE
    admin_user_id UUID;
    profile_exists BOOLEAN := false;
BEGIN
    -- Check if admin user exists
    SELECT id INTO admin_user_id 
    FROM users 
    WHERE email = 'admin@maintenanceplatform.com';
    
    IF admin_user_id IS NULL THEN
        -- Create admin user if doesn't exist
        INSERT INTO users (
            email, 
            phone, 
            password_hash, 
            user_type, 
            status,
            is_active,
            created_at,
            updated_at
        ) VALUES (
            'admin@maintenanceplatform.com',
            '+201234567890',
            '$2b$12$LQv3c1yqBwlFXK8QqLnF7.SWMX.jMa7dWRvyS5J5HZzJQK7.YtWNW', -- password: admin123
            'admin',
            'active',
            true,
            NOW(),
            NOW()
        ) RETURNING id INTO admin_user_id;
        
        -- Create customer profile for admin (required by system)
        INSERT INTO customer_profiles (
            user_id,
            first_name,
            last_name,
            preferred_language,
            created_at,
            updated_at
        ) VALUES (
            admin_user_id,
            'Admin',
            'User',
            'en',
            NOW(),
            NOW()
        );
        
        RAISE NOTICE 'Admin user created with ID: %', admin_user_id;
    ELSE
        -- Update existing user to be admin
        UPDATE users 
        SET user_type = 'admin',
            status = 'active',
            is_active = true,
            password_hash = '$2b$12$LQv3c1yqBwlFXK8QqLnF7.SWMX.jMa7dWRvyS5J5HZzJQK7.YtWNW', -- password: admin123
            updated_at = NOW()
        WHERE id = admin_user_id;
        
        -- Check if profile exists
        SELECT EXISTS(SELECT 1 FROM customer_profiles WHERE user_id = admin_user_id) INTO profile_exists;
        
        IF NOT profile_exists THEN
            INSERT INTO customer_profiles (
                user_id,
                first_name,
                last_name,
                preferred_language,
                created_at,
                updated_at
            ) VALUES (
                admin_user_id,
                'Admin',
                'User',
                'en',
                NOW(),
                NOW()
            );
        END IF;
        
        RAISE NOTICE 'Admin user updated with ID: %', admin_user_id;
    END IF;
    
END $$;

-- 6. Update all users to have proper status
UPDATE users 
SET status = 'active', is_active = true 
WHERE status IS NULL OR is_active IS NULL;

-- 7. Verify the changes
SELECT 
    email, 
    user_type, 
    status, 
    is_active,
    created_at
FROM users 
WHERE email = 'admin@maintenanceplatform.com';

-- Show the table structure
SELECT column_name, data_type, column_default
FROM information_schema.columns 
WHERE table_name = 'users' 
ORDER BY ordinal_position;