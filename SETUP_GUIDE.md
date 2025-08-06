# Complete Setup Guide - Maintenance Service Platform

This guide will walk you through setting up the entire maintenance service platform from scratch.

## 📋 Prerequisites

### Required Software
- **Python 3.11+** - Backend development
- **Node.js 20+** - Frontend development
- **Flutter 3.24+** - Mobile app development
- **Git** - Version control
- **VS Code** - Recommended IDE

### Required Accounts
- **Supabase Account** - Database and backend services
- **GitHub Account** - Code repository and CI/CD
- **Render Account** - Backend deployment
- **Netlify Account** - Frontend deployment

## 🗄️ Database Setup (Supabase)

### 1. Create Supabase Project
1. Go to [Supabase Dashboard](https://supabase.com/dashboard)
2. Click "New Project"
3. Choose organization and enter project details:
   - **Name**: Maintenance Platform
   - **Database Password**: Create a strong password
   - **Region**: Choose closest to Egypt (Europe West)

### 2. Configure Database
1. Go to **SQL Editor** in your Supabase dashboard
2. Run the following scripts in order:

#### Step 1: Create Tables
```sql
-- Copy and paste content from: database/create_tables_fixed.sql
-- This creates all 18 core tables with relationships
```

#### Step 2: Add Online Status
```sql
-- Copy and paste content from: database/add_is_online_column.sql
-- This adds real-time provider tracking
```

#### Step 3: Enable Security
```sql
-- Copy and paste content from: database/enable_rls_final.sql
-- This enables Row Level Security for data protection
```

### 3. Get Database Credentials
1. Go to **Settings > API** in Supabase
2. Copy the following values:
   - **Project URL**: `https://your-project-id.supabase.co`
   - **Anon Key**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`
   - **Service Role Key**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`

3. Go to **Settings > Database** and copy:
   - **Connection String**: `postgresql://postgres:[password]@[host]:5432/postgres`

## 🔧 Backend Setup (Flask API)

### 1. Environment Setup
```bash
cd backend
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your credentials
nano .env
```

Add your Supabase credentials:
```env
# Supabase Configuration
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your_anon_key_here
SUPABASE_SERVICE_KEY=your_service_key_here
DATABASE_URL=postgresql://postgres:your_password@db.your-project-id.supabase.co:5432/postgres

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your_secret_key_here
JWT_SECRET_KEY=your_jwt_secret_here

# Redis Configuration (optional for development)
REDIS_URL=redis://localhost:6379/0
```

### 3. Run Backend Server
```bash
python src/main.py
```

The API will be available at: `http://localhost:5000`

### 4. Test API
```bash
# Health check
curl http://localhost:5000/api/health

# Get service categories
curl http://localhost:5000/api/services/categories
```

## 🎨 Frontend Web App Setup (React)

### 1. Install Dependencies
```bash
cd frontend-web
pnpm install
# or: npm install
```

### 2. Environment Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit .env file
nano .env
```

Add your configuration:
```env
# API Configuration
VITE_API_BASE_URL=http://localhost:5000/api
VITE_SUPABASE_URL=https://your-project-id.supabase.co
VITE_SUPABASE_ANON_KEY=your_anon_key_here

# App Configuration
VITE_APP_NAME=Maintenance Platform
VITE_APP_VERSION=1.0.0
```

### 3. Run Development Server
```bash
pnpm run dev
# or: npm run dev
```

The web app will be available at: `http://localhost:5173`

### 4. Test Web App
1. Open browser to `http://localhost:5173`
2. Register a new customer account
3. Browse service categories
4. Test booking flow

## 👑 Admin Dashboard Setup (React)

### 1. Install Dependencies
```bash
cd frontend-admin
pnpm install
```

### 2. Environment Configuration
```bash
cp .env.example .env
nano .env
```

Add configuration:
```env
VITE_API_BASE_URL=http://localhost:5000/api
VITE_SUPABASE_URL=https://your-project-id.supabase.co
VITE_SUPABASE_ANON_KEY=your_anon_key_here
```

### 3. Run Admin Dashboard
```bash
pnpm run dev
```

Available at: `http://localhost:5174`

### 4. Admin Login
- **Email**: admin@maintenanceplatform.com
- **Password**: admin123

## 📱 Mobile App Setup (Flutter)

### 1. Install Flutter Dependencies
```bash
cd mobile-flutter
flutter pub get
```

### 2. Configure Supabase
Edit `lib/config/supabase_config.dart`:
```dart
class SupabaseConfig {
  static const String supabaseUrl = 'https://your-project-id.supabase.co';
  static const String supabaseAnonKey = 'your_anon_key_here';
}
```

### 3. Configure Android
Edit `android/app/build.gradle`:
```gradle
android {
    compileSdkVersion 34
    
    defaultConfig {
        minSdkVersion 21
        targetSdkVersion 34
    }
}
```

### 4. Configure iOS
Edit `ios/Runner/Info.plist`:
```xml
<key>NSLocationWhenInUseUsageDescription</key>
<string>This app needs location access to find nearby service providers.</string>
```

### 5. Run Mobile App
```bash
# Check connected devices
flutter devices

# Run on device/emulator
flutter run
```

## 🚀 Production Deployment

### 1. Backend Deployment (Render)

#### Create Render Account
1. Go to [Render.com](https://render.com)
2. Sign up with GitHub account
3. Connect your repository

#### Deploy Backend
1. Create new **Web Service**
2. Connect GitHub repository
3. Configure build settings:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python src/main.py`
   - **Environment**: Python 3.11

4. Add environment variables:
   - `SUPABASE_URL`
   - `SUPABASE_ANON_KEY`
   - `DATABASE_URL`
   - `JWT_SECRET_KEY`
   - `FLASK_ENV=production`

### 2. Frontend Deployment (Netlify)

#### Deploy Web App
```bash
cd frontend-web

# Build for production
pnpm run build

# Deploy to Netlify
npx netlify-cli deploy --prod --dir=dist
```

#### Deploy Admin Dashboard
```bash
cd frontend-admin
pnpm run build
npx netlify-cli deploy --prod --dir=dist
```

### 3. Mobile App Deployment

#### Android (Google Play)
```bash
flutter build apk --release
flutter build appbundle --release
```

#### iOS (App Store)
```bash
flutter build ios --release
```

## 🔒 Security Configuration

### 1. Enable Row Level Security
Already configured in database setup scripts.

### 2. Configure CORS
Backend CORS is configured for production domains.

### 3. Environment Variables
Never commit `.env` files to version control.

### 4. API Rate Limiting
Configured in Flask app for production.

## 📊 Monitoring & Analytics

### 1. Supabase Dashboard
- Monitor database performance
- View API usage statistics
- Check error logs

### 2. Render Dashboard
- Monitor backend performance
- View deployment logs
- Check resource usage

### 3. Netlify Analytics
- Monitor frontend performance
- View visitor statistics
- Check build logs

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

## 🔧 Troubleshooting

### Common Issues

#### Database Connection Error
- Check Supabase credentials in `.env`
- Verify database is running
- Check network connectivity

#### CORS Error
- Verify API_BASE_URL in frontend `.env`
- Check backend CORS configuration
- Ensure backend is running

#### Flutter Build Error
- Run `flutter clean && flutter pub get`
- Check Flutter version: `flutter --version`
- Verify Android/iOS setup

#### Authentication Error
- Check JWT_SECRET_KEY configuration
- Verify token expiration settings
- Check user permissions

### Getting Help

1. **Documentation**: Check `/documentation` folder
2. **Logs**: Check application logs for errors
3. **Database**: Use Supabase dashboard for database issues
4. **API**: Test endpoints with Postman/curl

## ✅ Verification Checklist

### Backend ✓
- [ ] Database tables created successfully
- [ ] API endpoints responding
- [ ] Authentication working
- [ ] Environment variables configured

### Frontend ✓
- [ ] Web app loads without errors
- [ ] User registration/login working
- [ ] Service categories displaying
- [ ] API calls successful

### Admin Dashboard ✓
- [ ] Admin login working
- [ ] Dashboard statistics loading
- [ ] User management functional
- [ ] Provider verification working

### Mobile App ✓
- [ ] App builds and runs
- [ ] Location permissions working
- [ ] API integration functional
- [ ] Navigation working

### Production ✓
- [ ] Backend deployed to Render
- [ ] Frontend deployed to Netlify
- [ ] Environment variables configured
- [ ] SSL certificates active
- [ ] Domain names configured

## 🎉 Success!

Your maintenance service platform is now fully set up and ready for use!

### Next Steps
1. **Test all user flows** thoroughly
2. **Configure payment gateways** for Egypt
3. **Set up monitoring** and alerts
4. **Plan marketing strategy** for launch
5. **Prepare customer support** processes

### Production URLs
- **Web App**: https://your-app.netlify.app
- **Admin Dashboard**: https://your-admin.netlify.app
- **API**: https://your-api.onrender.com
- **Mobile App**: Available on App Store & Google Play

**Congratulations! Your platform is ready to serve the Egyptian maintenance market!** 🚀

