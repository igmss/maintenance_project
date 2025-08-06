-- Add is_online column to provider_locations table
-- This enables real-time provider availability tracking

-- =====================================================
-- ADD IS_ONLINE COLUMN TO PROVIDER_LOCATIONS
-- =====================================================

-- Check if column already exists
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'provider_locations' 
        AND column_name = 'is_online'
    ) THEN
        -- Add the is_online column
        ALTER TABLE provider_locations 
        ADD COLUMN is_online BOOLEAN DEFAULT true;
        
        RAISE NOTICE '✅ Added is_online column to provider_locations table';
    ELSE
        RAISE NOTICE 'ℹ️  is_online column already exists in provider_locations table';
    END IF;
END $$;

-- =====================================================
-- CREATE INDEX FOR PERFORMANCE
-- =====================================================

-- Create index for fast online provider queries
CREATE INDEX IF NOT EXISTS idx_provider_locations_online 
ON provider_locations(provider_id, is_online, created_at DESC);

-- Create composite index for location-based queries
CREATE INDEX IF NOT EXISTS idx_provider_locations_online_location 
ON provider_locations(is_online, latitude, longitude, created_at DESC);

-- =====================================================
-- UPDATE EXISTING DATA
-- =====================================================

-- Set all existing provider locations to online by default
UPDATE provider_locations 
SET is_online = true 
WHERE is_online IS NULL;

-- =====================================================
-- CREATE HELPER FUNCTIONS
-- =====================================================

-- Function to get online providers within a radius
CREATE OR REPLACE FUNCTION get_online_providers_nearby(
    customer_lat DECIMAL(10,8),
    customer_lng DECIMAL(11,8),
    radius_km INTEGER DEFAULT 50
)
RETURNS TABLE(
    provider_id UUID,
    business_name VARCHAR(200),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    average_rating DECIMAL(3,2),
    total_reviews INTEGER,
    distance_km DECIMAL(8,2),
    last_location_update TIMESTAMP WITH TIME ZONE,
    is_available BOOLEAN
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        spp.user_id as provider_id,
        spp.business_name,
        spp.first_name,
        spp.last_name,
        spp.average_rating,
        spp.total_reviews,
        ROUND(
            (6371 * acos(
                cos(radians(customer_lat)) * 
                cos(radians(pl.latitude)) * 
                cos(radians(pl.longitude) - radians(customer_lng)) + 
                sin(radians(customer_lat)) * 
                sin(radians(pl.latitude))
            ))::DECIMAL, 2
        ) as distance_km,
        pl.created_at as last_location_update,
        spp.is_available
    FROM service_provider_profiles spp
    INNER JOIN (
        -- Get the most recent location for each online provider
        SELECT DISTINCT ON (provider_id) 
            provider_id, latitude, longitude, created_at
        FROM provider_locations 
        WHERE is_online = true
        AND created_at > NOW() - INTERVAL '1 hour' -- Only consider recent locations
        ORDER BY provider_id, created_at DESC
    ) pl ON pl.provider_id = spp.user_id
    WHERE spp.verification_status = 'verified'
    AND spp.is_available = true
    AND (
        6371 * acos(
            cos(radians(customer_lat)) * 
            cos(radians(pl.latitude)) * 
            cos(radians(pl.longitude) - radians(customer_lng)) + 
            sin(radians(customer_lat)) * 
            sin(radians(pl.latitude))
        )
    ) <= radius_km
    ORDER BY distance_km ASC;
END;
$$ LANGUAGE plpgsql;

-- Function to update provider online status
CREATE OR REPLACE FUNCTION update_provider_online_status(
    p_provider_id UUID,
    p_is_online BOOLEAN,
    p_latitude DECIMAL(10,8) DEFAULT NULL,
    p_longitude DECIMAL(11,8) DEFAULT NULL
)
RETURNS BOOLEAN AS $$
DECLARE
    location_updated BOOLEAN := false;
BEGIN
    -- If provider is going online and location is provided, insert new location
    IF p_is_online = true AND p_latitude IS NOT NULL AND p_longitude IS NOT NULL THEN
        INSERT INTO provider_locations (provider_id, latitude, longitude, is_online)
        VALUES (p_provider_id, p_latitude, p_longitude, true);
        location_updated := true;
    END IF;
    
    -- Update all existing locations for this provider
    UPDATE provider_locations 
    SET is_online = p_is_online
    WHERE provider_id = p_provider_id;
    
    -- Update provider availability status
    UPDATE service_provider_profiles 
    SET is_available = p_is_online,
        updated_at = CURRENT_TIMESTAMP
    WHERE user_id = p_provider_id;
    
    RETURN location_updated;
END;
$$ LANGUAGE plpgsql;

-- Function to automatically set providers offline after inactivity
CREATE OR REPLACE FUNCTION auto_offline_inactive_providers()
RETURNS INTEGER AS $$
DECLARE
    affected_count INTEGER;
BEGIN
    -- Set providers offline if no location update in last 30 minutes
    UPDATE provider_locations 
    SET is_online = false
    WHERE is_online = true 
    AND created_at < NOW() - INTERVAL '30 minutes';
    
    GET DIAGNOSTICS affected_count = ROW_COUNT;
    
    -- Also update their availability status
    UPDATE service_provider_profiles 
    SET is_available = false,
        updated_at = CURRENT_TIMESTAMP
    WHERE user_id IN (
        SELECT DISTINCT provider_id 
        FROM provider_locations 
        WHERE is_online = false
        AND provider_id NOT IN (
            SELECT provider_id 
            FROM provider_locations 
            WHERE is_online = true
        )
    );
    
    RETURN affected_count;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- CREATE VIEWS FOR EASY ACCESS
-- =====================================================

-- View for online providers with their latest location
CREATE OR REPLACE VIEW online_providers AS
SELECT 
    spp.user_id as provider_id,
    spp.business_name,
    spp.first_name,
    spp.last_name,
    spp.average_rating,
    spp.total_reviews,
    spp.total_completed_jobs,
    spp.verification_status,
    spp.is_available,
    pl.latitude,
    pl.longitude,
    pl.created_at as last_location_update,
    pl.accuracy,
    pl.heading,
    pl.speed
FROM service_provider_profiles spp
INNER JOIN (
    SELECT DISTINCT ON (provider_id) 
        provider_id, latitude, longitude, created_at, accuracy, heading, speed
    FROM provider_locations 
    WHERE is_online = true
    ORDER BY provider_id, created_at DESC
) pl ON pl.provider_id = spp.user_id
WHERE spp.verification_status = 'verified'
AND spp.is_available = true;

-- =====================================================
-- VERIFICATION AND TESTING
-- =====================================================

-- Test the new functionality
DO $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '🎉 IS_ONLINE COLUMN SETUP COMPLETE!';
    RAISE NOTICE '';
    RAISE NOTICE '✅ Column added to provider_locations table';
    RAISE NOTICE '✅ Performance indexes created';
    RAISE NOTICE '✅ Helper functions created:';
    RAISE NOTICE '   • get_online_providers_nearby()';
    RAISE NOTICE '   • update_provider_online_status()';
    RAISE NOTICE '   • auto_offline_inactive_providers()';
    RAISE NOTICE '✅ Views created: online_providers';
    RAISE NOTICE '';
    RAISE NOTICE '🚀 Ready to update backend and frontend code!';
END $$;

-- Show current provider locations status
SELECT 
    'Provider Locations Status' as info,
    COUNT(*) as total_locations,
    COUNT(*) FILTER (WHERE is_online = true) as online_locations,
    COUNT(*) FILTER (WHERE is_online = false) as offline_locations
FROM provider_locations;

-- Show online providers view
SELECT 
    'Online Providers Available' as info,
    COUNT(*) as online_providers_count
FROM online_providers;

