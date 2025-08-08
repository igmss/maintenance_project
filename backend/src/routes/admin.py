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
        
        # Average rating (remove is_verified filter as column doesn't exist)
        avg_rating_query = db.session.query(
            func.avg(BookingReview.rating).label('avg_rating')
        )
        
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

@admin_bp.route('/providers', methods=['GET'])
@admin_required
def get_all_providers(current_user):
    """Get all service providers with filtering and pagination"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        verification_status = request.args.get('verification_status')
        search = request.args.get('search')
        
        # Build base query
        query = ServiceProviderProfile.query
        
        # Filter by verification status
        if verification_status:
            query = query.filter(ServiceProviderProfile.verification_status == verification_status)
        
        # Search by name
        if search:
            query = query.filter(
                or_(
                    ServiceProviderProfile.first_name.ilike(f'%{search}%'),
                    ServiceProviderProfile.last_name.ilike(f'%{search}%')
                )
            )
        
        # Order by creation date (newest first)
        query = query.order_by(ServiceProviderProfile.created_at.desc())
        
        # Get all providers (skip pagination for now to avoid issues)
        providers = query.all()
        
        # Prepare provider data
        providers_data = []
        for provider in providers:
            try:
                provider_data = provider.to_dict()
                # Try to get user data safely
                if hasattr(provider, 'user') and provider.user:
                    provider_data['user'] = provider.user.to_dict()
                else:
                    provider_data['user'] = None
                providers_data.append(provider_data)
            except Exception as provider_error:
                print(f"Error processing provider {provider.id}: {provider_error}")
                continue
        
        return jsonify({
            'providers': providers_data,
            'pagination': {
                'page': 1,
                'per_page': len(providers_data),
                'total': len(providers_data),
                'pages': 1,
                'has_next': False,
                'has_prev': False
            }
        }), 200
        
    except Exception as e:
        print(f"Error in get_all_providers: {str(e)}")
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/providers/<provider_id>/verification', methods=['PUT'])
@admin_required
def update_provider_verification(current_user, provider_id):
    """Update provider verification status"""
    try:
        data = request.get_json()
        
        if 'verification_status' not in data:
            return jsonify({'error': 'verification_status is required'}), 400
        
        provider = ServiceProviderProfile.query.get_or_404(provider_id)
        
        # Validate status
        valid_statuses = ['pending', 'approved', 'rejected']
        if data['verification_status'] not in valid_statuses:
            return jsonify({'error': f'Invalid status. Must be one of: {valid_statuses}'}), 400
        
        old_status = provider.verification_status
        provider.verification_status = data['verification_status']
        provider.updated_at = datetime.utcnow()
        
        # Add rejection reason if provided
        if data['verification_status'] == 'rejected' and 'rejection_reason' in data:
            provider.rejection_reason = data['rejection_reason']
        
        db.session.commit()
        
        return jsonify({
            'message': f'Provider verification status updated from {old_status} to {data["verification_status"]}',
            'provider': provider.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Document Review Endpoints
@admin_bp.route('/documents', methods=['GET'])
@admin_required
def get_pending_documents(current_user):
    """Get all documents pending review"""
    try:
        status = request.args.get('status', 'pending')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        query = ProviderDocument.query.filter_by(verification_status=status)
        
        # Join with provider profile to get provider info
        query = query.join(ServiceProviderProfile, ProviderDocument.provider_id == ServiceProviderProfile.id)
        query = query.join(User, ServiceProviderProfile.user_id == User.id)
        
        documents = query.order_by(ProviderDocument.created_at.desc()).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        document_data = []
        for doc in documents.items:
            doc_dict = doc.to_dict()
            # Add provider info
            doc_dict['provider'] = {
                'id': doc.provider.id,
                'first_name': doc.provider.first_name,
                'last_name': doc.provider.last_name,
                'email': doc.provider.user.email,
                'verification_status': doc.provider.verification_status
            }
            document_data.append(doc_dict)
        
        return jsonify({
            'documents': document_data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': documents.total,
                'pages': documents.pages,
                'has_next': documents.has_next,
                'has_prev': documents.has_prev
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error in get_pending_documents: {str(e)}")
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/documents/<document_id>/review', methods=['PUT'])
@admin_required
def review_document(current_user, document_id):
    """Approve or reject a specific document"""
    try:
        data = request.get_json()
        
        if 'action' not in data or data['action'] not in ['approve', 'reject']:
            return jsonify({'error': 'Action must be "approve" or "reject"'}), 400
        
        document = ProviderDocument.query.get_or_404(document_id)
        
        if data['action'] == 'approve':
            document.verification_status = 'approved'
            document.verified_by = current_user.id
            document.verified_at = datetime.utcnow()
            document.rejection_reason = None
            message = 'Document approved successfully'
        else:  # reject
            document.verification_status = 'rejected'
            document.verified_by = current_user.id
            document.verified_at = datetime.utcnow()
            document.rejection_reason = data.get('reason', 'Document does not meet requirements')
            message = f'Document rejected: {document.rejection_reason}'
        
        db.session.commit()
        
        # Check if all required documents are approved for auto-approval
        provider = document.provider
        all_docs = ProviderDocument.query.filter_by(provider_id=provider.id).all()
        
        required_docs = ['national_id', 'certificate', 'license']  # Define required docs
        approved_docs = [doc.document_type for doc in all_docs if doc.verification_status == 'approved']
        
        # Auto-approve provider if all required documents are approved
        if all(doc_type in approved_docs for doc_type in required_docs) and provider.verification_status == 'pending':
            provider.verification_status = 'approved'
            provider.user.status = 'active'
            db.session.commit()
            
        return jsonify({
            'message': message,
            'document': document.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error in review_document: {str(e)}")
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/providers/<provider_id>/documents', methods=['GET'])
@admin_required
def get_provider_documents(current_user, provider_id):
    """Get all documents for a specific provider"""
    try:
        provider = ServiceProviderProfile.query.get_or_404(provider_id)
        documents = ProviderDocument.query.filter_by(provider_id=provider_id).all()
        
        return jsonify({
            'provider': provider.to_dict(),
            'documents': [doc.to_dict() for doc in documents]
        }), 200
        
    except Exception as e:
        logger.error(f"Error in get_provider_documents: {str(e)}")
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

@admin_bp.route('/services', methods=['GET'])
@admin_required
def get_all_services(current_user):
    """Get all services for admin panel"""
    try:
        language = request.args.get('lang', 'en')
        category_id = request.args.get('category_id')
        
        query = Service.query
        
        # Filter by category if specified
        if category_id:
            query = query.filter_by(category_id=category_id)
        
        # Join with category to get category info
        services = query.join(ServiceCategory).order_by(ServiceCategory.name_ar, Service.name_ar).all()
        
        services_data = []
        for service in services:
            service_dict = service.to_dict(language)
            service_dict['category'] = service.category.to_dict(language)
            services_data.append(service_dict)
        
        return jsonify({
            'services': services_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/services', methods=['POST'])
@admin_required
def create_service(current_user):
    """Create a new service"""
    try:
        data = request.get_json()
        print(f"Service creation data: {data}")
        
        # Validate required fields
        required_fields = ['category_id', 'name_ar', 'name_en', 'base_price']
        for field in required_fields:
            if field not in data or data[field] is None:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Validate category exists
        try:
            category = ServiceCategory.query.get(data['category_id'])
            if not category:
                return jsonify({'error': f'Category with id {data["category_id"]} not found'}), 404
        except Exception as cat_error:
            print(f"Category lookup error: {cat_error}")
            return jsonify({'error': f'Invalid category_id: {data["category_id"]}'}), 400
        
        # Convert price to float
        try:
            base_price = float(data['base_price'])
        except (ValueError, TypeError):
            return jsonify({'error': 'base_price must be a valid number'}), 400
        
        service = Service(
            category_id=data['category_id'],
            name_ar=data['name_ar'],
            name_en=data['name_en'],
            description_ar=data.get('description_ar'),
            description_en=data.get('description_en'),
            base_price=base_price,
            price_unit=data.get('price_unit', 'fixed'),
            estimated_duration=data.get('estimated_duration'),
            is_emergency_service=data.get('is_emergency_service', False),
            emergency_surcharge_percentage=data.get('emergency_surcharge_percentage', 0.00)
        )
        
        db.session.add(service)
        db.session.commit()
        
        # Safely get service dict
        try:
            service_dict = service.to_dict()
        except Exception as dict_error:
            print(f"Service to_dict error: {dict_error}")
            service_dict = {
                'id': service.id,
                'name_ar': service.name_ar,
                'name_en': service.name_en,
                'base_price': service.base_price,
                'is_active': service.is_active
            }
        
        return jsonify({
            'message': 'Service created successfully',
            'service': service_dict
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Service creation error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/services/<service_id>', methods=['PUT'])
@admin_required
def update_service(current_user, service_id):
    """Update an existing service"""
    try:
        data = request.get_json()
        service = Service.query.get_or_404(service_id)
        
        # Update fields if provided
        if 'category_id' in data:
            # Validate category exists
            category = ServiceCategory.query.get_or_404(data['category_id'])
            service.category_id = data['category_id']
        
        if 'name_ar' in data:
            service.name_ar = data['name_ar']
        if 'name_en' in data:
            service.name_en = data['name_en']
        if 'description_ar' in data:
            service.description_ar = data['description_ar']
        if 'description_en' in data:
            service.description_en = data['description_en']
        if 'base_price' in data:
            service.base_price = data['base_price']
        if 'price_unit' in data:
            service.price_unit = data['price_unit']
        if 'estimated_duration' in data:
            service.estimated_duration = data['estimated_duration']
        if 'is_emergency_service' in data:
            service.is_emergency_service = data['is_emergency_service']
        if 'emergency_surcharge_percentage' in data:
            service.emergency_surcharge_percentage = data['emergency_surcharge_percentage']
        if 'is_active' in data:
            service.is_active = data['is_active']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Service updated successfully',
            'service': service.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/services/<service_id>', methods=['DELETE'])
@admin_required
def delete_service(current_user, service_id):
    """Delete a service (soft delete by setting is_active=False)"""
    try:
        service = Service.query.get_or_404(service_id)
        
        # Soft delete by setting is_active to False
        service.is_active = False
        db.session.commit()
        
        return jsonify({
            'message': 'Service deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/services/categories', methods=['GET'])
@admin_required
def get_all_service_categories(current_user):
    """Get all service categories for admin panel"""
    try:
        language = request.args.get('lang', 'en')
        categories = ServiceCategory.query.order_by(ServiceCategory.sort_order).all()
        
        return jsonify({
            'categories': [category.to_dict(language) for category in categories]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/analytics', methods=['GET'])
@admin_required
def get_analytics_data(current_user):
    """Get comprehensive analytics data for admin dashboard"""
    try:
        # Date range for analytics
        today = datetime.utcnow().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        year_ago = today - timedelta(days=365)
        
        # Revenue analytics
        revenue_query = db.session.query(
            func.sum(Booking.total_price).label('total'),
            func.count(Booking.id).label('count')
        ).filter(
            Booking.booking_status == 'completed',
            Booking.total_price.isnot(None)
        )
        
        total_revenue = revenue_query.scalar() or 0
        
        # Monthly revenue for chart
        monthly_revenue = db.session.query(
            func.date_trunc('month', Booking.created_at).label('month'),
            func.sum(Booking.total_price).label('revenue'),
            func.count(Booking.id).label('bookings')
        ).filter(
            Booking.booking_status == 'completed',
            Booking.created_at >= datetime.combine(year_ago, datetime.min.time())
        ).group_by(
            func.date_trunc('month', Booking.created_at)
        ).order_by('month').all()
        
        # Service performance
        service_stats = db.session.query(
            Service.name_ar,
            Service.name_en,
            func.count(Booking.id).label('bookings'),
            func.sum(Booking.total_price).label('revenue'),
            func.avg(BookingReview.rating).label('avg_rating')
        ).join(Booking).outerjoin(BookingReview).filter(
            Booking.booking_status == 'completed'
        ).group_by(Service.id, Service.name_ar, Service.name_en).order_by(
            func.count(Booking.id).desc()
        ).limit(10).all()
        
        # Provider performance
        provider_stats = db.session.query(
            ServiceProviderProfile.first_name,
            ServiceProviderProfile.last_name,
            func.count(Booking.id).label('bookings'),
            func.sum(Booking.total_price).label('revenue'),
            func.avg(BookingReview.rating).label('avg_rating')
        ).join(Booking).outerjoin(BookingReview).filter(
            Booking.booking_status == 'completed'
        ).group_by(
            ServiceProviderProfile.id,
            ServiceProviderProfile.first_name,
            ServiceProviderProfile.last_name
        ).order_by(
            func.count(Booking.id).desc()
        ).limit(10).all()
        
        return jsonify({
            'revenue': {
                'total': float(total_revenue),
                'monthly_data': [
                    {
                        'month': row.month.strftime('%Y-%m'),
                        'revenue': float(row.revenue or 0),
                        'bookings': row.bookings
                    } for row in monthly_revenue
                ]
            },
            'services': [
                {
                    'name': row.name_ar,
                    'name_en': row.name_en,
                    'bookings': row.bookings,
                    'revenue': float(row.revenue or 0),
                    'rating': float(row.avg_rating or 0)
                } for row in service_stats
            ],
            'providers': [
                {
                    'name': f"{row.first_name} {row.last_name}",
                    'bookings': row.bookings,
                    'revenue': float(row.revenue or 0),
                    'rating': float(row.avg_rating or 0)
                } for row in provider_stats
            ]
        }), 200
        
    except Exception as e:
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

