-- Check all tables in the database
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public';

-- Check users table structure
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns 
WHERE table_name = 'users'
ORDER BY ordinal_position;

-- Check service_provider_profiles table structure
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns 
WHERE table_name = 'service_provider_profiles'
ORDER BY ordinal_position;

-- Check provider_documents table structure
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns 
WHERE table_name = 'provider_documents'
ORDER BY ordinal_position;

-- Check current service providers and their status
SELECT 
    u.email,
    u.user_type,
    u.status as user_status,
    spp.verification_status,
    spp.first_name,
    spp.last_name,
    spp.created_at
FROM users u
LEFT JOIN service_provider_profiles spp ON u.id = spp.user_id
WHERE u.user_type = 'service_provider'
ORDER BY spp.created_at DESC;

-- Check documents for service providers
SELECT 
    pd.id,
    pd.document_type,
    pd.verification_status,
    pd.created_at,
    spp.first_name,
    spp.last_name,
    u.email
FROM provider_documents pd
JOIN service_provider_profiles spp ON pd.provider_id = spp.id
JOIN users u ON spp.user_id = u.id
ORDER BY pd.created_at DESC;