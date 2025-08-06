import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Loader2, Eye, EyeOff, ArrowRight } from 'lucide-react';
import { useAuth } from '../lib/auth.jsx';
import { isValidEmail, isValidEgyptianPhone } from '../lib/utils';

const LoginPage = () => {
  const [formData, setFormData] = useState({
    email_or_phone: '',
    password: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    // Clear error when user starts typing
    if (error) setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      // Validate input
      if (!formData.email_or_phone || !formData.password) {
        throw new Error('يرجى ملء جميع الحقول المطلوبة');
      }

      // Validate email or phone format
      const isEmail = formData.email_or_phone.includes('@');
      if (isEmail && !isValidEmail(formData.email_or_phone)) {
        throw new Error('يرجى إدخال بريد إلكتروني صحيح');
      }
      if (!isEmail && !isValidEgyptianPhone(formData.email_or_phone)) {
        throw new Error('يرجى إدخال رقم هاتف مصري صحيح');
      }

      // Send correct parameters to backend
      const loginData = {
        email_or_phone: formData.email_or_phone,  // Backend expects this exact parameter name
        password: formData.password
      };

      const response = await login(loginData);
      
      // Redirect based on user type
      const redirectPath = {
        customer: '/dashboard',
        service_provider: '/provider-dashboard',
        admin: '/admin-dashboard'
      }[response.user.user_type] || '/dashboard';
      
      navigate(redirectPath);
    } catch (err) {
      setError(err.message || 'حدث خطأ أثناء تسجيل الدخول');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Header */}
        <div className="text-center mb-8">
          <Link to="/" className="inline-block">
            <h1 className="text-3xl font-bold text-blue-600 mb-2">منصة الصيانة</h1>
          </Link>
          <p className="text-gray-600">أهلاً بك مرة أخرى</p>
        </div>

        <Card className="shadow-lg">
          <CardHeader className="space-y-1">
            <CardTitle className="text-2xl text-center">تسجيل الدخول</CardTitle>
            <CardDescription className="text-center">
              أدخل بياناتك للوصول إلى حسابك
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              {error && (
                <Alert variant="destructive">
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}

              <div className="space-y-2">
                <Label htmlFor="email_or_phone">البريد الإلكتروني أو رقم الهاتف</Label>
                <Input
                  id="email_or_phone"
                  name="email_or_phone"
                  type="text"
                  placeholder="example@email.com أو 01012345678"
                  value={formData.email_or_phone}
                  onChange={handleChange}
                  required
                  className="text-right"
                  dir="ltr"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="password">كلمة المرور</Label>
                <div className="relative">
                  <Input
                    id="password"
                    name="password"
                    type={showPassword ? 'text' : 'password'}
                    placeholder="أدخل كلمة المرور"
                    value={formData.password}
                    onChange={handleChange}
                    required
                    className="pr-10"
                  />
                  <button
                    type="button"
                    className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                    onClick={() => setShowPassword(!showPassword)}
                  >
                    {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </button>
                </div>
              </div>

              <div className="flex items-center justify-between">
                <Link 
                  to="/forgot-password" 
                  className="text-sm text-blue-600 hover:text-blue-500"
                >
                  نسيت كلمة المرور؟
                </Link>
              </div>

              <Button 
                type="submit" 
                className="w-full" 
                disabled={loading}
              >
                {loading ? (
                  <>
                    <Loader2 className="ml-2 h-4 w-4 animate-spin" />
                    جاري تسجيل الدخول...
                  </>
                ) : (
                  <>
                    تسجيل الدخول
                    <ArrowRight className="mr-2 h-4 w-4" />
                  </>
                )}
              </Button>
            </form>

            <div className="mt-6">
              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-gray-300" />
                </div>
                <div className="relative flex justify-center text-sm">
                  <span className="px-2 bg-white text-gray-500">أو</span>
                </div>
              </div>

              <div className="mt-6 text-center">
                <p className="text-sm text-gray-600">
                  ليس لديك حساب؟{' '}
                  <Link 
                    to="/register" 
                    className="font-medium text-blue-600 hover:text-blue-500"
                  >
                    إنشاء حساب جديد
                  </Link>
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Back to Home */}
        <div className="mt-8 text-center">
          <Link 
            to="/" 
            className="text-sm text-gray-600 hover:text-gray-800 inline-flex items-center"
          >
            العودة إلى الصفحة الرئيسية
            <ArrowRight className="mr-1 h-4 w-4" />
          </Link>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;

