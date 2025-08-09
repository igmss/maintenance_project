-- Fix provider_service_areas table governorate column issue
-- The backend model doesn't include governorate field, but DB requires it

-- Option 1: Make governorate column nullable (recommended for quick fix)
ALTER TABLE provider_service_areas 
ALTER COLUMN governorate DROP NOT NULL;

-- Option 2: Add default value for governorate column
UPDATE provider_service_areas 
SET governorate = 'Cairo' 
WHERE governorate IS NULL;

-- Verify the fix
SELECT 'PROVIDER_SERVICE_AREAS - GOVERNORATE COLUMN INFO' as info;
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns 
WHERE table_name = 'provider_service_areas' 
  AND column_name = 'governorate';
