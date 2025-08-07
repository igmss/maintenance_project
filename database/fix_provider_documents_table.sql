-- Fix Provider Documents Table Schema
-- Add ALL missing columns and ENUMs that the backend ProviderDocument model expects

-- Create required ENUM types if they don't exist
DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'document_types') THEN
        CREATE TYPE document_types AS ENUM ('national_id', 'certificate', 'license', 'insurance', 'background_check');
    END IF;
END $$;

DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'doc_verification_status') THEN
        CREATE TYPE doc_verification_status AS ENUM ('pending', 'approved', 'rejected');
    END IF;
END $$;

-- Add missing columns to provider_documents table
ALTER TABLE provider_documents 
ADD COLUMN IF NOT EXISTS document_type document_types,
ADD COLUMN IF NOT EXISTS document_url TEXT,
ADD COLUMN IF NOT EXISTS verification_status doc_verification_status DEFAULT 'pending',
ADD COLUMN IF NOT EXISTS verified_by VARCHAR(36),
ADD COLUMN IF NOT EXISTS verified_at TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS rejection_reason TEXT,
ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;

-- Set default values for existing records
UPDATE provider_documents 
SET 
    document_type = 'national_id'
WHERE document_type IS NULL;

UPDATE provider_documents 
SET 
    document_url = 'https://example.com/document.pdf'
WHERE document_url IS NULL;

UPDATE provider_documents 
SET 
    verification_status = 'pending'
WHERE verification_status IS NULL;

UPDATE provider_documents 
SET 
    created_at = CURRENT_TIMESTAMP
WHERE created_at IS NULL;

-- Make required columns NOT NULL after setting defaults
ALTER TABLE provider_documents 
ALTER COLUMN document_type SET NOT NULL,
ALTER COLUMN document_url SET NOT NULL;

-- Add foreign key constraint for verified_by if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE table_name = 'provider_documents' 
        AND constraint_name = 'provider_documents_verified_by_fkey'
    ) THEN
        ALTER TABLE provider_documents 
        ADD CONSTRAINT provider_documents_verified_by_fkey 
        FOREIGN KEY (verified_by) REFERENCES users(id);
    END IF;
END $$;

-- Verify the table structure
SELECT 'PROVIDER_DOCUMENTS - ALL COLUMNS' as info;
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns 
WHERE table_name = 'provider_documents' 
ORDER BY ordinal_position;