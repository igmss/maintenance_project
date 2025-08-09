#!/usr/bin/env python3
"""
Fix existing service providers by adding default location data
This script adds default Cairo locations for providers who don't have any location entries
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from backend.src.models import db
from backend.src.models.user import ServiceProviderProfile
from backend.src.models.location import ProviderLocation, ProviderServiceArea
from backend.src.main import create_app
from datetime import datetime

def fix_existing_providers():
    """Add default locations for existing providers without location data"""
    app = create_app()
    
    with app.app_context():
        print("🔧 Fixing existing service providers without location data...")
        print("=" * 60)
        
        # Find providers without location data
        providers_without_location = db.session.query(ServiceProviderProfile).filter(
            ~ServiceProviderProfile.id.in_(
                db.session.query(ProviderLocation.provider_id).distinct()
            )
        ).all()
        
        print(f"📊 Found {len(providers_without_location)} providers without location data")
        
        if len(providers_without_location) == 0:
            print("✅ All providers already have location data!")
            return
        
        # Default Cairo coordinates (can be customized)
        default_locations = [
            {"lat": 30.0444, "lng": 31.2357, "area": "Cairo - Downtown"},
            {"lat": 30.0626, "lng": 31.2497, "area": "Cairo - Nasr City"},
            {"lat": 30.0131, "lng": 31.2089, "area": "Giza - Dokki"},
            {"lat": 30.0254, "lng": 31.4970, "area": "Cairo - New Cairo"},
            {"lat": 31.2001, "lng": 29.9187, "area": "Alexandria - Center"},
        ]
        
        created_locations = 0
        created_service_areas = 0
        
        for i, provider in enumerate(providers_without_location):
            try:
                # Use different default locations to spread providers around
                location_data = default_locations[i % len(default_locations)]
                
                print(f"   Adding location for provider {provider.id} ({provider.business_name or 'Unnamed'})")
                
                # Create default location entry
                location = ProviderLocation(
                    provider_id=provider.id,
                    latitude=location_data["lat"],
                    longitude=location_data["lng"],
                    accuracy=10.0,
                    is_online=True,
                    battery_level=100
                )
                db.session.add(location)
                created_locations += 1
                
                # Create default service area
                service_area = ProviderServiceArea(
                    provider_id=provider.id,
                    area_name=location_data["area"],
                    center_latitude=location_data["lat"],
                    center_longitude=location_data["lng"],
                    radius_km=provider.service_radius or 15.0,
                    is_primary_area=True,
                    travel_time_minutes=30
                )
                db.session.add(service_area)
                created_service_areas += 1
                
                # Update provider availability
                provider.is_available = True
                
            except Exception as e:
                print(f"   ❌ Error adding location for provider {provider.id}: {e}")
                continue
        
        # Commit all changes
        try:
            db.session.commit()
            print(f"\n✅ Successfully created:")
            print(f"   📍 {created_locations} provider locations")
            print(f"   🗺️  {created_service_areas} service areas")
            print(f"   🔄 Updated {len(providers_without_location)} providers")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error saving changes: {e}")

def verify_fix():
    """Verify that the fix worked"""
    app = create_app()
    
    with app.app_context():
        total_providers = ServiceProviderProfile.query.count()
        providers_with_locations = db.session.query(ProviderLocation.provider_id).distinct().count()
        providers_with_areas = db.session.query(ProviderServiceArea.provider_id).distinct().count()
        
        print(f"\n📊 Results after fix:")
        print(f"   👥 Total providers: {total_providers}")
        print(f"   📍 Providers with locations: {providers_with_locations}")
        print(f"   🗺️  Providers with service areas: {providers_with_areas}")
        
        if providers_with_locations == total_providers:
            print("✅ All providers now have location data!")
        else:
            print(f"⚠️  Still missing locations for {total_providers - providers_with_locations} providers")

if __name__ == "__main__":
    print("🚀 Starting provider location fix...")
    fix_existing_providers()
    verify_fix()
    print("\n🎉 Provider location fix completed!")