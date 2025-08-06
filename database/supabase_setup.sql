-- Supabase Database Setup Script
-- Maintenance Service Platform

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "postgis";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create custom types
CREATE TYPE user_type AS ENUM ('customer', 'service_provider', 'admin');
CREATE TYPE user_status AS ENUM ('active', 'inactive', 'suspended', 'pending_verification');
CREATE TYPE booking_status AS ENUM ('pending', 'confirmed', 'in_progress', 'completed', 'cancelled');
CREATE TYPE booking_urgency AS ENUM ('normal', 'urgent', 'emergency');
CREATE TYPE provider_verification_status AS ENUM ('pending', 'approved', 'rejected');
CREATE TYPE document_type AS ENUM ('national_id', 'commercial_register', 'tax_card', 'insurance', 'license');

-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    user_type user_type NOT NULL,
    status user_status DEFAULT 'active',
    preferred_language VARCHAR(2) DEFAULT 'en',
    profile_image_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login_at TIMESTAMP WITH TIME ZONE,
    email_verified_at TIMESTAMP WITH TIME ZONE,
    phone_verified_at TIMESTAMP WITH TIME ZONE
);

-- Customer profiles
CREATE TABLE customer_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    date_of_birth DATE,
    gender VARCHAR(10),
    address TEXT,
    governorate VARCHAR(50),
    city VARCHAR(100),
    postal_code VARCHAR(10),
    emergency_contact_name VARCHAR(255),
    emergency_contact_phone VARCHAR(20),
    preferred_payment_method VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Service provider profiles
CREATE TABLE service_provider_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    business_name VARCHAR(255),
    business_description TEXT,
    years_of_experience INTEGER,
    verification_status provider_verification_status DEFAULT 'pending',
    verification_notes TEXT,
    verified_at TIMESTAMP WITH TIME ZONE,
    verified_by UUID REFERENCES users(id),
    rating DECIMAL(3,2) DEFAULT 0.00,
    total_reviews INTEGER DEFAULT 0,
    total_bookings INTEGER DEFAULT 0,
    is_available BOOLEAN DEFAULT true,
    service_radius INTEGER DEFAULT 10, -- in kilometers
    hourly_rate DECIMAL(10,2),
    emergency_rate_multiplier DECIMAL(3,2) DEFAULT 1.5,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Service categories
CREATE TABLE service_categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name_en VARCHAR(255) NOT NULL,
    name_ar VARCHAR(255) NOT NULL,
    description_en TEXT,
    description_ar TEXT,
    icon VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Services
CREATE TABLE services (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    category_id UUID REFERENCES service_categories(id) ON DELETE CASCADE,
    name_en VARCHAR(255) NOT NULL,
    name_ar VARCHAR(255) NOT NULL,
    description_en TEXT,
    description_ar TEXT,
    base_price DECIMAL(10,2),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Provider services (many-to-many relationship)
CREATE TABLE provider_services (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    provider_id UUID REFERENCES service_provider_profiles(id) ON DELETE CASCADE,
    service_id UUID REFERENCES services(id) ON DELETE CASCADE,
    custom_price DECIMAL(10,2),
    is_available BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(provider_id, service_id)
);

-- Provider service areas
CREATE TABLE provider_service_areas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    provider_id UUID REFERENCES service_provider_profiles(id) ON DELETE CASCADE,
    governorate VARCHAR(50) NOT NULL,
    city VARCHAR(100),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Bookings
CREATE TABLE bookings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID REFERENCES users(id) ON DELETE CASCADE,
    provider_id UUID REFERENCES users(id) ON DELETE SET NULL,
    service_category_id UUID REFERENCES service_categories(id),
    service_id UUID REFERENCES services(id),
    description TEXT NOT NULL,
    status booking_status DEFAULT 'pending',
    urgency booking_urgency DEFAULT 'normal',
    preferred_date DATE NOT NULL,
    preferred_time TIME NOT NULL,
    estimated_duration INTEGER, -- in hours
    estimated_price DECIMAL(10,2),
    final_price DECIMAL(10,2),
    emergency_fee DECIMAL(10,2) DEFAULT 0.00,
    platform_fee DECIMAL(10,2) DEFAULT 0.00,
    notes TEXT,
    customer_notes TEXT,
    provider_notes TEXT,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    cancelled_at TIMESTAMP WITH TIME ZONE,
    cancellation_reason TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Booking locations
CREATE TABLE booking_locations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    booking_id UUID REFERENCES bookings(id) ON DELETE CASCADE,
    address TEXT NOT NULL,
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    governorate VARCHAR(50) NOT NULL,
    city VARCHAR(100),
    postal_code VARCHAR(10),
    building_number VARCHAR(50),
    floor_number VARCHAR(10),
    apartment_number VARCHAR(10),
    landmark TEXT,
    access_instructions TEXT,
    location_point GEOMETRY(POINT, 4326),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Booking status history
CREATE TABLE booking_status_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    booking_id UUID REFERENCES bookings(id) ON DELETE CASCADE,
    status booking_status NOT NULL,
    changed_by UUID REFERENCES users(id),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Provider locations (for tracking)
CREATE TABLE provider_locations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    provider_id UUID REFERENCES users(id) ON DELETE CASCADE,
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    accuracy DECIMAL(8, 2),
    speed DECIMAL(8, 2),
    heading DECIMAL(5, 2),
    location_point GEOMETRY(POINT, 4326),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Reviews and ratings
CREATE TABLE booking_reviews (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    booking_id UUID REFERENCES bookings(id) ON DELETE CASCADE,
    customer_id UUID REFERENCES users(id) ON DELETE CASCADE,
    provider_id UUID REFERENCES users(id) ON DELETE CASCADE,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    review_text TEXT,
    service_quality_rating INTEGER CHECK (service_quality_rating >= 1 AND service_quality_rating <= 5),
    punctuality_rating INTEGER CHECK (punctuality_rating >= 1 AND punctuality_rating <= 5),
    professionalism_rating INTEGER CHECK (professionalism_rating >= 1 AND professionalism_rating <= 5),
    value_for_money_rating INTEGER CHECK (value_for_money_rating >= 1 AND value_for_money_rating <= 5),
    would_recommend BOOLEAN,
    is_public BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Provider documents
CREATE TABLE provider_documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    provider_id UUID REFERENCES service_provider_profiles(id) ON DELETE CASCADE,
    document_type document_type NOT NULL,
    document_url TEXT NOT NULL,
    document_number VARCHAR(255),
    expiry_date DATE,
    is_verified BOOLEAN DEFAULT false,
    verified_at TIMESTAMP WITH TIME ZONE,
    verified_by UUID REFERENCES users(id),
    verification_notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Notifications
CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    type VARCHAR(50) NOT NULL,
    data JSONB,
    is_read BOOLEAN DEFAULT false,
    read_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Payment transactions
CREATE TABLE payment_transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    booking_id UUID REFERENCES bookings(id) ON DELETE CASCADE,
    customer_id UUID REFERENCES users(id) ON DELETE CASCADE,
    provider_id UUID REFERENCES users(id) ON DELETE CASCADE,
    amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'EGP',
    payment_method VARCHAR(50) NOT NULL,
    payment_gateway VARCHAR(50),
    gateway_transaction_id VARCHAR(255),
    status VARCHAR(50) DEFAULT 'pending',
    paid_at TIMESTAMP WITH TIME ZONE,
    refunded_at TIMESTAMP WITH TIME ZONE,
    refund_amount DECIMAL(10,2),
    gateway_response JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_phone ON users(phone);
CREATE INDEX idx_users_type ON users(user_type);
CREATE INDEX idx_users_status ON users(status);

CREATE INDEX idx_bookings_customer ON bookings(customer_id);
CREATE INDEX idx_bookings_provider ON bookings(provider_id);
CREATE INDEX idx_bookings_status ON bookings(status);
CREATE INDEX idx_bookings_date ON bookings(preferred_date);
CREATE INDEX idx_bookings_created ON bookings(created_at);

CREATE INDEX idx_provider_locations_provider ON provider_locations(provider_id);
CREATE INDEX idx_provider_locations_created ON provider_locations(created_at);
CREATE INDEX idx_provider_locations_point ON provider_locations USING GIST(location_point);

CREATE INDEX idx_booking_locations_point ON booking_locations USING GIST(location_point);
CREATE INDEX idx_booking_locations_booking ON booking_locations(booking_id);

CREATE INDEX idx_notifications_user ON notifications(user_id);
CREATE INDEX idx_notifications_read ON notifications(is_read);
CREATE INDEX idx_notifications_created ON notifications(created_at);

CREATE INDEX idx_reviews_provider ON booking_reviews(provider_id);
CREATE INDEX idx_reviews_booking ON booking_reviews(booking_id);
CREATE INDEX idx_reviews_rating ON booking_reviews(rating);

-- Create triggers for updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_customer_profiles_updated_at BEFORE UPDATE ON customer_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_service_provider_profiles_updated_at BEFORE UPDATE ON service_provider_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_bookings_updated_at BEFORE UPDATE ON bookings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create trigger to update location_point when lat/lng changes
CREATE OR REPLACE FUNCTION update_location_point()
RETURNS TRIGGER AS $$
BEGIN
    NEW.location_point = ST_SetSRID(ST_MakePoint(NEW.longitude, NEW.latitude), 4326);
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_provider_locations_point BEFORE INSERT OR UPDATE ON provider_locations
    FOR EACH ROW EXECUTE FUNCTION update_location_point();

CREATE TRIGGER update_booking_locations_point BEFORE INSERT OR UPDATE ON booking_locations
    FOR EACH ROW EXECUTE FUNCTION update_location_point();

-- Row Level Security (RLS) Policies
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE customer_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE service_provider_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE bookings ENABLE ROW LEVEL SECURITY;
ALTER TABLE booking_locations ENABLE ROW LEVEL SECURITY;
ALTER TABLE provider_locations ENABLE ROW LEVEL SECURITY;
ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE booking_reviews ENABLE ROW LEVEL SECURITY;

-- Users can only see their own data
CREATE POLICY "Users can view own profile" ON users
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON users
    FOR UPDATE USING (auth.uid() = id);

-- Customer profiles
CREATE POLICY "Customers can view own profile" ON customer_profiles
    FOR ALL USING (auth.uid() = user_id);

-- Service provider profiles
CREATE POLICY "Providers can view own profile" ON service_provider_profiles
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Public can view verified providers" ON service_provider_profiles
    FOR SELECT USING (verification_status = 'approved');

-- Bookings
CREATE POLICY "Customers can view own bookings" ON bookings
    FOR SELECT USING (auth.uid() = customer_id);

CREATE POLICY "Providers can view assigned bookings" ON bookings
    FOR SELECT USING (auth.uid() = provider_id);

CREATE POLICY "Customers can create bookings" ON bookings
    FOR INSERT WITH CHECK (auth.uid() = customer_id);

CREATE POLICY "Providers can update assigned bookings" ON bookings
    FOR UPDATE USING (auth.uid() = provider_id);

-- Notifications
CREATE POLICY "Users can view own notifications" ON notifications
    FOR ALL USING (auth.uid() = user_id);

-- Insert sample data
INSERT INTO service_categories (name_en, name_ar, description_en, description_ar, icon) VALUES
('Plumbing', 'السباكة', 'Professional plumbing services', 'خدمات السباكة المهنية', 'plumbing'),
('Electrical', 'الكهرباء', 'Electrical installation and repair', 'تركيب وإصلاح الكهرباء', 'electrical'),
('Air Conditioning', 'تكييف الهواء', 'AC installation and maintenance', 'تركيب وصيانة التكييف', 'ac'),
('Carpentry', 'النجارة', 'Wood work and furniture repair', 'أعمال الخشب وإصلاح الأثاث', 'carpentry'),
('Painting', 'الدهان', 'Interior and exterior painting', 'دهان داخلي وخارجي', 'painting'),
('Cleaning', 'التنظيف', 'Professional cleaning services', 'خدمات التنظيف المهنية', 'cleaning'),
('Appliance Repair', 'إصلاح الأجهزة', 'Home appliance repair and maintenance', 'إصلاح وصيانة الأجهزة المنزلية', 'appliance'),
('Pest Control', 'مكافحة الحشرات', 'Professional pest control services', 'خدمات مكافحة الحشرات المهنية', 'pest');

-- Insert sample services
INSERT INTO services (category_id, name_en, name_ar, description_en, description_ar, base_price) 
SELECT 
    sc.id,
    'Pipe Repair',
    'إصلاح الأنابيب',
    'Fix leaking or broken pipes',
    'إصلاح الأنابيب المتسربة أو المكسورة',
    150.00
FROM service_categories sc WHERE sc.name_en = 'Plumbing';

INSERT INTO services (category_id, name_en, name_ar, description_en, description_ar, base_price) 
SELECT 
    sc.id,
    'Electrical Wiring',
    'التوصيلات الكهربائية',
    'Install or repair electrical wiring',
    'تركيب أو إصلاح التوصيلات الكهربائية',
    200.00
FROM service_categories sc WHERE sc.name_en = 'Electrical';

-- Create admin user (password: Admin123!)
INSERT INTO users (email, phone, password_hash, full_name, user_type, status, email_verified_at, phone_verified_at)
VALUES (
    'admin@maintenanceplatform.com',
    '+201000000000',
    'scrypt:32768:8:1$aOmKNOOoqaHynG8w$0f55188e3657ff46a6ff8d9a6d50f16ec91914748b8d57fd64dd0f98576c4b91065c2cc5a2e9bcf01bdb60090cb58a56088e41e6c90123232550f0304b4e795d',
    'Platform Administrator',
    'admin',
    'active',
    NOW(),
    NOW()
);

COMMIT;

