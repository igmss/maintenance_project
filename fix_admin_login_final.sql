-- Final Admin Login Fix
-- Run this in Supabase SQL Editor to fix admin login

-- 1. Add missing columns if they don't exist
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'suspended', 'inactive'));

-- 2. Fix the admin user - update password hash and user type
UPDATE users SET 
  password_hash = '$2b$12$LQv3c1yqBwlFXK8QqLnF7.SWMX.jMa7dWRvyS5J5HZzJQK7.YtWNW', -- This is for password: admin123
  user_type = 'admin',
  status = 'active',
  updated_at = NOW()
WHERE email = 'admin@maintenanceplatform.com';

-- 3. If user doesn't exist, create it
INSERT INTO users (
  email, 
  phone, 
  password_hash, 
  user_type, 
  status,
  created_at,
  updated_at
) 
SELECT 
  'admin@maintenanceplatform.com',
  '01012345678',
  '$2b$12$LQv3c1yqBwlFXK8QqLnF7.SWMX.jMa7dWRvyS5J5HZzJQK7.YtWNW', -- password: admin123
  'admin',
  'active',
  NOW(),
  NOW()
WHERE NOT EXISTS (
  SELECT 1 FROM users WHERE email = 'admin@maintenanceplatform.com'
);

-- 4. Ensure admin has a profile (required by the system)
WITH admin_user AS (
  SELECT id FROM users WHERE email = 'admin@maintenanceplatform.com'
)
INSERT INTO customer_profiles (
  user_id,
  first_name,
  last_name,
  preferred_language,
  created_at,
  updated_at
)
SELECT 
  admin_user.id,
  'Admin',
  'User',
  'en',
  NOW(),
  NOW()
FROM admin_user
WHERE NOT EXISTS (
  SELECT 1 FROM customer_profiles WHERE user_id = admin_user.id
);

-- 5. Verify the admin user
SELECT 
  email, 
  user_type, 
  status, 
  created_at,
  updated_at
FROM users 
WHERE email = 'admin@maintenanceplatform.com';

-- Success message
SELECT 'Admin user fixed! Credentials: admin@maintenanceplatform.com / admin123' as message;