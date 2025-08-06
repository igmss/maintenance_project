# Maintenance Service Platform - Complete Project

A comprehensive maintenance service platform built for the Egyptian market, similar to Uber for maintenance services. This platform connects customers with verified service providers for home and business maintenance needs.

## 🎯 Project Overview

### Market Opportunity
- **USD 12.12B Market**: Egyptian maintenance services by 2030
- **11.60% CAGR**: Rapid market growth
- **72% Internet Penetration**: Strong digital adoption
- **First-Mover Advantage**: Comprehensive platform in underserved market

### Key Features
- ✅ **Real-time Provider Tracking**: GPS-based online/offline status
- ✅ **Bilingual Support**: Arabic/English with RTL layouts
- ✅ **Multi-platform**: Web, Mobile (Flutter), Admin Dashboard
- ✅ **Secure Authentication**: JWT with role-based access
- ✅ **Payment Integration**: Egyptian payment gateways
- ✅ **Provider Verification**: Document upload and admin approval
- ✅ **Real-time Notifications**: In-app, push, and email
- ✅ **Location Services**: GPS tracking and service areas
- ✅ **Review System**: Customer and provider ratings

## 📁 Project Structure

```
maintenance-platform-complete/
├── backend/                    # Flask API Backend
├── frontend-web/              # React Web Application
├── frontend-admin/            # React Admin Dashboard
├── mobile-flutter/            # Flutter Mobile App
├── database/                  # SQL Scripts & Schema
├── documentation/             # Project Documentation
├── deployment/                # CI/CD & Deployment Configs
└── README.md                  # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 20+
- Flutter 3.24+
- PostgreSQL (Supabase)
- Git

### 1. Database Setup
```bash
# Go to Supabase Dashboard: https://supabase.com/dashboard
# SQL Editor > New Query
# Run scripts in this order:
1. database/create_tables_fixed.sql
2. database/add_is_online_column.sql
3. database/enable_rls_final.sql
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your Supabase credentials

# Run development server
python src/main.py
```

### 3. Frontend Web App Setup
```bash
cd frontend-web
pnpm install

# Configure environment
cp .env.example .env
# Edit .env with your API URLs

# Run development server
pnpm run dev
```

### 4. Admin Dashboard Setup
```bash
cd frontend-admin
pnpm install

# Configure environment
cp .env.example .env
# Edit .env with your API URLs

# Run development server
pnpm run dev
```

### 5. Mobile App Setup
```bash
cd mobile-flutter
flutter pub get

# Configure Supabase
# Edit lib/config/supabase_config.dart

# Run on device/emulator
flutter run
```

## 🔧 Technology Stack

### Backend
- **Framework**: Flask (Python)
- **Database**: PostgreSQL (Supabase)
- **Authentication**: JWT with bcrypt
- **API**: RESTful with comprehensive endpoints
- **Caching**: Redis for session management
- **File Storage**: Supabase Storage

### Frontend Web
- **Framework**: React 18 with TypeScript
- **Styling**: Tailwind CSS + Shadcn/UI
- **State Management**: React Context + Hooks
- **Routing**: React Router v6
- **Build Tool**: Vite
- **Icons**: Lucide React

### Mobile App
- **Framework**: Flutter 3.24
- **State Management**: Riverpod
- **Database**: Hive (local) + Supabase (remote)
- **Maps**: Google Maps
- **Notifications**: Firebase
- **Internationalization**: flutter_localizations

### Admin Dashboard
- **Framework**: React 18 with TypeScript
- **UI Components**: Shadcn/UI
- **Charts**: Recharts
- **Data Tables**: TanStack Table
- **Authentication**: JWT with role-based access

### Database
- **Primary**: PostgreSQL (Supabase)
- **Caching**: Redis
- **File Storage**: Supabase Storage
- **Security**: Row Level Security (RLS)
- **Backup**: Automated Supabase backups

## 🌐 Deployment

### Production URLs
- **Backend API**: Deploy to Render
- **Web App**: Deploy to Netlify
- **Admin Dashboard**: Deploy to Netlify
- **Mobile App**: App Store & Google Play

### Environment Variables
```bash
# Backend (.env)
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_anon_key
DATABASE_URL=your_database_url
JWT_SECRET_KEY=your_jwt_secret
FLASK_ENV=production

# Frontend (.env)
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_anon_key
VITE_API_BASE_URL=your_backend_url
```

### Deployment Commands
```bash
# Backend (Render)
git push origin main  # Auto-deploys via GitHub Actions

# Frontend (Netlify)
pnpm run build
netlify deploy --prod --dir=dist

# Mobile (App Stores)
flutter build apk --release
flutter build ios --release
```

## 📊 API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/profile` - Get user profile
- `PUT /api/auth/profile` - Update profile

### Services
- `GET /api/services/categories` - Get service categories
- `GET /api/services/categories/{id}/services` - Get category services
- `POST /api/services/search` - Search providers
- `POST /api/services/bookings` - Create booking

### Providers
- `GET /api/providers/online` - Get online providers
- `POST /api/providers/status` - Toggle online/offline
- `POST /api/providers/location` - Update location
- `GET /api/providers/{id}` - Get provider profile

### Admin
- `GET /api/admin/dashboard/stats` - Dashboard statistics
- `GET /api/admin/users` - User management
- `GET /api/admin/bookings` - Booking management
- `PUT /api/admin/users/{id}/status` - Update user status

## 🔒 Security Features

### Authentication & Authorization
- JWT tokens with refresh mechanism
- Role-based access control (Customer, Provider, Admin)
- Password hashing with bcrypt
- Session management with Redis

### Data Protection
- Row Level Security (RLS) on all tables
- Input validation and sanitization
- SQL injection prevention
- XSS protection with CSP headers

### API Security
- Rate limiting on all endpoints
- CORS configuration for frontend integration
- Request/response logging
- Error handling without data exposure

## 📱 Mobile App Features

### Customer App
- Service category browsing
- Real-time provider search
- GPS-based provider matching
- Booking management
- Payment integration
- Review and rating system

### Provider App
- Online/offline status toggle
- Real-time location tracking
- Booking request management
- Earnings dashboard
- Document upload for verification
- Service area management

## 🎨 Design System

### Colors
- **Primary**: Deep Blue (#1B365D)
- **Secondary**: Vibrant Teal (#00A693)
- **Accent**: Warm Orange (#FF6B35)
- **Success**: Green (#10B981)
- **Warning**: Amber (#F59E0B)
- **Error**: Red (#EF4444)

### Typography
- **Arabic**: Cairo font family
- **English**: Inter font family
- **RTL Support**: Proper right-to-left layouts

### Components
- Material 3 design system
- Consistent spacing and sizing
- Accessible color contrasts
- Mobile-first responsive design

## 📈 Business Model

### Revenue Streams
1. **Commission**: 10-15% per completed booking
2. **Subscription**: Premium provider memberships
3. **Advertising**: Featured provider listings
4. **Insurance**: Optional service insurance

### Target Market
- **Primary**: Urban Egyptian households
- **Secondary**: Small businesses and offices
- **Tertiary**: Property management companies

### Competitive Advantages
- Real-time provider tracking
- Comprehensive verification system
- Bilingual Arabic/English support
- Local payment gateway integration
- Egyptian market focus

## 🧪 Testing

### Backend Testing
```bash
cd backend
pytest tests/ -v --cov=src
```

### Frontend Testing
```bash
cd frontend-web
pnpm test
```

### Mobile Testing
```bash
cd mobile-flutter
flutter test
```

## 📚 Documentation

- `documentation/market_research.md` - Market analysis
- `documentation/system_architecture.md` - Technical architecture
- `documentation/design_concept.md` - UI/UX design
- `documentation/testing_report.md` - QA and testing
- `documentation/deployment_guide.md` - Deployment instructions
- `documentation/SECURITY_CONFIGURATION_GUIDE.md` - Security setup

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new features
5. Submit a pull request

## 📄 License

This project is proprietary software. All rights reserved.

## 📞 Support

For technical support or business inquiries:
- Email: support@maintenanceplatform.com
- Documentation: See `/documentation` folder
- Issues: Create GitHub issues for bugs

## 🎉 Acknowledgments

- Built with modern web and mobile technologies
- Designed for the Egyptian market
- Enterprise-grade security and scalability
- Production-ready deployment configurations

---

**Ready to launch your maintenance service platform!** 🚀

This complete project includes everything needed to build and deploy a successful maintenance service marketplace in Egypt.

