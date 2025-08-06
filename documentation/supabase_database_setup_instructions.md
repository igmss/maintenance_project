# Supabase Database Setup Instructions

## Database Configuration Updated ✅

I've successfully updated all project configurations to use your real Supabase database:

**Supabase Project Details:**
- **Project URL**: https://mxfduvxgvobbnazeovfd.supabase.co
- **Project ID**: mxfduvxgvobbnazeovfd
- **Database**: PostgreSQL with PostGIS extensions

## Files Updated with Real Supabase Configuration

### Backend Configuration ✅
- **Environment File**: `/maintenance-platform-backend/.env`
- **Render Deployment**: `/maintenance-platform-backend/render.yaml`
- **Database URL**: Updated to use your Supabase PostgreSQL connection

### Frontend Configuration ✅
- **Web App Environment**: `/maintenance-platform-web/.env`
- **Admin Dashboard Environment**: `/maintenance-platform-admin/.env`
- **API Client**: Updated to use correct environment variable names

### Mobile App Configuration ✅
- **Flutter Config**: `/maintenance_platform_mobile/lib/config/supabase_config.dart`
- **Main App**: Updated to initialize Supabase with your credentials

### Deployment Configuration ✅
- **GitHub Actions**: Updated all CI/CD pipelines with real Supabase URLs
- **Render Config**: Updated to use your database instead of managed database
- **Netlify Config**: Environment variables updated for production deployment

## Next Steps: Database Schema Setup

To complete the setup, you need to run the database schema script in your Supabase project:

### Method 1: Supabase Dashboard (Recommended)

1. **Go to Supabase Dashboard**: https://supabase.com/dashboard/project/mxfduvxgvobbnazeovfd
2. **Navigate to SQL Editor**: Click on "SQL Editor" in the left sidebar
3. **Create New Query**: Click "New Query"
4. **Copy and Paste**: Copy the entire content from `/home/ubuntu/supabase_setup.sql`
5. **Execute**: Click "Run" to execute the SQL script
6. **Verify**: Check that all tables were created successfully

### Method 2: Command Line (Alternative)

If you have `psql` installed locally:

```bash
# Connect to your Supabase database
psql "postgresql://postgres.mxfduvxgvobbnazeovfd:cWtHkFawo6+EfgCmHbSel73Smpz3I0zHrohYwsex3JwwfyRbXSDj+J5nS/7IPFiuopukH+c45HNNj5aky8miAw==@aws-0-us-east-1.pooler.supabase.com:6543/postgres"

# Run the setup script
\i /path/to/supabase_setup.sql
```

## Database Schema Overview

The setup script will create:

### Core Tables
- **Users & Profiles**: Customer and service provider management
- **Services & Categories**: Service catalog with Arabic/English support
- **Bookings & Reviews**: Complete booking workflow and rating system
- **Location Data**: GPS tracking and service areas
- **Payment Transactions**: Financial transaction management
- **Notifications**: Multi-channel notification system

### Security Features
- **Row Level Security (RLS)**: Data access control policies
- **User Authentication**: Supabase Auth integration
- **Data Encryption**: Secure data storage and transmission

### Sample Data
- **Service Categories**: 8 main categories (Plumbing, Electrical, etc.)
- **Egyptian Governorates**: Complete location hierarchy
- **Admin User**: Default admin account for testing

## Testing Database Connection

After running the setup script, you can test the connection:

### Test API Connection
```bash
# Test health endpoint (should work immediately)
curl https://maintenance-platform-api.onrender.com/api/health

# Test database connection (after backend deployment)
curl https://maintenance-platform-api.onrender.com/api/services/categories
```

### Test Frontend Connection
1. Start the web application: `cd maintenance-platform-web && pnpm run dev`
2. Open browser to `http://localhost:5173`
3. Try registering a new user account
4. Check that data is being saved to Supabase

## Environment Variables Summary

All applications now use these Supabase configurations:

```env
# Supabase Configuration
SUPABASE_URL=https://mxfduvxgvobbnazeovfd.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im14ZmR1dnhndm9iYm5hemVvdmZkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ0MDk2ODMsImV4cCI6MjA2OTk4NTY4M30.j8u43-htgzBkRJxvrJUCO9bpc__V1fbFVQOezZRfGPA
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im14ZmR1dnhndm9iYm5hemVvdmZkIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NDQwOTY4MywiZXhwIjoyMDY5OTg1NjgzfQ.FWDK2Jl-cEVUVKhACB26iZPD0k0qZxaOhXpXE6JPx80

# Database URL
DATABASE_URL=postgresql://postgres.mxfduvxgvobbnazeovfd:cWtHkFawo6+EfgCmHbSel73Smpz3I0zHrohYwsex3JwwfyRbXSDj+J5nS/7IPFiuopukH+c45HNNj5aky8miAw==@aws-0-us-east-1.pooler.supabase.com:6543/postgres
```

## Deployment Ready ✅

Your maintenance service platform is now configured to use your real Supabase database and is ready for deployment:

1. **Backend**: Deploy to Render using the updated `render.yaml`
2. **Frontend**: Deploy to Netlify with updated environment variables
3. **Mobile**: Build and deploy to app stores with Supabase integration
4. **Database**: Run the setup script to create all necessary tables

The platform will now use your production Supabase database for all data storage and user management!

## Support

If you encounter any issues during database setup:
1. Check the Supabase dashboard for error messages
2. Verify all environment variables are correctly set
3. Ensure the database setup script completed successfully
4. Test API endpoints to confirm database connectivity

Your maintenance service platform is now fully configured and ready for production deployment! 🚀

