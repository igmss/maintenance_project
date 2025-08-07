from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from src.models import db
from src.models.service import ServiceCategory, Service, ProviderService, Booking, BookingStatusHistory, BookingReview
from src.models.user import ServiceProviderProfile, CustomerProfile
from src.models.location import ProviderLocation, ProviderServiceArea
from src.utils.auth import token_required, customer_required, provider_required
from src.utils.location import find_nearby_providers, calculate_distance, estimate_travel_time

services_bp = Blueprint('services', __name__)

@services_bp.route('/categories', methods=['GET'])
def get_service_categories():
    """Get all active service categories"""
    try:
        language = request.args.get('lang', 'en')
        categories = ServiceCategory.query.filter_by(is_active=True).order_by(ServiceCategory.sort_order).all()
        
        return jsonify({
            'categories': [category.to_dict(language) for category in categories]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@services_bp.route('/categories/<category_id>/services', methods=['GET'])
def get_category_services(category_id):
    """Get all services in a category"""
    try:
        language = request.args.get('lang', 'en')
        category = ServiceCategory.query.get_or_404(category_id)
        
        services = Service.query.filter_by(
            category_id=category_id,
            is_active=True
        ).all()
        
        return jsonify({
            'category': category.to_dict(language),
            'services': [service.to_dict(language) for service in services]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@services_bp.route('/search', methods=['POST'])
def search_providers():
    """Search for service providers based on location and service"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['latitude', 'longitude', 'service_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        service_id = data['service_id']
        max_distance = data.get('max_distance_km', 25)  # Default 25km radius
        
        # Get service details
        service = Service.query.get_or_404(service_id)
        
        # Find providers who offer this service
        provider_services = ProviderService.query.filter_by(
            service_id=service_id,
            is_active=True
        ).join(ServiceProviderProfile).filter(
            ServiceProviderProfile.verification_status == 'approved',
            ServiceProviderProfile.is_available == True
        ).all()
        
        available_providers = []
        
        for provider_service in provider_services:
            provider = provider_service.provider
            
            # Get provider's current location
            location = ProviderLocation.query.filter_by(
                provider_id=provider.id,
                is_online=True
            ).order_by(ProviderLocation.last_updated.desc()).first()
            
            if location:
                distance = calculate_distance(
                    latitude, longitude,
                    float(location.latitude), float(location.longitude)
                )
                
                if distance <= max_distance:
                    travel_time = estimate_travel_time(distance)
                    
                    provider_data = provider.to_dict()
                    provider_data.update({
                        'distance_km': round(distance, 2),
                        'estimated_travel_time': travel_time,
                        'current_location': location.to_dict(),
                        'service_details': provider_service.to_dict(),
                        'price': float(provider_service.custom_price) if provider_service.custom_price else float(service.base_price)
                    })
                    
                    available_providers.append(provider_data)
        
        # Sort by distance
        available_providers.sort(key=lambda x: x['distance_km'])
        
        return jsonify({
            'service': service.to_dict(),
            'search_location': {
                'latitude': latitude,
                'longitude': longitude
            },
            'providers': available_providers,
            'total_found': len(available_providers)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@services_bp.route('/bookings', methods=['POST'])
@customer_required
def create_booking(current_user):
    """Create a new service booking"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['service_id', 'scheduled_date', 'service_address']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Validate service exists
        service = Service.query.get_or_404(data['service_id'])
        
        # Validate scheduled date
        try:
            scheduled_date = datetime.fromisoformat(data['scheduled_date'].replace('Z', '+00:00'))
        except ValueError:
            return jsonify({'error': 'Invalid date format'}), 400
        
        # Check if scheduled date is in the future
        if scheduled_date <= datetime.utcnow():
            return jsonify({'error': 'Scheduled date must be in the future'}), 400
        
        # Validate service address
        address = data['service_address']
        required_address_fields = ['street', 'city', 'governorate', 'latitude', 'longitude']
        for field in required_address_fields:
            if field not in address:
                return jsonify({'error': f'service_address.{field} is required'}), 400
        
        # Calculate pricing
        base_price = float(service.base_price)
        is_emergency = data.get('is_emergency', False)
        
        if is_emergency and service.is_emergency_service:
            emergency_surcharge = base_price * (float(service.emergency_surcharge_percentage) / 100)
            total_amount = base_price + emergency_surcharge
        else:
            total_amount = base_price
        
        # Calculate platform commission (15%)
        commission_rate = 0.15
        platform_commission = total_amount * commission_rate
        provider_earnings = total_amount - platform_commission
        
        # Create booking
        booking = Booking(
            customer_id=current_user.customer_profile.id,
            service_id=data['service_id'],
            scheduled_date=scheduled_date,
            service_address=address,
            special_instructions=data.get('special_instructions'),
            total_amount=total_amount,
            platform_commission=platform_commission,
            provider_earnings=provider_earnings,
            estimated_duration=service.estimated_duration
        )
        
        # If provider is specified, assign directly
        if 'provider_id' in data:
            provider = ServiceProviderProfile.query.get_or_404(data['provider_id'])
            
            # Verify provider offers this service
            provider_service = ProviderService.query.filter_by(
                provider_id=provider.id,
                service_id=service.id,
                is_active=True
            ).first()
            
            if not provider_service:
                return jsonify({'error': 'Provider does not offer this service'}), 400
            
            booking.provider_id = provider.id
            booking.booking_status = 'confirmed'
        
        db.session.add(booking)
        db.session.flush()  # Get booking ID
        
        # Create status history entry
        status_history = BookingStatusHistory(
            booking_id=booking.id,
            new_status=booking.booking_status,
            changed_by=current_user.id,
            change_reason='Booking created'
        )
        db.session.add(status_history)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Booking created successfully',
            'booking': booking.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@services_bp.route('/bookings', methods=['GET'])
@token_required
def get_bookings(current_user):
    """Get user's bookings"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status = request.args.get('status')
        
        # Build query based on user type
        if current_user.user_type == 'customer':
            query = Booking.query.filter_by(customer_id=current_user.customer_profile.id)
        elif current_user.user_type == 'service_provider':
            query = Booking.query.filter_by(provider_id=current_user.provider_profile.id)
        else:  # admin
            query = Booking.query
        
        # Filter by status if provided
        if status:
            query = query.filter_by(booking_status=status)
        
        # Order by creation date (newest first)
        query = query.order_by(Booking.created_at.desc())
        
        # Paginate results
        bookings = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        return jsonify({
            'bookings': [booking.to_dict() for booking in bookings.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': bookings.total,
                'pages': bookings.pages,
                'has_next': bookings.has_next,
                'has_prev': bookings.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@services_bp.route('/bookings/<booking_id>', methods=['GET'])
@token_required
def get_booking(current_user, booking_id):
    """Get specific booking details"""
    try:
        booking = Booking.query.get_or_404(booking_id)
        
        # Check if user has access to this booking
        if current_user.user_type == 'customer':
            if booking.customer_id != current_user.customer_profile.id:
                return jsonify({'error': 'Access denied'}), 403
        elif current_user.user_type == 'service_provider':
            if booking.provider_id != current_user.provider_profile.id:
                return jsonify({'error': 'Access denied'}), 403
        # Admin can access all bookings
        
        return jsonify({
            'booking': booking.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@services_bp.route('/bookings/<booking_id>/status', methods=['PUT'])
@token_required
def update_booking_status(current_user, booking_id):
    """Update booking status"""
    try:
        data = request.get_json()
        
        if 'status' not in data:
            return jsonify({'error': 'Status is required'}), 400
        
        booking = Booking.query.get_or_404(booking_id)
        new_status = data['status']
        
        # Validate status transitions based on user type
        valid_transitions = {
            'customer': {
                'pending': ['cancelled'],
                'confirmed': ['cancelled'],
                'completed': []
            },
            'service_provider': {
                'pending': ['confirmed'],
                'confirmed': ['in_progress', 'cancelled'],
                'in_progress': ['completed'],
                'completed': []
            },
            'admin': {
                'pending': ['confirmed', 'cancelled'],
                'confirmed': ['in_progress', 'cancelled'],
                'in_progress': ['completed', 'cancelled'],
                'completed': ['disputed']
            }
        }
        
        current_status = booking.booking_status
        allowed_transitions = valid_transitions.get(current_user.user_type, {}).get(current_status, [])
        
        if new_status not in allowed_transitions:
            return jsonify({'error': f'Cannot transition from {current_status} to {new_status}'}), 400
        
        # Check user permissions
        if current_user.user_type == 'customer':
            if booking.customer_id != current_user.customer_profile.id:
                return jsonify({'error': 'Access denied'}), 403
        elif current_user.user_type == 'service_provider':
            if booking.provider_id != current_user.provider_profile.id:
                return jsonify({'error': 'Access denied'}), 403
        
        # Update booking status
        old_status = booking.booking_status
        booking.booking_status = new_status
        booking.updated_at = datetime.utcnow()
        
        # Update timing fields
        if new_status == 'in_progress':
            booking.actual_start_time = datetime.utcnow()
        elif new_status == 'completed':
            booking.actual_end_time = datetime.utcnow()
            if booking.actual_start_time:
                duration = booking.actual_end_time - booking.actual_start_time
                booking.actual_duration = int(duration.total_seconds() / 60)  # minutes
        
        # Create status history entry
        status_history = BookingStatusHistory(
            booking_id=booking.id,
            previous_status=old_status,
            new_status=new_status,
            changed_by=current_user.id,
            change_reason=data.get('reason', f'Status changed to {new_status}')
        )
        
        db.session.add(status_history)
        db.session.commit()
        
        return jsonify({
            'message': 'Booking status updated successfully',
            'booking': booking.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@services_bp.route('/bookings/<booking_id>/review', methods=['POST'])
@customer_required
def create_review(current_user, booking_id):
    """Create a review for completed booking"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if 'rating' not in data:
            return jsonify({'error': 'Rating is required'}), 400
        
        rating = int(data['rating'])
        if rating < 1 or rating > 5:
            return jsonify({'error': 'Rating must be between 1 and 5'}), 400
        
        booking = Booking.query.get_or_404(booking_id)
        
        # Check if customer owns this booking
        if booking.customer_id != current_user.customer_profile.id:
            return jsonify({'error': 'Access denied'}), 403
        
        # Check if booking is completed
        if booking.booking_status != 'completed':
            return jsonify({'error': 'Can only review completed bookings'}), 400
        
        # Check if review already exists
        existing_review = BookingReview.query.filter_by(booking_id=booking_id).first()
        if existing_review:
            return jsonify({'error': 'Review already exists for this booking'}), 409
        
        # Create review
        review = BookingReview(
            booking_id=booking.id,
            customer_id=current_user.customer_profile.id,
            provider_id=booking.provider_id,
            rating=rating,
            review_text=data.get('review_text'),
            review_photos=data.get('review_photos', [])
        )
        
        db.session.add(review)
        
        # Update provider's average rating
        if booking.provider:
            provider_reviews = BookingReview.query.filter_by(provider_id=booking.provider_id).all()
            total_rating = sum(r.rating for r in provider_reviews) + rating
            review_count = len(provider_reviews) + 1
            booking.provider.average_rating = total_rating / review_count
        
        db.session.commit()
        
        return jsonify({
            'message': 'Review created successfully',
            'review': review.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

