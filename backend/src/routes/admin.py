from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from sqlalchemy import func, and_, or_
from src.models import db
from src.models.user import User, CustomerProfile, ServiceProviderProfile, ProviderDocument
from src.models.service import ServiceCategory, Service, Booking, BookingReview
from src.models.location import Governorate, City
from src.utils.auth import admin_required

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard/stats', methods=['GET'])
@admin_required
def get_dashboard_stats(current_user):
    """Get dashboard statistics for admin"""
    try:
        # Date range for statistics
        today = datetime.utcnow().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        # User statistics
        total_users = User.query.count()
        total_customers = User.query.filter_by(user_type='customer').count()
        total_providers = User.query.filter_by(user_type='service_provider').count()
        
        # New users this week
        new_users_week = User.query.filter(
            User.created_at >= datetime.combine(week_ago, datetime.min.time())
        ).count()
        
        # Provider verification statistics
        pending_verification = ServiceProviderProfile.query.filter_by(
            verification_status='pending'
        ).count()
        
        verified_providers = ServiceProviderProfile.query.filter_by(
            verification_status='approved'
        ).count()
        
        # Booking statistics
        total_bookings = Booking.query.count()
        completed_bookings = Booking.query.filter_by(booking_status='completed').count()
        active_bookings = Booking.query.filter(
            Booking.booking_status.in_(['pending', 'confirmed', 'in_progress'])
        ).count()
        
        # Bookings this month
        bookings_this_month = Booking.query.filter(
            Booking.created_at >= datetime.combine(month_ago, datetime.min.time())
        ).count()
        
        # Revenue statistics (from completed bookings)
        revenue_query = db.session.query(
            func.sum(Booking.total_amount).label('total_revenue'),
            func.sum(Booking.platform_commission).label('platform_revenue')
        ).filter(Booking.booking_status == 'completed')
        
        revenue_result = revenue_query.first()
        total_revenue = float(revenue_result.total_revenue) if revenue_result.total_revenue else 0
        platform_revenue = float(revenue_result.platform_revenue) if revenue_result.platform_revenue else 0
        
        # Monthly revenue
        monthly_revenue_query = db.session.query(
            func.sum(Booking.platform_commission).label('monthly_revenue')
        ).filter(
            and_(
                Booking.booking_status == 'completed',
                Booking.created_at >= datetime.combine(month_ago, datetime.min.time())
            )
        )
        
        monthly_revenue_result = monthly_revenue_query.first()
        monthly_revenue = float(monthly_revenue_result.monthly_revenue) if monthly_revenue_result.monthly_revenue else 0
        
        # Service statistics
        total_services = Service.query.filter_by(is_active=True).count()
        total_categories = ServiceCategory.query.filter_by(is_active=True).count()
        
        # Average rating
        avg_rating_query = db.session.query(
            func.avg(BookingReview.rating).label('avg_rating')
        ).filter(BookingReview.is_verified == True)
        
        avg_rating_result = avg_rating_query.first()
        average_rating = round(float(avg_rating_result.avg_rating), 2) if avg_rating_result.avg_rating else 0
        
        return jsonify({
            'users': {
                'total': total_users,
                'customers': total_customers,
                'providers': total_providers,
                'new_this_week': new_users_week
            },
            'providers': {
                'total': total_providers,
                'verified': verified_providers,
                'pending_verification': pending_verification,
                'verification_rate': round((verified_providers / total_providers * 100), 2) if total_providers > 0 else 0
            },
            'bookings': {
                'total': total_bookings,
                'completed': completed_bookings,
                'active': active_bookings,
                'this_month': bookings_this_month,
                'completion_rate': round((completed_bookings / total_bookings * 100), 2) if total_bookings > 0 else 0
            },
            'revenue': {
                'total_revenue': total_revenue,
                'platform_revenue': platform_revenue,
                'monthly_revenue': monthly_revenue,
                'commission_rate': round((platform_revenue / total_revenue * 100), 2) if total_revenue > 0 else 15
            },
            'services': {
                'total_services': total_services,
                'total_categories': total_categories,
                'average_rating': average_rating
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/users', methods=['GET'])
@admin_required
def get_users(current_user):
    """Get all users with pagination and filtering"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        user_type = request.args.get('user_type')
        status = request.args.get('status')
        search = request.args.get('search')
        
        # Build query
        query = User.query
        
        # Filter by user type
        if user_type:
            query = query.filter_by(user_type=user_type)
        
        # Filter by status
        if status:
            query = query.filter_by(status=status)
        
        # Search by email or phone
        if search:
            query = query.filter(
                or_(
                    User.email.ilike(f'%{search}%'),
                    User.phone.ilike(f'%{search}%')
                )
            )
        
        # Order by creation date (newest first)
        query = query.order_by(User.created_at.desc())
        
        # Paginate
        users = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        # Prepare user data with profiles
        users_data = []
        for user in users.items:
            user_data = user.to_dict()
            
            # Add profile information
            if user.user_type == 'customer' and user.customer_profile:
                user_data['profile'] = user.customer_profile.to_dict()
            elif user.user_type == 'service_provider' and user.provider_profile:
                user_data['profile'] = user.provider_profile.to_dict()
            
            users_data.append(user_data)
        
        return jsonify({
            'users': users_data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': users.total,
                'pages': users.pages,
                'has_next': users.has_next,
                'has_prev': users.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/users/<user_id>/status', methods=['PUT'])
@admin_required
def update_user_status(current_user, user_id):
    """Update user status (activate, suspend, etc.)"""
    try:
        data = request.get_json()
        
        if 'status' not in data:
            return jsonify({'error': 'Status is required'}), 400
        
        user = User.query.get_or_404(user_id)
        
        # Validate status
        valid_statuses = ['active', 'inactive', 'suspended', 'pending_verification']
        if data['status'] not in valid_statuses:
            return jsonify({'error': f'Invalid status. Must be one of: {valid_statuses}'}), 400
        
        # Prevent admin from suspending themselves
        if user.id == current_user.id and data['status'] == 'suspended':
            return jsonify({'error': 'Cannot suspend your own account'}), 400
        
        old_status = user.status
        user.status = data['status']
        user.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': f'User status updated from {old_status} to {data["status"]}',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/bookings', methods=['GET'])
@admin_required
def get_all_bookings(current_user):
    """Get all bookings with filtering and pagination"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status = request.args.get('status')
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        # Build query
        query = Booking.query
        
        # Filter by status
        if status:
            query = query.filter_by(booking_status=status)
        
        # Filter by date range
        if date_from:
            try:
                from_date = datetime.fromisoformat(date_from)
                query = query.filter(Booking.created_at >= from_date)
            except ValueError:
                return jsonify({'error': 'Invalid date_from format'}), 400
        
        if date_to:
            try:
                to_date = datetime.fromisoformat(date_to)
                query = query.filter(Booking.created_at <= to_date)
            except ValueError:
                return jsonify({'error': 'Invalid date_to format'}), 400
        
        # Order by creation date (newest first)
        query = query.order_by(Booking.created_at.desc())
        
        # Paginate
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

@admin_bp.route('/services/categories', methods=['POST'])
@admin_required
def create_service_category(current_user):
    """Create a new service category"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name_ar', 'name_en']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if category already exists
        existing = ServiceCategory.query.filter(
            or_(
                ServiceCategory.name_ar == data['name_ar'],
                ServiceCategory.name_en == data['name_en']
            )
        ).first()
        
        if existing:
            return jsonify({'error': 'Category with this name already exists'}), 409
        
        category = ServiceCategory(
            name_ar=data['name_ar'],
            name_en=data['name_en'],
            description_ar=data.get('description_ar'),
            description_en=data.get('description_en'),
            icon_url=data.get('icon_url'),
            sort_order=data.get('sort_order', 0)
        )
        
        db.session.add(category)
        db.session.commit()
        
        return jsonify({
            'message': 'Service category created successfully',
            'category': category.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/services/categories/<category_id>', methods=['PUT'])
@admin_required
def update_service_category(current_user, category_id):
    """Update a service category"""
    try:
        data = request.get_json()
        category = ServiceCategory.query.get_or_404(category_id)
        
        # Update fields
        if 'name_ar' in data:
            category.name_ar = data['name_ar']
        if 'name_en' in data:
            category.name_en = data['name_en']
        if 'description_ar' in data:
            category.description_ar = data['description_ar']
        if 'description_en' in data:
            category.description_en = data['description_en']
        if 'icon_url' in data:
            category.icon_url = data['icon_url']
        if 'sort_order' in data:
            category.sort_order = data['sort_order']
        if 'is_active' in data:
            category.is_active = data['is_active']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Service category updated successfully',
            'category': category.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/services', methods=['POST'])
@admin_required
def create_service(current_user):
    """Create a new service"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['category_id', 'name_ar', 'name_en', 'base_price']
        for field in required_fields:
            if field not in data or data[field] is None:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Validate category exists
        category = ServiceCategory.query.get_or_404(data['category_id'])
        
        service = Service(
            category_id=data['category_id'],
            name_ar=data['name_ar'],
            name_en=data['name_en'],
            description_ar=data.get('description_ar'),
            description_en=data.get('description_en'),
            base_price=data['base_price'],
            price_unit=data.get('price_unit', 'fixed'),
            estimated_duration=data.get('estimated_duration'),
            is_emergency_service=data.get('is_emergency_service', False),
            emergency_surcharge_percentage=data.get('emergency_surcharge_percentage', 0.00)
        )
        
        db.session.add(service)
        db.session.commit()
        
        return jsonify({
            'message': 'Service created successfully',
            'service': service.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/analytics/revenue', methods=['GET'])
@admin_required
def get_revenue_analytics(current_user):
    """Get revenue analytics data"""
    try:
        # Get date range from query params
        days = request.args.get('days', 30, type=int)
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=days)
        
        # Daily revenue data
        daily_revenue = db.session.query(
            func.date(Booking.created_at).label('date'),
            func.sum(Booking.platform_commission).label('revenue'),
            func.count(Booking.id).label('bookings')
        ).filter(
            and_(
                Booking.booking_status == 'completed',
                func.date(Booking.created_at) >= start_date,
                func.date(Booking.created_at) <= end_date
            )
        ).group_by(func.date(Booking.created_at)).all()
        
        # Revenue by service category
        category_revenue = db.session.query(
            ServiceCategory.name_en.label('category'),
            func.sum(Booking.platform_commission).label('revenue'),
            func.count(Booking.id).label('bookings')
        ).join(Service).join(Booking).filter(
            Booking.booking_status == 'completed'
        ).group_by(ServiceCategory.id, ServiceCategory.name_en).all()
        
        # Top performing providers
        top_providers = db.session.query(
            ServiceProviderProfile.first_name,
            ServiceProviderProfile.last_name,
            func.sum(Booking.provider_earnings).label('earnings'),
            func.count(Booking.id).label('completed_jobs'),
            func.avg(BookingReview.rating).label('avg_rating')
        ).join(Booking).outerjoin(BookingReview).filter(
            Booking.booking_status == 'completed'
        ).group_by(
            ServiceProviderProfile.id,
            ServiceProviderProfile.first_name,
            ServiceProviderProfile.last_name
        ).order_by(func.sum(Booking.provider_earnings).desc()).limit(10).all()
        
        return jsonify({
            'daily_revenue': [
                {
                    'date': item.date.isoformat(),
                    'revenue': float(item.revenue) if item.revenue else 0,
                    'bookings': item.bookings
                }
                for item in daily_revenue
            ],
            'category_revenue': [
                {
                    'category': item.category,
                    'revenue': float(item.revenue) if item.revenue else 0,
                    'bookings': item.bookings
                }
                for item in category_revenue
            ],
            'top_providers': [
                {
                    'name': f"{item.first_name} {item.last_name}",
                    'earnings': float(item.earnings) if item.earnings else 0,
                    'completed_jobs': item.completed_jobs,
                    'avg_rating': round(float(item.avg_rating), 2) if item.avg_rating else 0
                }
                for item in top_providers
            ]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/system/settings', methods=['GET'])
@admin_required
def get_system_settings(current_user):
    """Get system settings and configuration"""
    try:
        # This would typically come from a settings table or config file
        # For now, we'll return some default settings
        settings = {
            'platform': {
                'name': 'Maintenance Platform',
                'version': '1.0.0',
                'commission_rate': 15.0,
                'emergency_surcharge_rate': 50.0,
                'supported_languages': ['ar', 'en'],
                'default_language': 'ar'
            },
            'booking': {
                'max_advance_days': 30,
                'cancellation_window_hours': 2,
                'auto_assign_providers': True,
                'require_provider_verification': True
            },
            'notifications': {
                'email_enabled': True,
                'sms_enabled': True,
                'push_enabled': True,
                'admin_notifications': True
            },
            'location': {
                'default_search_radius_km': 25,
                'max_search_radius_km': 100,
                'supported_governorates': Governorate.query.filter_by(is_active=True).count()
            }
        }
        
        return jsonify({
            'settings': settings
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

