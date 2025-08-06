-- Fix the remaining users table issue
-- Add missing is_active and is_verified columns to users table

ALTER TABLE users 
ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT true,
ADD COLUMN IF NOT EXISTS is_verified BOOLEAN DEFAULT false;

-- Update existing records with default values
UPDATE users 
SET is_active = true 
WHERE is_active IS NULL;

UPDATE users 
SET is_verified = false 
WHERE is_verified IS NULL;

-- Verify the fix
SELECT 'users' as table_name, column_name, data_type, is_nullable, column_default
FROM information_schema.columns 
WHERE table_name = 'users' 
AND column_name IN ('is_active', 'is_verified')
ORDER BY column_name;