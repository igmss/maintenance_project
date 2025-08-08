import os
import sys
from datetime import timedelta

# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import database and models
from src.models import db
from src.models.user import User, CustomerProfile, ServiceProviderProfile, CustomerAddress, ProviderDocument
from src.models.service import ServiceCategory, Service, ProviderService, Booking, BookingStatusHistory, BookingReview
from src.models.location import ProviderLocation, ProviderServiceArea, BookingLocation, Governorate, City

# Import routes
from src.routes.auth import auth_bp
from src.routes.user import user_bp
from src.routes.services import services_bp
from src.routes.providers import providers_bp
from src.routes.admin import admin_bp

def create_app():
    app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'maintenance-platform-secret-key-2024')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-maintenance-platform-2024')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)
    
    # Database configuration
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        # Fallback: construct from individual components
        db_host = os.getenv('DB_HOST', 'aws-0-us-east-1.pooler.supabase.com')
        db_port = os.getenv('DB_PORT', '6543')
        db_user = os.getenv('DB_USER', 'postgres.mxfduvxgvobbnazeovfd')
        db_password = os.getenv('DB_PASSWORD', 'Aa123e456y@$$')
        db_name = os.getenv('DB_NAME', 'postgres')
        
        if all([db_host, db_port, db_user, db_password, db_name]):
            database_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
            print(f"✅ Using constructed DATABASE_URL: postgresql://{db_user}:***@{db_host}:{db_port}/{db_name}")
        else:
            raise ValueError("❌ DATABASE_URL not provided and unable to construct from environment variables")
    else:
        print(f"✅ Using provided DATABASE_URL: {database_url[:50]}...")
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    # Initialize extensions
    CORS(app, origins="*", allow_headers=["Content-Type", "Authorization"])
    jwt = JWTManager(app)
    
    # Initialize database
    db.init_app(app)
    
    # Initialize Flask-Migrate
    migrate = Migrate(app, db)
    
    # JWT error handlers
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({'error': 'Token has expired'}), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({'error': 'Invalid token'}), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({'error': 'Authorization token is required'}), 401
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(user_bp, url_prefix='/api')
    app.register_blueprint(services_bp, url_prefix='/api/services')
    app.register_blueprint(providers_bp, url_prefix='/api/providers')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    
    # Health check endpoint
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({
            'status': 'healthy',
            'message': 'Maintenance Platform API is running',
            'version': '1.0.0'
        }), 200
    
    # API info endpoint
    @app.route('/api/info', methods=['GET'])
    def api_info():
        return jsonify({
            'name': 'Maintenance Platform API',
            'version': '1.0.0',
            'description': 'Backend API for maintenance service platform',
            'endpoints': {
                'auth': '/api/auth',
                'users': '/api/users',
                'services': '/api/services',
                'providers': '/api/providers',
                'admin': '/api/admin',
                'health': '/api/health'
            },
            'features': [
                'User authentication and authorization',
                'Service provider verification',
                'Booking management',
                'Real-time location tracking',
                'Review and rating system',
                'Multi-language support (Arabic/English)'
            ]
        }), 200
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Endpoint not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'error': 'Bad request'}), 400
    
    # Serve frontend static files
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve(path):
        static_folder_path = app.static_folder
        if static_folder_path is None:
            return jsonify({'error': 'Static folder not configured'}), 404

        if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
            return send_from_directory(static_folder_path, path)
        else:
            index_path = os.path.join(static_folder_path, 'index.html')
            if os.path.exists(index_path):
                return send_from_directory(static_folder_path, 'index.html')
            else:
                return jsonify({
                    'message': 'Maintenance Platform API',
                    'version': '1.0.0',
                    'status': 'running',
                    'docs': '/api/info',
                    'endpoints': {
                        'Authentication': '/api/auth',
                        'Services': '/api/services',
                        'Providers': '/api/providers',
                        'Admin': '/api/admin',
                        'Health Check': '/api/health'
                    }
                }), 200
    
    # Create database tables
    with app.app_context():
        db.create_all()
        
        # Create sample data if tables are empty
        if not ServiceCategory.query.first():
            create_sample_data()
    
    # File serving route
    @app.route('/uploads/<path:filename>')
    def serve_uploaded_file(filename):
        """Serve uploaded files"""
        upload_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
        return send_from_directory(upload_dir, filename)
    
    return app

def create_sample_data():
    """Create sample service categories and services"""
    try:
        # Service Categories
        categories = [
            {
                'name_ar': 'السباكة',
                'name_en': 'Plumbing',
                'description_ar': 'خدمات السباكة وإصلاح الأنابيب والحنفيات',
                'description_en': 'Plumbing services and pipe repairs',
                'icon_url': '/icons/plumbing.svg',
                'color_code': '#2196F3',
                'is_emergency_available': True,
                'sort_order': 1
            },
            {
                'name_ar': 'الكهرباء',
                'name_en': 'Electrical',
                'description_ar': 'خدمات الكهرباء والإصلاحات الكهربائية',
                'description_en': 'Electrical services and repairs',
                'icon_url': '/icons/electrical.svg',
                'color_code': '#FF9800',
                'is_emergency_available': True,
                'sort_order': 2
            },
            {
                'name_ar': 'التنظيف',
                'name_en': 'Cleaning',
                'description_ar': 'خدمات التنظيف المنزلي والمكتبي',
                'description_en': 'Home and office cleaning services',
                'icon_url': '/icons/cleaning.svg',
                'color_code': '#4CAF50',
                'is_emergency_available': False,
                'sort_order': 3
            },
            {
                'name_ar': 'النجارة',
                'name_en': 'Carpentry',
                'description_ar': 'خدمات النجارة وإصلاح الأثاث',
                'description_en': 'Carpentry and furniture repair services',
                'icon_url': '/icons/carpentry.svg',
                'color_code': '#795548',
                'is_emergency_available': False,
                'sort_order': 4
            },
            {
                'name_ar': 'صيانة التكييف',
                'name_en': 'AC Maintenance',
                'description_ar': 'صيانة وإصلاح أجهزة التكييف والتبريد',
                'description_en': 'Air conditioning maintenance and repair',
                'icon_url': '/icons/ac.svg',
                'color_code': '#00BCD4',
                'is_emergency_available': True,
                'sort_order': 5
            },
            {
                'name_ar': 'الدهان',
                'name_en': 'Painting',
                'description_ar': 'خدمات الدهان والديكور',
                'description_en': 'Painting and decoration services',
                'icon_url': '/icons/painting.svg',
                'color_code': '#E91E63',
                'is_emergency_available': False,
                'sort_order': 6
            }
        ]
        
        category_objects = []
        for cat_data in categories:
            category = ServiceCategory(**cat_data)
            db.session.add(category)
            category_objects.append(category)
        
        db.session.flush()  # Get category IDs
        
        # Services for each category
        services_data = [
            # Plumbing services
            {
                'category': category_objects[0],
                'services': [
                    {
                        'name_ar': 'إصلاح الحنفيات',
                        'name_en': 'Faucet Repair',
                        'description_ar': 'إصلاح وتركيب الحنفيات المتسربة والمعطلة',
                        'description_en': 'Repair and installation of leaky and broken faucets',
                        'base_price': 150.00,
                        'estimated_duration': 60
                    },
                    {
                        'name_ar': 'تسليك المجاري',
                        'name_en': 'Drain Unclogging',
                        'description_ar': 'تسليك المجاري والبالوعات المسدودة',
                        'description_en': 'Unclogging blocked drains and sewers',
                        'base_price': 200.00,
                        'estimated_duration': 90
                    },
                    {
                        'name_ar': 'إصلاح المراحيض',
                        'name_en': 'Toilet Repair',
                        'description_ar': 'إصلاح وصيانة المراحيض والخزانات',
                        'description_en': 'Toilet and tank repair and maintenance',
                        'base_price': 180.00,
                        'estimated_duration': 75
                    }
                ]
            },
            # Electrical services
            {
                'category': category_objects[1],
                'services': [
                    {
                        'name_ar': 'إصلاح الكهرباء',
                        'name_en': 'Electrical Repair',
                        'description_ar': 'إصلاح الأعطال الكهربائية والدوائر',
                        'description_en': 'Electrical fault and circuit repairs',
                        'base_price': 180.00,
                        'estimated_duration': 75,
                        'is_emergency_service': True,
                        'emergency_surcharge_percentage': 50.00
                    },
                    {
                        'name_ar': 'تركيب الإضاءة',
                        'name_en': 'Light Installation',
                        'description_ar': 'تركيب وحدات الإضاءة والثريات',
                        'description_en': 'Installation of lighting fixtures and chandeliers',
                        'base_price': 120.00,
                        'estimated_duration': 45
                    },
                    {
                        'name_ar': 'تركيب المراوح',
                        'name_en': 'Fan Installation',
                        'description_ar': 'تركيب وصيانة المراوح السقفية',
                        'description_en': 'Ceiling fan installation and maintenance',
                        'base_price': 160.00,
                        'estimated_duration': 60
                    }
                ]
            },
            # Cleaning services
            {
                'category': category_objects[2],
                'services': [
                    {
                        'name_ar': 'تنظيف المنازل',
                        'name_en': 'House Cleaning',
                        'description_ar': 'تنظيف شامل للمنازل والشقق',
                        'description_en': 'Complete house and apartment cleaning',
                        'base_price': 250.00,
                        'price_unit': 'hourly',
                        'estimated_duration': 180
                    },
                    {
                        'name_ar': 'تنظيف السجاد',
                        'name_en': 'Carpet Cleaning',
                        'description_ar': 'تنظيف وغسيل السجاد والموكيت',
                        'description_en': 'Carpet and rug cleaning and washing',
                        'base_price': 80.00,
                        'price_unit': 'per_item',
                        'estimated_duration': 120
                    }
                ]
            }
        ]
        
        for service_group in services_data:
            category = service_group['category']
            for service_data in service_group['services']:
                service = Service(
                    category_id=category.id,
                    **service_data
                )
                db.session.add(service)
        
        # Egyptian Governorates
        governorates = [
            {'name_ar': 'القاهرة', 'name_en': 'Cairo', 'code': 'CAI', 'center_latitude': 30.0444, 'center_longitude': 31.2357},
            {'name_ar': 'الجيزة', 'name_en': 'Giza', 'code': 'GIZ', 'center_latitude': 30.0131, 'center_longitude': 31.2089},
            {'name_ar': 'الإسكندرية', 'name_en': 'Alexandria', 'code': 'ALX', 'center_latitude': 31.2001, 'center_longitude': 29.9187},
            {'name_ar': 'القليوبية', 'name_en': 'Qalyubia', 'code': 'QLY', 'center_latitude': 30.1792, 'center_longitude': 31.2045},
            {'name_ar': 'بورسعيد', 'name_en': 'Port Said', 'code': 'PTS', 'center_latitude': 31.2653, 'center_longitude': 32.3019},
            {'name_ar': 'السويس', 'name_en': 'Suez', 'code': 'SUZ', 'center_latitude': 29.9668, 'center_longitude': 32.5498},
            {'name_ar': 'الإسماعيلية', 'name_en': 'Ismailia', 'code': 'ISM', 'center_latitude': 30.5965, 'center_longitude': 32.2715},
            {'name_ar': 'الدقهلية', 'name_en': 'Dakahlia', 'code': 'DAK', 'center_latitude': 31.0409, 'center_longitude': 31.3785},
            {'name_ar': 'الشرقية', 'name_en': 'Sharqia', 'code': 'SHR', 'center_latitude': 30.5965, 'center_longitude': 31.5041},
            {'name_ar': 'الغربية', 'name_en': 'Gharbia', 'code': 'GHR', 'center_latitude': 30.8754, 'center_longitude': 31.0335}
        ]
        
        for gov_data in governorates:
            governorate = Governorate(**gov_data)
            db.session.add(governorate)
        
        db.session.commit()
        print("✅ Sample data created successfully!")
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error creating sample data: {e}")

# Create Flask app
app = create_app()

# File serving endpoint for documents
@app.route('/uploads/documents/<filename>')
def uploaded_documents(filename):
    """Serve uploaded document files"""
    upload_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads', 'documents')
    return send_from_directory(upload_dir, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

