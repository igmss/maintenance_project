#!/usr/bin/env python3
"""
Script to analyze differences between expected backend models and actual database schema
"""

import requests
import json

# Expected schema based on backend models
EXPECTED_SCHEMA = {
    'users': {
        'id': 'string(36)',
        'email': 'string(255)',
        'phone': 'string(20)',
        'password_hash': 'string(255)',
        'user_type': 'string(20)',
        'is_active': 'boolean',
        'is_verified': 'boolean',
        'email_verified_at': 'datetime',
        'phone_verified_at': 'datetime',
        'last_login_at': 'datetime',
        'created_at': 'datetime',
        'updated_at': 'datetime'
    },
    'customer_profiles': {
        'id': 'string(36)',
        'user_id': 'string(36)',
        'first_name': 'string(100)',
        'last_name': 'string(100)',
        'date_of_birth': 'date',
        'gender': 'enum',
        'profile_image_url': 'text',
        'preferred_language': 'string(5)',
        'notification_preferences': 'json',
        'created_at': 'datetime',
        'updated_at': 'datetime'
    },
    'service_provider_profiles': {
        'id': 'string(36)',
        'user_id': 'string(36)',
        'business_name': 'string(200)',
        'first_name': 'string(100)',
        'last_name': 'string(100)',
        'business_license': 'string(100)',
        'tax_id': 'string(50)',
        'profile_image_url': 'text',
        'bio_ar': 'text',
        'bio_en': 'text',
        'business_description': 'text',
        'years_of_experience': 'integer',
        'verification_status': 'string(20)',
        'verification_date': 'datetime',
        'verification_notes': 'text',
        'verified_at': 'datetime',
        'verified_by': 'string(36)',
        'is_available': 'boolean',
        'average_rating': 'numeric(3,2)',
        'rating': 'numeric(3,2)',
        'total_reviews': 'integer',
        'total_bookings': 'integer',
        'total_completed_jobs': 'integer',
        'total_earnings': 'numeric(12,2)',
        'commission_rate': 'numeric(5,2)',
        'service_radius': 'integer',
        'hourly_rate': 'numeric(10,2)',
        'emergency_rate_multiplier': 'numeric(3,2)',
        'created_at': 'datetime',
        'updated_at': 'datetime'
    },
    'service_categories': {
        'id': 'string(36)',
        'name_ar': 'string(200)',
        'name_en': 'string(200)',
        'description_ar': 'text',
        'description_en': 'text',
        'icon_url': 'text',
        'is_active': 'boolean',
        'sort_order': 'integer',
        'created_at': 'datetime',
        'updated_at': 'datetime'
    },
    'services': {
        'id': 'string(36)',
        'category_id': 'string(36)',
        'name_ar': 'string(200)',
        'name_en': 'string(200)',
        'description_ar': 'text',
        'description_en': 'text',
        'base_price': 'numeric(10,2)',
        'price_unit': 'string(20)',  # This is missing!
        'estimated_duration': 'integer',  # This is missing!
        'is_active': 'boolean',
        'is_emergency_service': 'boolean',  # This is missing!
        'emergency_surcharge_percentage': 'numeric(5,2)',  # This is missing!
        'requires_materials': 'boolean',  # This is missing!
        'created_at': 'datetime',
        'updated_at': 'datetime'
    },
    'provider_services': {
        'id': 'string(36)',
        'provider_id': 'string(36)',
        'service_id': 'string(36)',
        'custom_price': 'numeric(10,2)',
        'is_available': 'boolean',
        'experience_years': 'integer',  # This might be missing!
        'created_at': 'datetime',
        'updated_at': 'datetime'
    }
}

def analyze_differences():
    print("🔍 Expected Backend Models vs Database Schema Analysis")
    print("=" * 60)
    
    print("\n📋 STEP 1: Run this query in Supabase SQL Editor:")
    print("-" * 50)
    with open('check_database_schema.sql', 'r') as f:
        print(f.read())
    
    print("\n📋 STEP 2: Critical Missing Columns (based on error messages):")
    print("-" * 50)
    
    missing_columns = {
        'users': ['is_active', 'is_verified', 'email_verified_at', 'phone_verified_at', 'last_login_at'],
        'services': ['price_unit', 'estimated_duration', 'is_emergency_service', 'emergency_surcharge_percentage', 'requires_materials'],
        'provider_services': ['experience_years']
    }
    
    for table, columns in missing_columns.items():
        print(f"\n{table.upper()} table missing:")
        for col in columns:
            expected_type = EXPECTED_SCHEMA[table].get(col, 'unknown')
            print(f"  ❌ {col} ({expected_type})")
    
    print("\n📋 STEP 3: Generate Migration SQL:")
    print("-" * 50)
    
    migration_sql = []
    
    # Users table
    migration_sql.append("-- Fix users table")
    migration_sql.append("ALTER TABLE users")
    migration_sql.append("ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT true,")
    migration_sql.append("ADD COLUMN IF NOT EXISTS is_verified BOOLEAN DEFAULT false,")
    migration_sql.append("ADD COLUMN IF NOT EXISTS email_verified_at TIMESTAMP WITH TIME ZONE,")
    migration_sql.append("ADD COLUMN IF NOT EXISTS phone_verified_at TIMESTAMP WITH TIME ZONE,")
    migration_sql.append("ADD COLUMN IF NOT EXISTS last_login_at TIMESTAMP WITH TIME ZONE;")
    migration_sql.append("")
    
    # Services table
    migration_sql.append("-- Fix services table")
    migration_sql.append("ALTER TABLE services")
    migration_sql.append("ADD COLUMN IF NOT EXISTS price_unit VARCHAR(20) DEFAULT 'fixed',")
    migration_sql.append("ADD COLUMN IF NOT EXISTS estimated_duration INTEGER,")
    migration_sql.append("ADD COLUMN IF NOT EXISTS is_emergency_service BOOLEAN DEFAULT false,")
    migration_sql.append("ADD COLUMN IF NOT EXISTS emergency_surcharge_percentage DECIMAL(5,2) DEFAULT 0.00,")
    migration_sql.append("ADD COLUMN IF NOT EXISTS requires_materials BOOLEAN DEFAULT false;")
    migration_sql.append("")
    
    # Provider services table
    migration_sql.append("-- Fix provider_services table")
    migration_sql.append("ALTER TABLE provider_services")
    migration_sql.append("ADD COLUMN IF NOT EXISTS experience_years INTEGER DEFAULT 0;")
    
    for line in migration_sql:
        print(line)
    
    print("\n📋 STEP 4: After running migration, test with:")
    print("-" * 50)
    print("python test_after_migration.py")
    
    return migration_sql

if __name__ == "__main__":
    analyze_differences()