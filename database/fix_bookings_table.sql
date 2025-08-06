-- Fix Bookings Table Schema
-- Add missing columns and ENUM types for bookings functionality

-- Create ENUM types if they don't exist
DO $$ 
BEGIN
    -- Booking status enum
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'booking_status') THEN
        CREATE TYPE booking_status AS ENUM ('pending', 'confirmed', 'in_progress', 'completed', 'cancelled', 'disputed');
    END IF;
    
    -- Payment status enum  
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'payment_status') THEN
        CREATE TYPE payment_status AS ENUM ('pending', 'paid', 'refunded', 'disputed');
    END IF;
    
    -- Payment methods enum
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'payment_methods') THEN
        CREATE TYPE payment_methods AS ENUM ('cash', 'card', 'wallet', 'bank_transfer');
    END IF;
    
    -- Location status enum (for booking locations)
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'location_status') THEN
        CREATE TYPE location_status AS ENUM ('en_route', 'arrived', 'in_progress');
    END IF;
END
$$;

-- Create bookings table if it doesn't exist
CREATE TABLE IF NOT EXISTS bookings (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    customer_id VARCHAR(36) NOT NULL REFERENCES customer_profiles(id),
    provider_id VARCHAR(36) REFERENCES service_provider_profiles(id),
    service_id VARCHAR(36) NOT NULL REFERENCES services(id),
    booking_status booking_status DEFAULT 'pending',
    scheduled_date TIMESTAMP WITH TIME ZONE NOT NULL,
    actual_start_time TIMESTAMP WITH TIME ZONE,
    actual_end_time TIMESTAMP WITH TIME ZONE,
    estimated_duration INTEGER, -- in minutes
    actual_duration INTEGER, -- in minutes
    service_address JSONB NOT NULL,
    special_instructions TEXT,
    total_amount DECIMAL(10,2) NOT NULL,
    platform_commission DECIMAL(10,2) NOT NULL,
    provider_earnings DECIMAL(10,2) NOT NULL,
    payment_status payment_status DEFAULT 'pending',
    payment_method payment_methods,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Add missing columns to existing bookings table
DO $$ 
BEGIN
    -- Add booking_status column if missing
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'bookings' AND column_name = 'booking_status') THEN
        ALTER TABLE bookings ADD COLUMN booking_status booking_status DEFAULT 'pending';
    END IF;
    
    -- Add payment_status column if missing
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'bookings' AND column_name = 'payment_status') THEN
        ALTER TABLE bookings ADD COLUMN payment_status payment_status DEFAULT 'pending';
    END IF;
    
    -- Add payment_method column if missing
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'bookings' AND column_name = 'payment_method') THEN
        ALTER TABLE bookings ADD COLUMN payment_method payment_methods;
    END IF;
    
    -- Add other potentially missing columns
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'bookings' AND column_name = 'estimated_duration') THEN
        ALTER TABLE bookings ADD COLUMN estimated_duration INTEGER;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'bookings' AND column_name = 'actual_duration') THEN
        ALTER TABLE bookings ADD COLUMN actual_duration INTEGER;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'bookings' AND column_name = 'service_address') THEN
        ALTER TABLE bookings ADD COLUMN service_address JSONB;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'bookings' AND column_name = 'special_instructions') THEN
        ALTER TABLE bookings ADD COLUMN special_instructions TEXT;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'bookings' AND column_name = 'platform_commission') THEN
        ALTER TABLE bookings ADD COLUMN platform_commission DECIMAL(10,2);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'bookings' AND column_name = 'provider_earnings') THEN
        ALTER TABLE bookings ADD COLUMN provider_earnings DECIMAL(10,2);
    END IF;
END
$$;

-- Create related tables if they don't exist

-- Booking status history table
CREATE TABLE IF NOT EXISTS booking_status_history (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    booking_id VARCHAR(36) NOT NULL REFERENCES bookings(id),
    previous_status VARCHAR(20),
    new_status VARCHAR(20) NOT NULL,
    changed_by VARCHAR(36) REFERENCES users(id),
    change_reason TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Booking reviews table
CREATE TABLE IF NOT EXISTS booking_reviews (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    booking_id VARCHAR(36) NOT NULL REFERENCES bookings(id),
    customer_id VARCHAR(36) NOT NULL REFERENCES customer_profiles(id),
    provider_id VARCHAR(36) NOT NULL REFERENCES service_provider_profiles(id),
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    review_text TEXT,
    review_photos JSONB,
    is_verified BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Booking locations table
CREATE TABLE IF NOT EXISTS booking_locations (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    booking_id VARCHAR(36) NOT NULL REFERENCES bookings(id),
    provider_id VARCHAR(36) NOT NULL REFERENCES service_provider_profiles(id),
    latitude DECIMAL(10,8) NOT NULL,
    longitude DECIMAL(11,8) NOT NULL,
    accuracy DECIMAL(6,2),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    status location_status DEFAULT 'en_route'
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_bookings_customer_id ON bookings(customer_id);
CREATE INDEX IF NOT EXISTS idx_bookings_provider_id ON bookings(provider_id);
CREATE INDEX IF NOT EXISTS idx_bookings_service_id ON bookings(service_id);
CREATE INDEX IF NOT EXISTS idx_bookings_created_at ON bookings(created_at);
CREATE INDEX IF NOT EXISTS idx_bookings_status ON bookings(booking_status);

-- Verify the changes
SELECT 'BOOKINGS TABLE STRUCTURE' as info;
SELECT column_name, data_type, column_default, is_nullable
FROM information_schema.columns 
WHERE table_name = 'bookings' 
ORDER BY ordinal_position;