-- Fixed Database Schema for Maintenance Platform
-- This version fixes all syntax errors and will run successfully

-- =====================================================
-- CORE USER MANAGEMENT TABLES
-- =====================================================

-- Users table (main authentication table)
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20) UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    user_type VARCHAR(20) NOT NULL CHECK (user_type IN ('customer', 'service_provider', 'admin')),
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    email_verified_at TIMESTAMP WITH TIME ZONE,
    phone_verified_at TIMESTAMP WITH TIME ZONE,
    last_login_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Customer profiles table
CREATE TABLE IF NOT EXISTS customer_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    date_of_birth DATE,
    gender VARCHAR(10) CHECK (gender IN ('male', 'female', 'other')),
    profile_image_url TEXT,
    preferred_language VARCHAR(10) DEFAULT 'ar' CHECK (preferred_language IN ('ar', 'en')),
    emergency_contact_name VARCHAR(200),
    emergency_contact_phone VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id)
);

-- Service provider profiles table
CREATE TABLE IF NOT EXISTS service_provider_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    business_name VARCHAR(200) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    business_license VARCHAR(100),
    tax_id VARCHAR(50),
    profile_image_url TEXT,
    bio_ar TEXT,
    bio_en TEXT,
    years_of_experience INTEGER DEFAULT 0,
    verification_status VARCHAR(20) DEFAULT 'pending' CHECK (verification_status IN ('pending', 'verified', 'rejected', 'suspended')),
    verification_date TIMESTAMP WITH TIME ZONE,
    verification_notes TEXT,
    is_available BOOLEAN DEFAULT true,
    average_rating DECIMAL(3,2) DEFAULT 0.00,
    total_reviews INTEGER DEFAULT 0,
    total_completed_jobs INTEGER DEFAULT 0,
    total_earnings DECIMAL(12,2) DEFAULT 0.00,
    commission_rate DECIMAL(5,2) DEFAULT 15.00,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id)
);

-- =====================================================
-- LOCATION MANAGEMENT TABLES
-- =====================================================

-- Egyptian governorates table
CREATE TABLE IF NOT EXISTS governorates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name_ar VARCHAR(100) NOT NULL,
    name_en VARCHAR(100) NOT NULL,
    code VARCHAR(10) UNIQUE NOT NULL,
    center_latitude DECIMAL(10,8),
    center_longitude DECIMAL(11,8),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Cities table
CREATE TABLE IF NOT EXISTS cities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    governorate_id UUID NOT NULL REFERENCES governorates(id) ON DELETE CASCADE,
    name_ar VARCHAR(100) NOT NULL,
    name_en VARCHAR(100) NOT NULL,
    center_latitude DECIMAL(10,8),
    center_longitude DECIMAL(11,8),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Customer addresses table
CREATE TABLE IF NOT EXISTS customer_addresses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    address_type VARCHAR(20) DEFAULT 'home' CHECK (address_type IN ('home', 'work', 'other')),
    address_line1 VARCHAR(255) NOT NULL,
    address_line2 VARCHAR(255),
    city VARCHAR(100) NOT NULL,
    governorate VARCHAR(100) NOT NULL,
    postal_code VARCHAR(20),
    latitude DECIMAL(10,8),
    longitude DECIMAL(11,8),
    is_default BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- SERVICE MANAGEMENT TABLES
-- =====================================================

-- Service categories table
CREATE TABLE IF NOT EXISTS service_categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name_ar VARCHAR(100) NOT NULL,
    name_en VARCHAR(100) NOT NULL,
    description_ar TEXT,
    description_en TEXT,
    icon_url TEXT,
    color_code VARCHAR(7) DEFAULT '#007bff',
    is_active BOOLEAN DEFAULT true,
    is_emergency_available BOOLEAN DEFAULT false,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Services table
CREATE TABLE IF NOT EXISTS services (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category_id UUID NOT NULL REFERENCES service_categories(id) ON DELETE CASCADE,
    name_ar VARCHAR(200) NOT NULL,
    name_en VARCHAR(200) NOT NULL,
    description_ar TEXT,
    description_en TEXT,
    base_price DECIMAL(10,2) NOT NULL,
    price_unit VARCHAR(20) DEFAULT 'fixed' CHECK (price_unit IN ('fixed', 'hourly', 'per_item', 'per_sqm')),
    estimated_duration INTEGER,
    is_active BOOLEAN DEFAULT true,
    is_emergency_service BOOLEAN DEFAULT false,
    emergency_surcharge_percentage DECIMAL(5,2) DEFAULT 0.00,
    requires_materials BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Provider services (many-to-many relationship)
CREATE TABLE IF NOT EXISTS provider_services (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    provider_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    service_id UUID NOT NULL REFERENCES services(id) ON DELETE CASCADE,
    custom_price DECIMAL(10,2),
    is_available BOOLEAN DEFAULT true,
    experience_years INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(provider_id, service_id)
);

-- =====================================================
-- PROVIDER LOCATION AND VERIFICATION
-- =====================================================

-- Provider locations (real-time tracking)
CREATE TABLE IF NOT EXISTS provider_locations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    provider_id UUID NOT NULL REFERENCES service_provider_profiles(id) ON DELETE CASCADE,
    latitude DECIMAL(10,8) NOT NULL,
    longitude DECIMAL(11,8) NOT NULL,
    accuracy DECIMAL(6,2),
    heading DECIMAL(5,2),
    speed DECIMAL(6,2),
    is_online BOOLEAN DEFAULT true,
    battery_level INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Provider service areas
CREATE TABLE IF NOT EXISTS provider_service_areas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    provider_id UUID NOT NULL REFERENCES service_provider_profiles(id) ON DELETE CASCADE,
    governorate_id UUID NOT NULL REFERENCES governorates(id) ON DELETE CASCADE,
    city_id UUID REFERENCES cities(id) ON DELETE CASCADE,
    travel_cost DECIMAL(8,2) DEFAULT 0.00,
    max_distance_km INTEGER DEFAULT 50,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(provider_id, governorate_id, city_id)
);

-- Provider documents (for verification)
CREATE TABLE IF NOT EXISTS provider_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    provider_id UUID NOT NULL REFERENCES service_provider_profiles(id) ON DELETE CASCADE,
    document_type VARCHAR(50) NOT NULL CHECK (document_type IN ('national_id', 'business_license', 'tax_certificate', 'insurance', 'certification', 'other')),
    document_url TEXT NOT NULL,
    document_number VARCHAR(100),
    expiry_date DATE,
    verification_status VARCHAR(20) DEFAULT 'pending' CHECK (verification_status IN ('pending', 'approved', 'rejected')),
    verification_notes TEXT,
    verified_by UUID REFERENCES users(id),
    verified_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- BOOKING MANAGEMENT TABLES
-- =====================================================

-- Main bookings table
CREATE TABLE IF NOT EXISTS bookings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    booking_number VARCHAR(20) UNIQUE NOT NULL,
    customer_id UUID NOT NULL REFERENCES users(id),
    provider_id UUID REFERENCES users(id),
    service_id UUID NOT NULL REFERENCES services(id),
    booking_date DATE NOT NULL,
    booking_time TIME NOT NULL,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'confirmed', 'in_progress', 'completed', 'cancelled', 'refunded')),
    priority VARCHAR(10) DEFAULT 'normal' CHECK (priority IN ('normal', 'urgent', 'emergency')),
    
    -- Pricing
    service_price DECIMAL(10,2) NOT NULL,
    travel_cost DECIMAL(8,2) DEFAULT 0.00,
    emergency_surcharge DECIMAL(8,2) DEFAULT 0.00,
    materials_cost DECIMAL(10,2) DEFAULT 0.00,
    platform_fee DECIMAL(8,2) DEFAULT 0.00,
    total_amount DECIMAL(10,2) NOT NULL,
    
    -- Payment
    payment_status VARCHAR(20) DEFAULT 'pending' CHECK (payment_status IN ('pending', 'paid', 'refunded', 'failed')),
    payment_method VARCHAR(20) CHECK (payment_method IN ('cash', 'card', 'wallet', 'bank_transfer')),
    
    -- Location
    address_line1 VARCHAR(255) NOT NULL,
    address_line2 VARCHAR(255),
    city VARCHAR(100) NOT NULL,
    governorate VARCHAR(100) NOT NULL,
    postal_code VARCHAR(20),
    latitude DECIMAL(10,8),
    longitude DECIMAL(11,8),
    
    -- Additional info
    notes TEXT,
    special_instructions TEXT,
    estimated_duration INTEGER,
    actual_start_time TIMESTAMP WITH TIME ZONE,
    actual_end_time TIMESTAMP WITH TIME ZONE,
    
    -- Timestamps
    confirmed_at TIMESTAMP WITH TIME ZONE,
    cancelled_at TIMESTAMP WITH TIME ZONE,
    cancellation_reason TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Booking status history
CREATE TABLE IF NOT EXISTS booking_status_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    booking_id UUID NOT NULL REFERENCES bookings(id) ON DELETE CASCADE,
    old_status VARCHAR(20),
    new_status VARCHAR(20) NOT NULL,
    changed_by UUID NOT NULL REFERENCES users(id),
    reason TEXT,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Booking locations (for tracking during service)
CREATE TABLE IF NOT EXISTS booking_locations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    booking_id UUID NOT NULL REFERENCES bookings(id) ON DELETE CASCADE,
    provider_id UUID NOT NULL REFERENCES users(id),
    latitude DECIMAL(10,8) NOT NULL,
    longitude DECIMAL(11,8) NOT NULL,
    accuracy DECIMAL(6,2),
    location_type VARCHAR(20) DEFAULT 'tracking' CHECK (location_type IN ('start', 'tracking', 'end')),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Booking reviews and ratings
CREATE TABLE IF NOT EXISTS booking_reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    booking_id UUID NOT NULL REFERENCES bookings(id) ON DELETE CASCADE,
    reviewer_id UUID NOT NULL REFERENCES users(id),
    reviewer_type VARCHAR(20) NOT NULL CHECK (reviewer_type IN ('customer', 'provider')),
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    review_text TEXT,
    service_quality_rating INTEGER CHECK (service_quality_rating >= 1 AND service_quality_rating <= 5),
    punctuality_rating INTEGER CHECK (punctuality_rating >= 1 AND punctuality_rating <= 5),
    communication_rating INTEGER CHECK (communication_rating >= 1 AND communication_rating <= 5),
    value_for_money_rating INTEGER CHECK (value_for_money_rating >= 1 AND value_for_money_rating <= 5),
    would_recommend BOOLEAN,
    is_public BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(booking_id, reviewer_id)
);

-- =====================================================
-- NOTIFICATION SYSTEM
-- =====================================================

-- Notifications table
CREATE TABLE IF NOT EXISTS notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    notification_type VARCHAR(50) NOT NULL,
    title_ar VARCHAR(200) NOT NULL,
    title_en VARCHAR(200) NOT NULL,
    message_ar TEXT NOT NULL,
    message_en TEXT NOT NULL,
    data JSONB,
    is_read BOOLEAN DEFAULT false,
    is_sent BOOLEAN DEFAULT false,
    sent_at TIMESTAMP WITH TIME ZONE,
    read_at TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- PAYMENT SYSTEM
-- =====================================================

-- Payment transactions table
CREATE TABLE IF NOT EXISTS payment_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    transaction_reference VARCHAR(100) UNIQUE NOT NULL,
    booking_id UUID REFERENCES bookings(id),
    user_id UUID NOT NULL REFERENCES users(id),
    transaction_type VARCHAR(20) NOT NULL CHECK (transaction_type IN ('payment', 'refund', 'commission', 'withdrawal')),
    payment_method VARCHAR(20) NOT NULL CHECK (payment_method IN ('cash', 'card', 'wallet', 'bank_transfer', 'fawry')),
    amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'EGP',
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed', 'cancelled')),
    gateway_reference VARCHAR(200),
    gateway_response JSONB,
    fees DECIMAL(8,2) DEFAULT 0.00,
    net_amount DECIMAL(10,2) NOT NULL,
    processed_at TIMESTAMP WITH TIME ZONE,
    failed_reason TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- INSERT SAMPLE DATA
-- =====================================================

-- Insert Egyptian governorates
INSERT INTO governorates (name_ar, name_en, code, center_latitude, center_longitude) VALUES
('القاهرة', 'Cairo', 'CAI', 30.0444, 31.2357),
('الجيزة', 'Giza', 'GIZ', 30.0131, 31.2089),
('الإسكندرية', 'Alexandria', 'ALX', 31.2001, 29.9187),
('القليوبية', 'Qalyubia', 'QLY', 30.1792, 31.2045),
('بورسعيد', 'Port Said', 'PTS', 31.2653, 32.3019),
('السويس', 'Suez', 'SUZ', 29.9668, 32.5498),
('دمياط', 'Damietta', 'DMT', 31.4165, 31.8133),
('الدقهلية', 'Dakahlia', 'DKH', 31.1656, 31.4913),
('الشرقية', 'Sharqia', 'SHR', 30.5965, 31.5041),
('كفر الشيخ', 'Kafr El Sheikh', 'KFS', 31.1107, 30.9388),
('الغربية', 'Gharbia', 'GHR', 30.8754, 31.0335),
('المنوفية', 'Monufia', 'MNF', 30.5972, 30.9876),
('البحيرة', 'Beheira', 'BHR', 30.8481, 30.3436),
('الإسماعيلية', 'Ismailia', 'ISM', 30.5903, 32.2722)
ON CONFLICT (code) DO NOTHING;

-- Insert service categories
INSERT INTO service_categories (name_ar, name_en, description_ar, description_en, icon_url, color_code, is_emergency_available, sort_order) VALUES
('السباكة', 'Plumbing', 'خدمات السباكة وإصلاح الأنابيب والحنفيات والمراحيض', 'Plumbing services including pipe repairs, faucets, and toilet fixes', '/icons/plumbing.svg', '#2196F3', true, 1),
('الكهرباء', 'Electrical', 'خدمات الكهرباء والإصلاحات الكهربائية وتركيب الأجهزة', 'Electrical services including repairs, installations, and appliance setup', '/icons/electrical.svg', '#FF9800', true, 2),
('التنظيف', 'Cleaning', 'خدمات التنظيف المنزلي والمكتبي والتنظيف العميق', 'Home and office cleaning services including deep cleaning', '/icons/cleaning.svg', '#4CAF50', false, 3),
('النجارة', 'Carpentry', 'خدمات النجارة وإصلاح الأثاث وصنع الخزائن', 'Carpentry services including furniture repair and cabinet making', '/icons/carpentry.svg', '#795548', false, 4),
('صيانة التكييف', 'AC Maintenance', 'صيانة وإصلاح أجهزة التكييف والتبريد والتهوية', 'Air conditioning maintenance, repair, and ventilation services', '/icons/ac.svg', '#00BCD4', true, 5),
('الدهان', 'Painting', 'خدمات الدهان والديكور وتجديد الجدران', 'Painting and decoration services including wall renovation', '/icons/painting.svg', '#E91E63', false, 6),
('البستنة', 'Gardening', 'خدمات البستنة وتنسيق الحدائق والعناية بالنباتات', 'Gardening and landscaping services including plant care', '/icons/gardening.svg', '#8BC34A', false, 7),
('الأجهزة المنزلية', 'Home Appliances', 'إصلاح وصيانة الأجهزة المنزلية والكهربائية', 'Home appliance repair and maintenance services', '/icons/appliances.svg', '#9C27B0', false, 8)
ON CONFLICT DO NOTHING;

-- Create admin user
INSERT INTO users (email, phone, password_hash, user_type, is_active, is_verified) VALUES
('admin@maintenanceplatform.com', '+201000000000', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/VcSAg/9u2', 'admin', true, true)
ON CONFLICT (email) DO NOTHING;

-- =====================================================
-- SUCCESS MESSAGE
-- =====================================================

-- Display completion summary
SELECT 
    '🎉 Database Schema Created Successfully!' as status,
    COUNT(*) as tables_created
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN (
    'users', 'customer_profiles', 'service_provider_profiles',
    'governorates', 'cities', 'customer_addresses',
    'service_categories', 'services', 'provider_services',
    'provider_locations', 'provider_service_areas', 'provider_documents',
    'bookings', 'booking_status_history', 'booking_locations', 'booking_reviews',
    'notifications', 'payment_transactions'
);

-- Show sample data counts
SELECT 
    'governorates' as table_name, COUNT(*) as sample_records FROM governorates
UNION ALL
SELECT 
    'service_categories' as table_name, COUNT(*) as sample_records FROM service_categories
UNION ALL
SELECT 
    'admin_users' as table_name, COUNT(*) as sample_records FROM users WHERE user_type = 'admin';

