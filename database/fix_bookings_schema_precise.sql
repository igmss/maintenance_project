-- Precise Fix for Bookings Table Schema Mismatch
-- The backend expects 'scheduled_date' but database has 'preferred_date' + 'preferred_time'

-- Add the missing scheduled_date column
ALTER TABLE bookings 
ADD COLUMN IF NOT EXISTS scheduled_date TIMESTAMP WITH TIME ZONE;

-- Add other missing columns that backend expects
ALTER TABLE bookings 
ADD COLUMN IF NOT EXISTS actual_start_time TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS actual_end_time TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS total_amount DECIMAL(10,2);

-- Populate scheduled_date from existing preferred_date + preferred_time
UPDATE bookings 
SET scheduled_date = (preferred_date + preferred_time)::timestamp with time zone
WHERE scheduled_date IS NULL AND preferred_date IS NOT NULL AND preferred_time IS NOT NULL;

-- Set default values for required columns that might be NULL
UPDATE bookings 
SET total_amount = COALESCE(estimated_price, final_price, 0.00)
WHERE total_amount IS NULL;

UPDATE bookings 
SET platform_commission = COALESCE(platform_commission, 0.00)
WHERE platform_commission IS NULL;

UPDATE bookings 
SET provider_earnings = COALESCE(provider_earnings, total_amount - platform_commission, 0.00)
WHERE provider_earnings IS NULL;

-- Make sure service_address has a default JSON structure if NULL
UPDATE bookings 
SET service_address = '{}'::jsonb
WHERE service_address IS NULL;

-- Verify the fix
SELECT 'BOOKINGS TABLE - KEY COLUMNS' as info;
SELECT column_name, data_type, is_nullable
FROM information_schema.columns 
WHERE table_name = 'bookings' 
AND column_name IN (
    'scheduled_date', 
    'booking_status', 
    'actual_start_time', 
    'actual_end_time',
    'total_amount',
    'platform_commission',
    'provider_earnings',
    'service_address'
)
ORDER BY column_name;