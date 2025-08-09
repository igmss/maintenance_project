-- Check the data type of users.id field
SELECT column_name, data_type, character_maximum_length 
FROM information_schema.columns 
WHERE table_name = 'users' AND column_name = 'id';

-- Also check a sample user ID to see the format
SELECT id, email, user_type FROM users LIMIT 3;