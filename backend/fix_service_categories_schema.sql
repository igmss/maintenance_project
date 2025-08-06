-- Fix service_categories table schema by adding missing columns
-- This script adds the missing columns that are defined in the SQLAlchemy model

-- Add color_code column
ALTER TABLE service_categories 
ADD COLUMN IF NOT EXISTS color_code VARCHAR(7) DEFAULT '#007bff';

-- Add is_emergency_available column  
ALTER TABLE service_categories 
ADD COLUMN IF NOT EXISTS is_emergency_available BOOLEAN DEFAULT FALSE;

-- Update any existing rows to have the default values
UPDATE service_categories 
SET color_code = '#007bff' 
WHERE color_code IS NULL;

UPDATE service_categories 
SET is_emergency_available = FALSE 
WHERE is_emergency_available IS NULL;

-- Verify the changes
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns 
WHERE table_name = 'service_categories' AND table_schema = 'public'
ORDER BY ordinal_position;