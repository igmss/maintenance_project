# Foreign Key Constraint Fix - provider_locations Table

## Problem Summary

The application was failing with a foreign key constraint violation:

```
(psycopg2.errors.ForeignKeyViolation) insert or update on table "provider_locations" violates foreign key constraint "provider_locations_provider_id_fkey"
DETAIL: Key (provider_id)=(9033233d-250f-4768-97af-0c3e8f461c82) is not present in table "users".
```

## Root Cause Analysis

There was a mismatch between the Python model and the database schema:

1. **Python Model** (`backend/src/models/location.py:9`): 
   ```python
   provider_id = db.Column(db.String(36), db.ForeignKey('service_provider_profiles.id'), nullable=False)
   ```

2. **Database Schema** (`database/supabase_setup.sql:183`):
   ```sql
   provider_id UUID REFERENCES users(id) ON DELETE CASCADE,
   ```

3. **Code Logic** (`backend/src/routes/providers.py:224`):
   ```python
   provider_id=current_user.provider_profile.id  # This is the service_provider_profiles.id
   ```

The code was using `current_user.provider_profile.id` (which exists in `service_provider_profiles` table) but the database constraint expected the `provider_id` to reference `users.id`.

## Solution Applied

### 1. Updated Python Code
Changed all instances of using `current_user.provider_profile.id` to `current_user.id` for ProviderLocation operations:

**Files modified:**
- `/workspace/backend/src/routes/providers.py` (4 instances)
- `/workspace/backend/src/routes/providers_updated.py` (2 instances)

### 2. Updated Python Model
Changed the foreign key reference in the ProviderLocation model:

**File:** `/workspace/backend/src/models/location.py`
```python
# Before:
provider_id = db.Column(db.String(36), db.ForeignKey('service_provider_profiles.id'), nullable=False)

# After:  
provider_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
```

### 3. Fixed Database Queries
Updated join logic in provider queries to properly link through the User table:

**Before:**
```python
ServiceProviderProfile.id == ProviderLocation.provider_id
```

**After:**
```python
ServiceProviderProfile.user_id == User.id
User.id == ProviderLocation.provider_id
```

## Database Schema Consistency

The fix aligns with the existing database pattern where most provider-related tables reference `users.id`:

- ✅ `provider_locations.provider_id` → `users.id`
- ✅ `bookings.provider_id` → `users.id` 
- ✅ `booking_reviews.provider_id` → `users.id`
- ✅ `payment_transactions.provider_id` → `users.id`
- ✅ `provider_documents.provider_id` → `service_provider_profiles.id` (exception - correctly designed)

## Additional Schema Fixes Needed

The database may still be missing some columns that the Python model expects. Apply this script to add missing columns:

```sql
-- Run: /workspace/database/fix_provider_locations_table.sql
```

This adds:
- `is_online BOOLEAN DEFAULT true`
- `battery_level INTEGER`  
- `last_updated TIMESTAMP WITH TIME ZONE`

## Testing

After applying these fixes, the location update API calls should work correctly:

1. **Provider status updates** (`POST /providers/status`)
2. **Location updates** (`POST /providers/location`)  
3. **Live location tracking** (`POST /providers/live-location`)

The foreign key constraint error should be resolved as the `provider_id` will now correctly reference valid `users.id` values.