-- Fix the full_name column issue in users table
-- Make full_name nullable since backend doesn't provide it during registration

ALTER TABLE users 
ALTER COLUMN full_name DROP NOT NULL;

-- Alternatively, you could set a default value:
-- ALTER TABLE users 
-- ALTER COLUMN full_name SET DEFAULT '';

-- Verify the change
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns 
WHERE table_name = 'users' 
AND column_name = 'full_name';