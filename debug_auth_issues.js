// Debug script to check authentication issues
// Open browser console and run this to debug auth problems

console.log('🔍 DEBUG: Admin Authentication Status');
console.log('=====================================');

// Check localStorage
const adminToken = localStorage.getItem('admin_token');
const adminUser = localStorage.getItem('admin_user');

console.log('📦 LocalStorage:');
console.log('  admin_token:', adminToken ? 'EXISTS' : 'NOT FOUND');
console.log('  admin_user:', adminUser ? 'EXISTS' : 'NOT FOUND');

if (adminUser) {
    try {
        const user = JSON.parse(adminUser);
        console.log('  User type:', user.user_type);
        console.log('  User email:', user.email);
        console.log('  User status:', user.status);
    } catch (e) {
        console.log('  ❌ Invalid user data in localStorage');
    }
}

// Check if token is valid by making a test request
if (adminToken) {
    console.log('\n🔬 Testing API Authentication...');
    
    fetch('https://maintenance-platform-backend.onrender.com/api/admin/dashboard/stats', {
        headers: {
            'Authorization': `Bearer ${adminToken}`,
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        console.log('  Response status:', response.status);
        if (response.status === 200) {
            console.log('  ✅ Token is VALID');
        } else if (response.status === 401) {
            console.log('  ❌ Token is INVALID or EXPIRED');
        } else {
            console.log('  ⚠️  Unexpected response:', response.statusText);
        }
        return response.text();
    })
    .then(data => {
        console.log('  Response data:', data.substring(0, 100) + '...');
    })
    .catch(error => {
        console.log('  ❌ Network error:', error.message);
    });
} else {
    console.log('\n❌ No token found - user needs to login');
}

// Instructions
console.log('\n📋 TROUBLESHOOTING STEPS:');
console.log('1. If no token found → Login with admin credentials');
console.log('2. If token invalid → Clear localStorage and re-login');
console.log('3. If user_type !== "admin" → Use proper admin account');
console.log('4. If network errors → Check backend is running');

// Helper function to clear auth
window.clearAdminAuth = function() {
    localStorage.removeItem('admin_token');
    localStorage.removeItem('admin_user');
    console.log('✅ Admin auth cleared. Please refresh and login again.');
}

console.log('\n🧹 To clear auth and start fresh, run: clearAdminAuth()');