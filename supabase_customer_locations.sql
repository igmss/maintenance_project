-- Supabase Customer Locations Table Creation
-- Run this in your Supabase SQL Editor

-- 1. Create the customer_locations table
CREATE TABLE IF NOT EXISTS public.customer_locations (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    customer_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    latitude NUMERIC(10, 8) NOT NULL,
    longitude NUMERIC(11, 8) NOT NULL,
    accuracy NUMERIC(6, 2),
    address_components JSONB,
    formatted_address TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_updated TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_customer_locations_customer_id ON public.customer_locations(customer_id);
CREATE INDEX IF NOT EXISTS idx_customer_locations_active ON public.customer_locations(is_active);
CREATE INDEX IF NOT EXISTS idx_customer_locations_updated ON public.customer_locations(last_updated DESC);

-- 3. Optional: Create GIN index for JSONB address_components (uncomment if needed)
-- CREATE INDEX IF NOT EXISTS idx_customer_locations_address_gin ON public.customer_locations USING GIN (address_components);

-- 4. Create trigger function for auto-updating last_updated
CREATE OR REPLACE FUNCTION public.update_customer_locations_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_updated = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 5. Create the trigger
DROP TRIGGER IF EXISTS trigger_customer_locations_updated_at ON public.customer_locations;
CREATE TRIGGER trigger_customer_locations_updated_at
    BEFORE UPDATE ON public.customer_locations
    FOR EACH ROW
    EXECUTE FUNCTION public.update_customer_locations_updated_at();

-- 6. Enable Row Level Security (RLS) - Important for Supabase
ALTER TABLE public.customer_locations ENABLE ROW LEVEL SECURITY;

-- 7. Create RLS policies
-- Policy: Users can only see their own location data
CREATE POLICY "Users can view their own locations" ON public.customer_locations
    FOR SELECT USING (auth.uid() = customer_id);

-- Policy: Users can insert their own location data
CREATE POLICY "Users can insert their own locations" ON public.customer_locations
    FOR INSERT WITH CHECK (auth.uid() = customer_id);

-- Policy: Users can update their own location data
CREATE POLICY "Users can update their own locations" ON public.customer_locations
    FOR UPDATE USING (auth.uid() = customer_id);

-- Policy: Users can delete their own location data
CREATE POLICY "Users can delete their own locations" ON public.customer_locations
    FOR DELETE USING (auth.uid() = customer_id);

-- 8. Add table comment
COMMENT ON TABLE public.customer_locations IS 'Customer live location tracking for better service provider matching';

-- 9. Verify the table was created successfully
SELECT 'customer_locations table created successfully in Supabase!' AS status;