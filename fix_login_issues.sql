-- Fix login issues by adding missing status column to users table
-- The backend code expects users.status but this column doesn't exist

ALTER TABLE users 
ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'suspended', 'inactive'));

-- Update existing users to have active status
UPDATE users 
SET status = 'active' 
WHERE status IS NULL;

-- Verify the change
SELECT column_name, data_type, column_default
FROM information_schema.columns 
WHERE table_name = 'users' 
AND column_name = 'status';