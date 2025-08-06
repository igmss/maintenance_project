-- Debug: Check if there are multiple users tables or schema issues

-- Check all users tables in all schemas
SELECT schemaname, tablename 
FROM pg_tables 
WHERE tablename LIKE '%users%'
ORDER BY schemaname, tablename;

-- Check the exact structure of the main users table
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns 
WHERE table_name = 'users' 
AND table_schema = 'public'
ORDER BY ordinal_position;

-- Check if there's an auth.users table (Supabase default)
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns 
WHERE table_name = 'users' 
AND table_schema = 'auth'
ORDER BY ordinal_position;