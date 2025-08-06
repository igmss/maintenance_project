-- COMPREHENSIVE PROVIDER DATABASE SCHEMA FIXES
-- Run all these scripts in order to fix provider-related tables

-- 1. Fix service_provider_profiles table (missing ~25 columns)
-- SOURCE: database/complete_service_provider_profiles_fix.sql

-- 2. Fix provider_services table (missing is_active, is_available, etc.)
-- SOURCE: database/fix_provider_services_table.sql

-- 3. Fix provider_service_areas table (missing area_name, coordinates, etc.)
-- SOURCE: database/fix_provider_service_areas_table.sql

-- 4. Fix provider_locations table (missing updated_at column)
-- SOURCE: database/fix_provider_locations_table.sql

-- SUMMARY OF REQUIRED FIXES:
-- ================================

-- TABLE: service_provider_profiles
-- MISSING: national_id, date_of_birth, preferred_language, profile_image_url,
--          bio_ar, bio_en, business_description, years_of_experience,
--          verification_status, verification_notes, verified_at, verified_by,
--          is_available, average_rating, rating, total_reviews, total_bookings,
--          total_completed_jobs, total_earnings, commission_rate, service_radius,
--          hourly_rate, emergency_rate_multiplier, business_license, tax_id

-- TABLE: provider_services  
-- MISSING: is_active, is_available, custom_price, experience_years,
--          created_at, updated_at

-- TABLE: provider_service_areas
-- MISSING: area_name, center_latitude, center_longitude, radius_km,
--          is_primary_area, travel_time_minutes, created_at

-- TABLE: provider_locations
-- MISSING: updated_at (for last_updated tracking)

-- DEPLOYMENT STEPS:
-- =================
-- 1. Run: database/complete_service_provider_profiles_fix.sql
-- 2. Run: database/fix_provider_services_table.sql
-- 3. Run: database/fix_provider_service_areas_table.sql  
-- 4. Run: database/fix_provider_locations_table.sql
-- 5. Deploy backend with updated models to Render
-- 6. Test provider dashboard at: siyaana.netlify.app