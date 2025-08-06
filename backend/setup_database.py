#!/usr/bin/env python3
"""
Supabase Database Setup Script for Maintenance Platform
"""

import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env')

def setup_database():
    print('🚀 Setting up Maintenance Platform database...')
    print(f'📊 Database URL: {os.getenv("DATABASE_URL", "Not found")[:50]}...')
    
    try:
        # Connect to database
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        cursor = conn.cursor()
        
        print('✅ Database connection successful!')
        
        # Create tables
        print('📝 Creating database tables...')
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                email VARCHAR(255) UNIQUE NOT NULL,
                phone VARCHAR(20) UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                user_type VARCHAR(20) NOT NULL CHECK (user_type IN ('customer', 'service_provider', 'admin')),
                is_active BOOLEAN DEFAULT true,
                is_verified BOOLEAN DEFAULT false,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        ''')
        
        # Customer profiles table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS customer_profiles (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                first_name VARCHAR(100) NOT NULL,
                last_name VARCHAR(100) NOT NULL,
                date_of_birth DATE,
                profile_image_url TEXT,
                preferred_language VARCHAR(10) DEFAULT 'ar',
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        ''')
        
        # Service provider profiles table
        cursor.execute('''
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
                verification_status VARCHAR(20) DEFAULT 'pending' CHECK (verification_status IN ('pending', 'verified', 'rejected')),
                is_available BOOLEAN DEFAULT true,
                average_rating DECIMAL(3,2) DEFAULT 0.00,
                total_reviews INTEGER DEFAULT 0,
                total_completed_jobs INTEGER DEFAULT 0,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        ''')
        
        # Service categories table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS service_categories (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                name_ar VARCHAR(100) NOT NULL,
                name_en VARCHAR(100) NOT NULL,
                description_ar TEXT,
                description_en TEXT,
                icon_url TEXT,
                is_active BOOLEAN DEFAULT true,
                sort_order INTEGER DEFAULT 0,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        ''')
        
        # Services table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS services (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                category_id UUID NOT NULL REFERENCES service_categories(id) ON DELETE CASCADE,
                name_ar VARCHAR(200) NOT NULL,
                name_en VARCHAR(200) NOT NULL,
                description_ar TEXT,
                description_en TEXT,
                base_price DECIMAL(10,2) NOT NULL,
                price_unit VARCHAR(20) DEFAULT 'fixed',
                estimated_duration INTEGER,
                is_active BOOLEAN DEFAULT true,
                is_emergency_service BOOLEAN DEFAULT false,
                emergency_surcharge_percentage DECIMAL(5,2) DEFAULT 0.00,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        ''')
        
        # Governorates table
        cursor.execute('''
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
        ''')
        
        # Bookings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bookings (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                customer_id UUID NOT NULL REFERENCES users(id),
                provider_id UUID NOT NULL REFERENCES users(id),
                service_id UUID NOT NULL REFERENCES services(id),
                booking_date DATE NOT NULL,
                booking_time TIME NOT NULL,
                status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'confirmed', 'in_progress', 'completed', 'cancelled')),
                total_amount DECIMAL(10,2) NOT NULL,
                payment_status VARCHAR(20) DEFAULT 'pending' CHECK (payment_status IN ('pending', 'paid', 'refunded')),
                address_line1 VARCHAR(255) NOT NULL,
                address_line2 VARCHAR(255),
                city VARCHAR(100) NOT NULL,
                governorate VARCHAR(100) NOT NULL,
                postal_code VARCHAR(20),
                latitude DECIMAL(10,8),
                longitude DECIMAL(11,8),
                notes TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        ''')
        
        print('✅ Core tables created successfully!')
        
        # Insert sample data
        print('📊 Creating sample data...')
        
        # Check if sample data exists
        cursor.execute("SELECT COUNT(*) FROM service_categories")
        count = cursor.fetchone()[0]
        
        if count == 0:
            # Service categories
            categories = [
                ('السباكة', 'Plumbing', 'خدمات السباكة وإصلاح الأنابيب والحنفيات', 'Plumbing services and pipe repairs', '/icons/plumbing.svg', 1),
                ('الكهرباء', 'Electrical', 'خدمات الكهرباء والإصلاحات الكهربائية', 'Electrical services and repairs', '/icons/electrical.svg', 2),
                ('التنظيف', 'Cleaning', 'خدمات التنظيف المنزلي والمكتبي', 'Home and office cleaning services', '/icons/cleaning.svg', 3),
                ('النجارة', 'Carpentry', 'خدمات النجارة وإصلاح الأثاث', 'Carpentry and furniture repair services', '/icons/carpentry.svg', 4),
                ('صيانة التكييف', 'AC Maintenance', 'صيانة وإصلاح أجهزة التكييف والتبريد', 'Air conditioning maintenance and repair', '/icons/ac.svg', 5),
                ('الدهان', 'Painting', 'خدمات الدهان والديكور', 'Painting and decoration services', '/icons/painting.svg', 6)
            ]
            
            for cat in categories:
                cursor.execute('''
                    INSERT INTO service_categories (name_ar, name_en, description_ar, description_en, icon_url, sort_order)
                    VALUES (%s, %s, %s, %s, %s, %s)
                ''', cat)
            
            # Egyptian governorates
            governorates = [
                ('القاهرة', 'Cairo', 'CAI', 30.0444, 31.2357),
                ('الجيزة', 'Giza', 'GIZ', 30.0131, 31.2089),
                ('الإسكندرية', 'Alexandria', 'ALX', 31.2001, 29.9187),
                ('القليوبية', 'Qalyubia', 'QLY', 30.1792, 31.2045),
                ('بورسعيد', 'Port Said', 'PTS', 31.2653, 32.3019)
            ]
            
            for gov in governorates:
                cursor.execute('''
                    INSERT INTO governorates (name_ar, name_en, code, center_latitude, center_longitude)
                    VALUES (%s, %s, %s, %s, %s)
                ''', gov)
            
            print('✅ Sample data created successfully!')
        else:
            print('ℹ️  Sample data already exists, skipping creation.')
        
        # Commit changes
        conn.commit()
        
        print('\n🎉 Database setup completed successfully!')
        print('📊 Tables created:')
        print('   - users')
        print('   - customer_profiles')
        print('   - service_provider_profiles')
        print('   - service_categories')
        print('   - services')
        print('   - governorates')
        print('   - bookings')
        
        print(f'\n🔗 Your database is ready at: {os.getenv("SUPABASE_URL")}')
        print('🚀 You can now start the backend server and test the API!')
        
        # Close connection
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f'❌ Database setup failed: {e}')
        print('Please check your database connection and try again.')

if __name__ == '__main__':
    setup_database()

