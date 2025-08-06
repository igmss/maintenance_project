import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Checkbox } from '@/components/ui/checkbox';
import { Loader2, Eye, EyeOff, ArrowRight, User, Wrench } from 'lucide-react';
import { useAuth } from '../lib/auth.jsx';
import { isValidEmail, isValidEgyptianPhone } from '../lib/utils';

const RegisterPage = () => {
  const [userType, setUserType] = useState('customer');
  const [formData, setFormData] = useState({
    email: '',
    phone: '',
    password: '',
    confirmPassword: '',
    first_name: '',
    last_name: '',
    user_type: 'customer',
    preferred_language: 'ar',
    // Service provider specific fields
    national_id: '',
    date_of_birth: '',
    // Terms acceptance
    acceptTerms: false
  });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData({
      ...formData,
      [name]: type === 'checkbox' ? checked : value
    });
    // Clear error when user starts typing
    if (error) setError('');
  };

  const handleUserTypeChange = (type) => {
    setUserType(type);
    setFormData({
      ...formData,
      user_type: type
    });
  };

  const validateForm = () => {
    // Basic validation
    if (!formData.email || !formData.phone || !formData.password || 
        !formData.first_name || !formData.last_name) {
      throw new Error('يرجى ملء جميع الحقول المطلوبة');
    }

    // Email validation
    if (!isValidEmail(formData.email)) {
      throw new Error('يرجى إدخال بريد إلكتروني صحيح');
    }

    // Phone validation
    if (!isValidEgyptianPhone(formData.phone)) {
      throw new Error('يرجى إدخال رقم هاتف مصري صحيح (مثال: 01123456789)');
    }

    // Password validation
    if (formData.password.length < 8) {
      throw new Error('كلمة المرور يجب أن تكون 8 أحرف على الأقل');
    }

    if (formData.password !== formData.confirmPassword) {
      throw new Error('كلمة المرور وتأكيد كلمة المرور غير متطابقتين');
    }

    // Service provider specific validation
    if (formData.user_type === 'service_provider') {
      if (!formData.national_id || !formData.date_of_birth) {
        throw new Error('يرجى ملء الرقم القومي وتاريخ الميلاد لمقدمي الخدمة');
      }

      if (formData.national_id.length !== 14) {
        throw new Error('الرقم القومي يجب أن يكون 14 رقم');
      }

      // Validate date of birth (must be at least 18 years old)
      const birthDate = new Date(formData.date_of_birth);
      const today = new Date();
      const age = today.getFullYear() - birthDate.getFullYear();
      if (age < 18) {
        throw new Error('يجب أن يكون عمرك 18 سنة على الأقل');
      }
    }

    // Terms acceptance
    if (!formData.acceptTerms) {
      throw new Error('يجب الموافقة على الشروط والأحكام');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      validateForm();

      // Prepare data for API
      const registrationData = {
        email: formData.email,
        phone: formData.phone,
        password: formData.password,
        first_name: formData.first_name,
        last_name: formData.last_name,
        user_type: formData.user_type,
        preferred_language: formData.preferred_language
      };

      // Add service provider specific fields
      if (formData.user_type === 'service_provider') {
        registrationData.national_id = formData.national_id;
        registrationData.date_of_birth = formData.date_of_birth;
      }

      const response = await register(registrationData);
      
      // Redirect based on user type
      const redirectPath = {
        customer: '/dashboard',
        service_provider: '/provider-dashboard',
        admin: '/admin-dashboard'
      }[response.user.user_type] || '/dashboard';
      
      navigate(redirectPath);
    } catch (err) {
      setError(err.message || 'حدث خطأ أثناء إنشاء الحساب');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="w-full max-w-2xl">
        {/* Header */}
        <div className="text-center mb-8">
          <Link to="/" className="inline-block">
            <h1 className="text-3xl font-bold text-blue-600 mb-2">منصة الصيانة</h1>
          </Link>
          <p className="text-gray-600">إنشاء حساب جديد</p>
        </div>

        <Card className="shadow-lg">
          <CardHeader className="space-y-1">
            <CardTitle className="text-2xl text-center">إنشاء حساب</CardTitle>
            <CardDescription className="text-center">
              اختر نوع الحساب وأدخل بياناتك
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              {error && (
                <Alert variant="destructive">
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}

              {/* User Type Selection */}
              <div className="space-y-3">
                <Label>نوع الحساب</Label>
                <div className="grid grid-cols-2 gap-4">
                  <div 
                    className={`p-4 border-2 rounded-lg cursor-pointer transition-all ${
                      userType === 'customer' 
                        ? 'border-blue-500 bg-blue-50' 
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                    onClick={() => handleUserTypeChange('customer')}
                  >
                    <div className="flex items-center space-x-3 space-x-reverse">
                      <User className="h-6 w-6 text-blue-600" />
                      <div>
                        <h3 className="font-medium">عميل</h3>
                        <p className="text-sm text-gray-500">أطلب خدمات الصيانة</p>
                      </div>
                    </div>
                  </div>
                  
                  <div 
                    className={`p-4 border-2 rounded-lg cursor-pointer transition-all ${
                      userType === 'service_provider' 
                        ? 'border-blue-500 bg-blue-50' 
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                    onClick={() => handleUserTypeChange('service_provider')}
                  >
                    <div className="flex items-center space-x-3 space-x-reverse">
                      <Wrench className="h-6 w-6 text-blue-600" />
                      <div>
                        <h3 className="font-medium">مقدم خدمة</h3>
                        <p className="text-sm text-gray-500">قدم خدمات الصيانة</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Personal Information */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="first_name">الاسم الأول *</Label>
                  <Input
                    id="first_name"
                    name="first_name"
                    type="text"
                    placeholder="أحمد"
                    value={formData.first_name}
                    onChange={handleChange}
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="last_name">الاسم الأخير *</Label>
                  <Input
                    id="last_name"
                    name="last_name"
                    type="text"
                    placeholder="محمد"
                    value={formData.last_name}
                    onChange={handleChange}
                    required
                  />
                </div>
              </div>

              {/* Contact Information */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="email">البريد الإلكتروني *</Label>
                  <Input
                    id="email"
                    name="email"
                    type="email"
                    placeholder="example@email.com"
                    value={formData.email}
                    onChange={handleChange}
                    required
                    dir="ltr"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="phone">رقم الهاتف *</Label>
                  <Input
                    id="phone"
                    name="phone"
                    type="tel"
                    placeholder="01123456789"
                    value={formData.phone}
                    onChange={handleChange}
                    required
                    dir="ltr"
                  />
                </div>
              </div>

              {/* Service Provider Specific Fields */}
              {userType === 'service_provider' && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="national_id">الرقم القومي *</Label>
                    <Input
                      id="national_id"
                      name="national_id"
                      type="text"
                      placeholder="12345678901234"
                      value={formData.national_id}
                      onChange={handleChange}
                      maxLength={14}
                      dir="ltr"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="date_of_birth">تاريخ الميلاد *</Label>
                    <Input
                      id="date_of_birth"
                      name="date_of_birth"
                      type="date"
                      value={formData.date_of_birth}
                      onChange={handleChange}
                    />
                  </div>
                </div>
              )}

              {/* Password Fields */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="password">كلمة المرور *</Label>
                  <div className="relative">
                    <Input
                      id="password"
                      name="password"
                      type={showPassword ? 'text' : 'password'}
                      placeholder="8 أحرف على الأقل"
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

                <div className="space-y-2">
                  <Label htmlFor="confirmPassword">تأكيد كلمة المرور *</Label>
                  <div className="relative">
                    <Input
                      id="confirmPassword"
                      name="confirmPassword"
                      type={showConfirmPassword ? 'text' : 'password'}
                      placeholder="أعد إدخال كلمة المرور"
                      value={formData.confirmPassword}
                      onChange={handleChange}
                      required
                      className="pr-10"
                    />
                    <button
                      type="button"
                      className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                      onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                    >
                      {showConfirmPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </button>
                  </div>
                </div>
              </div>

              {/* Terms and Conditions */}
              <div className="flex items-center space-x-2 space-x-reverse">
                <Checkbox
                  id="acceptTerms"
                  name="acceptTerms"
                  checked={formData.acceptTerms}
                  onCheckedChange={(checked) => 
                    setFormData({ ...formData, acceptTerms: checked })
                  }
                />
                <Label htmlFor="acceptTerms" className="text-sm">
                  أوافق على{' '}
                  <Link to="/terms" className="text-blue-600 hover:text-blue-500">
                    الشروط والأحكام
                  </Link>
                  {' '}و{' '}
                  <Link to="/privacy" className="text-blue-600 hover:text-blue-500">
                    سياسة الخصوصية
                  </Link>
                </Label>
              </div>

              <Button 
                type="submit" 
                className="w-full" 
                disabled={loading}
              >
                {loading ? (
                  <>
                    <Loader2 className="ml-2 h-4 w-4 animate-spin" />
                    جاري إنشاء الحساب...
                  </>
                ) : (
                  <>
                    إنشاء حساب
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
                  لديك حساب بالفعل؟{' '}
                  <Link 
                    to="/login" 
                    className="font-medium text-blue-600 hover:text-blue-500"
                  >
                    تسجيل الدخول
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

export default RegisterPage;

