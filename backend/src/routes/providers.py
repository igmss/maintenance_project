from flask import Blueprint, request, jsonify
from datetime import datetime
from src.models import db
from src.models.user import ServiceProviderProfile, ProviderDocument
from src.models.service import ProviderService, Service
from src.models.location import ProviderLocation, ProviderServiceArea
from src.utils.auth import token_required, provider_required, admin_required
from src.utils.location import validate_coordinates

providers_bp = Blueprint('providers', __name__)

@providers_bp.route('/profile', methods=['GET'])
@provider_required
def get_provider_profile(current_user):
    """Get service provider profile with services and areas"""
    try:
        provider = current_user.provider_profile
        
        # Get provider services
        provider_services = ProviderService.query.filter_by(
            provider_id=provider.id,
            is_active=True
        ).all()
        
        # Get service areas
        service_areas = ProviderServiceArea.query.filter_by(
            provider_id=provider.id
        ).all()
        
        # Get current location
        current_location = ProviderLocation.query.filter_by(
            provider_id=provider.id
        ).order_by(ProviderLocation.last_updated.desc()).first()
        
        # Get documents
        documents = ProviderDocument.query.filter_by(
            provider_id=provider.id
        ).all()
        
        profile_data = provider.to_dict()
        profile_data.update({
            'services': [ps.to_dict() for ps in provider_services],
            'service_areas': [sa.to_dict() for sa in service_areas],
            'current_location': current_location.to_dict() if current_location else None,
            'documents': [doc.to_dict() for doc in documents]
        })
        
        return jsonify({
            'profile': profile_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@providers_bp.route('/services', methods=['POST'])
@provider_required
def add_provider_service(current_user):
    """Add a service to provider's offerings"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if 'service_id' not in data:
            return jsonify({'error': 'service_id is required'}), 400
        
        # Validate service exists
        service = Service.query.get_or_404(data['service_id'])
        
        # Check if provider already offers this service
        existing = ProviderService.query.filter_by(
            provider_id=current_user.provider_profile.id,
            service_id=data['service_id']
        ).first()
        
        if existing:
            return jsonify({'error': 'Service already added to your offerings'}), 409
        
        # Create provider service
        provider_service = ProviderService(
            provider_id=current_user.provider_profile.id,
            service_id=data['service_id'],
            custom_price=data.get('custom_price'),
            experience_years=data.get('experience_years', 0),
            is_available=data.get('is_available', True),
            is_active=data.get('is_active', True)
        )
        
        db.session.add(provider_service)
        db.session.commit()
        
        return jsonify({
            'message': 'Service added successfully',
            'provider_service': provider_service.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@providers_bp.route('/services/<provider_service_id>', methods=['PUT'])
@provider_required
def update_provider_service(current_user, provider_service_id):
    """Update provider service details"""
    try:
        data = request.get_json()
        
        provider_service = ProviderService.query.get_or_404(provider_service_id)
        
        # Check ownership
        if provider_service.provider_id != current_user.provider_profile.id:
            return jsonify({'error': 'Access denied'}), 403
        
        # Update fields
        if 'custom_price' in data:
            provider_service.custom_price = data['custom_price']
        if 'experience_years' in data:
            provider_service.experience_years = data['experience_years']
        if 'is_available' in data:
            provider_service.is_available = data['is_available']
        if 'is_active' in data:
            provider_service.is_active = data['is_active']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Service updated successfully',
            'provider_service': provider_service.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@providers_bp.route('/location', methods=['POST'])
@provider_required
def update_location(current_user):
    """Update provider's current location and online status"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['latitude', 'longitude']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        
        # Validate coordinates
        if not validate_coordinates(latitude, longitude):
            return jsonify({'error': 'Invalid coordinates for Egypt'}), 400
        
        # Get online status (default to True if not provided)
        is_online = data.get('is_online', True)
        
        # Create new location entry with online status
        location = ProviderLocation(
            provider_id=current_user.provider_profile.id,
            latitude=latitude,
            longitude=longitude,
            accuracy=data.get('accuracy'),
            heading=data.get('heading'),
            speed=data.get('speed'),
            is_online=is_online
        )
        
        db.session.add(location)
        
        # Update provider availability status
        provider = current_user.provider_profile
        provider.is_available = is_online
        provider.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Location and status updated successfully',
            'location': {
                'id': str(location.id),
                'latitude': location.latitude,
                'longitude': location.longitude,
                'is_online': location.is_online,
                'timestamp': location.created_at.isoformat()
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Toggle provider online/offline status
@providers_bp.route('/status', methods=['POST'])
@provider_required
def toggle_online_status(current_user):
    """Toggle provider online/offline status"""
    try:
        data = request.get_json()
        
        is_online = data.get('is_online', True)
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        
        # If going online, location is required
        if is_online and (not latitude or not longitude):
            return jsonify({'error': 'Location is required when going online'}), 400
        
        # Update all existing locations for this provider to offline first
        ProviderLocation.query.filter_by(
            provider_id=current_user.provider_profile.id
        ).update({'is_online': False})
        
        # If going online with new location, create new location record
        if is_online and latitude and longitude:
            if not validate_coordinates(float(latitude), float(longitude)):
                return jsonify({'error': 'Invalid coordinates for Egypt'}), 400
                
            location = ProviderLocation(
                provider_id=current_user.provider_profile.id,
                latitude=float(latitude),
                longitude=float(longitude),
                is_online=True
            )
            db.session.add(location)
        
        # Update provider profile availability
        provider = current_user.provider_profile
        provider.is_available = is_online
        provider.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': f'Provider status updated to {"online" if is_online else "offline"}',
            'is_online': is_online,
            'is_available': is_online
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Get online providers for customers
@providers_bp.route('/online', methods=['GET'])
def get_online_providers():
    """Get online providers for customers"""
    try:
        # Get query parameters
        latitude = request.args.get('latitude', type=float)
        longitude = request.args.get('longitude', type=float)
        radius = request.args.get('radius', 50, type=int)  # Default 50km radius
        service_id = request.args.get('service_id')
        
        # Get distinct providers with their latest online location
        subquery = db.session.query(
            ProviderLocation.provider_id,
            db.func.max(ProviderLocation.created_at).label('latest_update')
        ).filter(
            ProviderLocation.is_online == True
        ).group_by(ProviderLocation.provider_id).subquery()
        
        providers_with_location = db.session.query(
            ServiceProviderProfile,
            ProviderLocation.latitude,
            ProviderLocation.longitude,
            ProviderLocation.created_at
        ).join(
            ProviderLocation,
            ServiceProviderProfile.id == ProviderLocation.provider_id
        ).join(
            subquery,
            db.and_(
                ProviderLocation.provider_id == subquery.c.provider_id,
                ProviderLocation.created_at == subquery.c.latest_update
            )
        ).filter(
            ServiceProviderProfile.verification_status == 'verified',
            ServiceProviderProfile.is_available == True,
            ProviderLocation.is_online == True
        )
        
        # Apply distance filter if coordinates provided
        if latitude and longitude:
            # Calculate distance using Haversine formula
            distance_formula = db.func.acos(
                db.func.cos(db.func.radians(latitude)) *
                db.func.cos(db.func.radians(ProviderLocation.latitude)) *
                db.func.cos(db.func.radians(ProviderLocation.longitude) - db.func.radians(longitude)) +
                db.func.sin(db.func.radians(latitude)) *
                db.func.sin(db.func.radians(ProviderLocation.latitude))
            ) * 6371  # Earth's radius in km
            
            providers_with_location = providers_with_location.filter(
                distance_formula <= radius
            )
        
        results = providers_with_location.all()
        
        # Format response
        online_providers = []
        for provider, lat, lng, last_update in results:
            provider_data = provider.to_dict()
            provider_data.update({
                'current_location': {
                    'latitude': float(lat),
                    'longitude': float(lng),
                    'last_update': last_update.isoformat()
                },
                'is_online': True
            })
            
            # Calculate distance if customer location provided
            if latitude and longitude:
                from math import radians, cos, sin, asin, sqrt
                
                # Haversine formula
                lat1, lon1, lat2, lon2 = map(radians, [latitude, longitude, lat, lng])
                dlat = lat2 - lat1
                dlon = lon2 - lon1
                a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
                distance = 2 * asin(sqrt(a)) * 6371  # Earth's radius in km
                
                provider_data['distance_km'] = round(distance, 2)
            
            # Remove sensitive information
            provider_data.pop('national_id', None)
            provider_data.pop('date_of_birth', None)
            
            online_providers.append(provider_data)
        
        # Sort by distance if available, otherwise by rating
        if latitude and longitude:
            online_providers.sort(key=lambda x: x.get('distance_km', float('inf')))
        else:
            online_providers.sort(key=lambda x: x.get('average_rating', 0), reverse=True)
        
        return jsonify({
            'online_providers': online_providers,
            'count': len(online_providers),
            'search_params': {
                'latitude': latitude,
                'longitude': longitude,
                'radius_km': radius,
                'service_id': service_id
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@providers_bp.route('/availability', methods=['PUT'])
@provider_required
def update_availability(current_user):
    """Update provider availability status"""
    try:
        data = request.get_json()
        
        if 'is_available' not in data:
            return jsonify({'error': 'is_available is required'}), 400
        
        provider = current_user.provider_profile
        provider.is_available = data['is_available']
        provider.updated_at = datetime.utcnow()
        
        # Update location online status
        if not data['is_available']:
            # Set all locations to offline
            ProviderLocation.query.filter_by(
                provider_id=provider.id
            ).update({'is_online': False})
        
        db.session.commit()
        
        return jsonify({
            'message': 'Availability updated successfully',
            'is_available': provider.is_available
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@providers_bp.route('/service-areas', methods=['POST'])
@provider_required
def add_service_area(current_user):
    """Add a service area for the provider"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['area_name', 'center_latitude', 'center_longitude', 'radius_km']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        latitude = float(data['center_latitude'])
        longitude = float(data['center_longitude'])
        radius = float(data['radius_km'])
        
        # Validate coordinates
        if not validate_coordinates(latitude, longitude):
            return jsonify({'error': 'Invalid coordinates for Egypt'}), 400
        
        # Validate radius (max 100km)
        if radius <= 0 or radius > 100:
            return jsonify({'error': 'Radius must be between 1 and 100 km'}), 400
        
        # If this is marked as primary, unset other primary areas
        if data.get('is_primary_area', False):
            ProviderServiceArea.query.filter_by(
                provider_id=current_user.provider_profile.id,
                is_primary_area=True
            ).update({'is_primary_area': False})
        
        service_area = ProviderServiceArea(
            provider_id=current_user.provider_profile.id,
            area_name=data['area_name'],
            center_latitude=latitude,
            center_longitude=longitude,
            radius_km=radius,
            is_primary_area=data.get('is_primary_area', False),
            travel_time_minutes=data.get('travel_time_minutes', 30)
        )
        
        db.session.add(service_area)
        db.session.commit()
        
        return jsonify({
            'message': 'Service area added successfully',
            'service_area': service_area.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@providers_bp.route('/service-areas/<area_id>', methods=['DELETE'])
@provider_required
def delete_service_area(current_user, area_id):
    """Delete a service area"""
    try:
        service_area = ProviderServiceArea.query.get_or_404(area_id)
        
        # Check ownership
        if service_area.provider_id != current_user.provider_profile.id:
            return jsonify({'error': 'Access denied'}), 403
        
        db.session.delete(service_area)
        db.session.commit()
        
        return jsonify({
            'message': 'Service area deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@providers_bp.route('/documents', methods=['POST'])
@provider_required
def upload_document(current_user):
    """Upload verification document"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['document_type', 'document_url']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Validate document type
        valid_types = ['national_id', 'certificate', 'license', 'insurance', 'background_check']
        if data['document_type'] not in valid_types:
            return jsonify({'error': f'Invalid document type. Must be one of: {valid_types}'}), 400
        
        # Check if document type already exists
        existing = ProviderDocument.query.filter_by(
            provider_id=current_user.provider_profile.id,
            document_type=data['document_type']
        ).first()
        
        if existing:
            # Update existing document
            existing.document_url = data['document_url']
            existing.verification_status = 'pending'
            existing.verified_by = None
            existing.verified_at = None
            existing.rejection_reason = None
            document = existing
        else:
            # Create new document
            document = ProviderDocument(
                provider_id=current_user.provider_profile.id,
                document_type=data['document_type'],
                document_url=data['document_url']
            )
            db.session.add(document)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Document uploaded successfully',
            'document': document.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@providers_bp.route('/<provider_id>', methods=['GET'])
def get_provider_public_profile(provider_id):
    """Get public provider profile for customers"""
    try:
        provider = ServiceProviderProfile.query.get_or_404(provider_id)
        
        # Only show verified providers
        if provider.verification_status != 'verified':
            return jsonify({'error': 'Provider not found'}), 404
        
        # Get provider services
        provider_services = ProviderService.query.filter_by(
            provider_id=provider.id,
            is_active=True
        ).all()
        
        # Get recent reviews (last 10)
        from src.models.service import BookingReview
        reviews = BookingReview.query.filter_by(
            provider_id=provider.id,
            is_verified=True
        ).order_by(BookingReview.created_at.desc()).limit(10).all()
        
        # Get current location (if online)
        current_location = ProviderLocation.query.filter_by(
            provider_id=provider.id,
            is_online=True
        ).order_by(ProviderLocation.last_updated.desc()).first()
        
        profile_data = provider.to_dict()
        profile_data.update({
            'services': [ps.to_dict() for ps in provider_services],
            'reviews': [review.to_dict() for review in reviews],
            'is_online': current_location is not None,
            'last_seen': current_location.last_updated.isoformat() if current_location else None
        })
        
        # Remove sensitive information
        profile_data.pop('national_id', None)
        profile_data.pop('date_of_birth', None)
        
        return jsonify({
            'provider': profile_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@providers_bp.route('/verification-queue', methods=['GET'])
@admin_required
def get_verification_queue(current_user):
    """Get providers pending verification (admin only)"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        providers = ServiceProviderProfile.query.filter_by(
            verification_status='pending'
        ).order_by(ServiceProviderProfile.created_at.asc()).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        provider_data = []
        for provider in providers.items:
            data = provider.to_dict()
            
            # Get documents
            documents = ProviderDocument.query.filter_by(
                provider_id=provider.id
            ).all()
            data['documents'] = [doc.to_dict() for doc in documents]
            
            provider_data.append(data)
        
        return jsonify({
            'providers': provider_data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': providers.total,
                'pages': providers.pages,
                'has_next': providers.has_next,
                'has_prev': providers.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@providers_bp.route('/<provider_id>/verify', methods=['POST'])
@admin_required
def verify_provider(current_user, provider_id):
    """Verify or reject a service provider (admin only)"""
    try:
        data = request.get_json()
        
        if 'action' not in data or data['action'] not in ['approve', 'reject']:
            return jsonify({'error': 'Action must be "approve" or "reject"'}), 400
        
        provider = ServiceProviderProfile.query.get_or_404(provider_id)
        
        if data['action'] == 'approve':
            provider.verification_status = 'verified'
            provider.background_check_status = 'clear'
            
            # Activate the user account
            provider.user.status = 'active'
            
            message = 'Provider verified successfully'
        else:  # reject
            provider.verification_status = 'rejected'
            reason = data.get('reason', 'Verification requirements not met')
            
            # You might want to store rejection reason somewhere
            # For now, we'll just include it in the response
            message = f'Provider rejected: {reason}'
        
        provider.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': message,
            'provider': provider.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

