from flask import Blueprint, request, jsonify
from datetime import datetime
from src.models import db
from src.models.user import User
from src.models.location import CustomerLocation, ProviderLocation
from src.models.service import ServiceProviderProfile, ProviderService
from src.utils.auth import customer_required
from src.utils.location import validate_coordinates, calculate_distance
from sqlalchemy import and_, func

customers_bp = Blueprint('customers', __name__)

@customers_bp.route('/location', methods=['POST'])
@customer_required
def update_customer_location(current_user):
    """Update customer live location"""
    try:
        data = request.get_json()
        
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        
        if not latitude or not longitude:
            return jsonify({'error': 'Latitude and longitude are required'}), 400
        
        if not validate_coordinates(float(latitude), float(longitude)):
            return jsonify({'error': 'Invalid coordinates for Egypt'}), 400
        
        # Update or create customer location
        customer_location = CustomerLocation.query.filter_by(
            customer_id=current_user.id,
            is_active=True
        ).first()
        
        if customer_location:
            # Update existing location
            customer_location.latitude = float(latitude)
            customer_location.longitude = float(longitude)
            customer_location.accuracy = data.get('accuracy', customer_location.accuracy)
            customer_location.formatted_address = data.get('formatted_address', customer_location.formatted_address)
            customer_location.address_components = data.get('address_components', customer_location.address_components)
            customer_location.last_updated = datetime.utcnow()
        else:
            # Create new location
            customer_location = CustomerLocation(
                customer_id=current_user.id,
                latitude=float(latitude),
                longitude=float(longitude),
                accuracy=data.get('accuracy', 10.0),
                formatted_address=data.get('formatted_address'),
                address_components=data.get('address_components'),
                is_active=True
            )
            db.session.add(customer_location)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Customer location updated successfully',
            'location': customer_location.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@customers_bp.route('/nearby-providers', methods=['POST'])
@customer_required
def get_nearby_providers(current_user):
    """Get nearby online providers for a specific service"""
    try:
        data = request.get_json()
        
        service_id = data.get('service_id')
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        max_distance_km = data.get('max_distance_km', 25)
        
        if not service_id:
            return jsonify({'error': 'service_id is required'}), 400
        
        if not latitude or not longitude:
            return jsonify({'error': 'latitude and longitude are required'}), 400
        
        # Find providers who offer this service
        provider_services = ProviderService.query.filter_by(
            service_id=service_id,
            is_active=True
        ).all()
        
        provider_ids = [ps.provider_id for ps in provider_services]
        
        if not provider_ids:
            return jsonify({'providers': []}), 200
        
        # Get online providers with recent locations
        online_providers = db.session.query(
            ServiceProviderProfile,
            ProviderLocation
        ).join(
            ProviderLocation, 
            and_(
                ProviderLocation.provider_id == ServiceProviderProfile.user_id,
                ProviderLocation.is_online == True
            )
        ).filter(
            ServiceProviderProfile.id.in_(provider_ids),
            ServiceProviderProfile.is_available == True,
            ServiceProviderProfile.verification_status == 'approved'
        ).all()
        
        # Calculate distances and filter by max distance
        nearby_providers = []
        customer_lat = float(latitude)
        customer_lng = float(longitude)
        
        for provider_profile, provider_location in online_providers:
            provider_lat = float(provider_location.latitude)
            provider_lng = float(provider_location.longitude)
            
            distance = calculate_distance(
                customer_lat, customer_lng,
                provider_lat, provider_lng
            )
            
            if distance <= max_distance_km:
                provider_data = provider_profile.to_dict()
                provider_data['distance_km'] = round(distance, 2)
                provider_data['current_location'] = {
                    'latitude': provider_lat,
                    'longitude': provider_lng,
                    'last_updated': provider_location.last_updated.isoformat()
                }
                nearby_providers.append(provider_data)
        
        # Sort by distance
        nearby_providers.sort(key=lambda x: x['distance_km'])
        
        return jsonify({
            'providers': nearby_providers,
            'total_count': len(nearby_providers),
            'search_center': {
                'latitude': customer_lat,
                'longitude': customer_lng
            },
            'max_distance_km': max_distance_km
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@customers_bp.route('/location', methods=['GET'])
@customer_required
def get_customer_location(current_user):
    """Get customer's current location"""
    try:
        customer_location = CustomerLocation.query.filter_by(
            customer_id=current_user.id,
            is_active=True
        ).first()
        
        if not customer_location:
            return jsonify({'location': None}), 200
        
        return jsonify({
            'location': customer_location.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500