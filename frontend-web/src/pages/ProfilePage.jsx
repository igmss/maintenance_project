import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  ArrowLeft,
  User,
  Mail,
  Phone,
  MapPin,
  Camera,
  Save,
  Lock,
  Eye,
  EyeOff,
  Loader2,
  CheckCircle
} from 'lucide-react';
import { useAuth } from '../lib/auth.jsx';
import { 
  isValidEmail, 
  isValidEgyptianPhone, 
  getInitials 
} from '../lib/utils';

const ProfilePage = () => {
  const { user, updateProfile } = useAuth();
  const navigate = useNavigate();
  
  const [profileData, setProfileData] = useState({
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    bio: '',
    address: '',
    city: '',
    governorate: ''
  });
  
  const [passwordData, setPasswordData] = useState({
    current_password: '',
    new_password: '',
    confirm_password: ''
  });
  
  const [showPasswords, setShowPasswords] = useState({
    current: false,
    new: false,
    confirm: false
  });
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    if (user) {
      setProfileData({
        first_name: user.profile?.first_name || '',
        last_name: user.profile?.last_name || '',
        email: user.email || '',
        phone: user.phone || '',
        bio: user.profile?.bio || '',
        address: user.profile?.address || '',
        city: user.profile?.city || '',
        governorate: user.profile?.governorate || ''
      });
    }
  }, [user]);

  const handleProfileChange = (e) => {
    setProfileData({
      ...profileData,
      [e.target.name]: e.target.value
    });
    // Clear messages when user starts typing
    if (error) setError('');
    if (success) setSuccess('');
  };

  const handlePasswordChange = (e) => {
    setPasswordData({
      ...passwordData,
      [e.target.name]: e.target.value
    });
    // Clear messages when user starts typing
    if (error) setError('');
    if (success) setSuccess('');
  };

  const togglePasswordVisibility = (field) => {
    setShowPasswords({
      ...showPasswords,
      [field]: !showPasswords[field]
    });
  };

  const validateProfileForm = () => {
    if (!profileData.first_name || !profileData.last_name) {
      throw new Error('الاسم الأول والأخير مطلوبان');
    }

    if (!isValidEmail(profileData.email)) {
      throw new Error('يرجى إدخال بريد إلكتروني صحيح');
    }

    if (!isValidEgyptianPhone(profileData.phone)) {
      throw new Error('يرجى إدخال رقم هاتف مصري صحيح');
    }
  };

  const validatePasswordForm = () => {
    if (!passwordData.current_password || !passwordData.new_password || !passwordData.confirm_password) {
      throw new Error('يرجى ملء جميع حقول كلمة المرور');
    }

    if (passwordData.new_password.length < 8) {
      throw new Error('كلمة المرور الجديدة يجب أن تكون 8 أحرف على الأقل');
    }

    if (passwordData.new_password !== passwordData.confirm_password) {
      throw new Error('كلمة المرور الجديدة وتأكيدها غير متطابقتين');
    }
  };

  const handleProfileSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      validateProfileForm();
      
      await updateProfile(profileData);
      setSuccess('تم تحديث الملف الشخصي بنجاح');
    } catch (err) {
      setError(err.message || 'حدث خطأ أثناء تحديث الملف الشخصي');
    } finally {
      setLoading(false);
    }
  };

  const handlePasswordSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      validatePasswordForm();
      
      // This would call a change password API endpoint
      // await apiClient.changePassword(passwordData);
      
      setSuccess('تم تغيير كلمة المرور بنجاح');
      setPasswordData({
        current_password: '',
        new_password: '',
        confirm_password: ''
      });
    } catch (err) {
      setError(err.message || 'حدث خطأ أثناء تغيير كلمة المرور');
    } finally {
      setLoading(false);
    }
  };

  const egyptianGovernorates = [
    'القاهرة', 'الجيزة', 'الإسكندرية', 'الدقهلية', 'البحر الأحمر', 'البحيرة',
    'الفيوم', 'الغربية', 'الإسماعيلية', 'المنوفية', 'المنيا', 'القليوبية',
    'الوادي الجديد', 'السويس', 'أسوان', 'أسيوط', 'بني سويف', 'بورسعيد',
    'دمياط', 'الشرقية', 'جنوب سيناء', 'كفر الشيخ', 'مطروح', 'الأقصر',
    'قنا', 'شمال سيناء', 'سوهاج'
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center h-16">
            <Button 
              variant="ghost" 
              onClick={() => navigate('/dashboard')}
              className="mr-4"
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              العودة
            </Button>
            <h1 className="text-xl font-semibold text-gray-900">الملف الشخصي</h1>
          </div>
        </div>
      </header>

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Profile Header */}
        <Card className="mb-8">
          <CardContent className="pt-6">
            <div className="flex items-center space-x-6 space-x-reverse">
              <div className="relative">
                <Avatar className="h-24 w-24">
                  <AvatarImage src={user?.profile?.profile_image_url} />
                  <AvatarFallback className="text-2xl">
                    {getInitials(user?.profile?.full_name || user?.email)}
                  </AvatarFallback>
                </Avatar>
                <Button
                  size="sm"
                  className="absolute -bottom-2 -right-2 rounded-full h-8 w-8 p-0"
                  variant="secondary"
                >
                  <Camera className="h-4 w-4" />
                </Button>
              </div>
              <div>
                <h2 className="text-2xl font-bold text-gray-900">
                  {user?.profile?.full_name || 'المستخدم'}
                </h2>
                <p className="text-gray-600">{user?.email}</p>
                <p className="text-sm text-gray-500">
                  {user?.user_type === 'customer' ? 'عميل' : 
                   user?.user_type === 'service_provider' ? 'مقدم خدمة' : 'مدير'}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Messages */}
        {error && (
          <Alert variant="destructive" className="mb-6">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {success && (
          <Alert className="mb-6 border-green-200 bg-green-50">
            <CheckCircle className="h-4 w-4 text-green-600" />
            <AlertDescription className="text-green-800">{success}</AlertDescription>
          </Alert>
        )}

        {/* Profile Tabs */}
        <Tabs defaultValue="profile" className="space-y-4">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="profile">المعلومات الشخصية</TabsTrigger>
            <TabsTrigger value="security">الأمان</TabsTrigger>
          </TabsList>
          
          <TabsContent value="profile">
            <Card>
              <CardHeader>
                <CardTitle>المعلومات الشخصية</CardTitle>
                <CardDescription>
                  قم بتحديث معلوماتك الشخصية ومعلومات الاتصال
                </CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleProfileSubmit} className="space-y-6">
                  {/* Name Fields */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="first_name">الاسم الأول *</Label>
                      <Input
                        id="first_name"
                        name="first_name"
                        value={profileData.first_name}
                        onChange={handleProfileChange}
                        required
                      />
                    </div>
                    <div>
                      <Label htmlFor="last_name">الاسم الأخير *</Label>
                      <Input
                        id="last_name"
                        name="last_name"
                        value={profileData.last_name}
                        onChange={handleProfileChange}
                        required
                      />
                    </div>
                  </div>

                  {/* Contact Information */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="email">البريد الإلكتروني *</Label>
                      <div className="relative">
                        <Mail className="absolute right-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                        <Input
                          id="email"
                          name="email"
                          type="email"
                          value={profileData.email}
                          onChange={handleProfileChange}
                          className="pr-10"
                          required
                          dir="ltr"
                        />
                      </div>
                    </div>
                    <div>
                      <Label htmlFor="phone">رقم الهاتف *</Label>
                      <div className="relative">
                        <Phone className="absolute right-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                        <Input
                          id="phone"
                          name="phone"
                          type="tel"
                          value={profileData.phone}
                          onChange={handleProfileChange}
                          className="pr-10"
                          required
                          dir="ltr"
                        />
                      </div>
                    </div>
                  </div>

                  {/* Bio */}
                  <div>
                    <Label htmlFor="bio">نبذة شخصية</Label>
                    <Textarea
                      id="bio"
                      name="bio"
                      value={profileData.bio}
                      onChange={handleProfileChange}
                      placeholder="اكتب نبذة مختصرة عنك..."
                      rows={3}
                    />
                  </div>

                  {/* Location Information */}
                  <div className="space-y-4">
                    <h3 className="text-lg font-medium text-gray-900">معلومات الموقع</h3>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <Label htmlFor="governorate">المحافظة</Label>
                        <select
                          id="governorate"
                          name="governorate"
                          value={profileData.governorate}
                          onChange={handleProfileChange}
                          className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                        >
                          <option value="">اختر المحافظة</option>
                          {egyptianGovernorates.map((gov) => (
                            <option key={gov} value={gov}>{gov}</option>
                          ))}
                        </select>
                      </div>
                      <div>
                        <Label htmlFor="city">المدينة</Label>
                        <Input
                          id="city"
                          name="city"
                          value={profileData.city}
                          onChange={handleProfileChange}
                          placeholder="اسم المدينة"
                        />
                      </div>
                    </div>

                    <div>
                      <Label htmlFor="address">العنوان التفصيلي</Label>
                      <div className="relative">
                        <MapPin className="absolute right-3 top-3 h-4 w-4 text-gray-400" />
                        <Textarea
                          id="address"
                          name="address"
                          value={profileData.address}
                          onChange={handleProfileChange}
                          placeholder="الشارع، الحي، أقرب معلم..."
                          className="pr-10"
                          rows={2}
                        />
                      </div>
                    </div>
                  </div>

                  <div className="flex justify-end">
                    <Button type="submit" disabled={loading}>
                      {loading ? (
                        <>
                          <Loader2 className="ml-2 h-4 w-4 animate-spin" />
                          جاري الحفظ...
                        </>
                      ) : (
                        <>
                          <Save className="ml-2 h-4 w-4" />
                          حفظ التغييرات
                        </>
                      )}
                    </Button>
                  </div>
                </form>
              </CardContent>
            </Card>
          </TabsContent>
          
          <TabsContent value="security">
            <Card>
              <CardHeader>
                <CardTitle>الأمان</CardTitle>
                <CardDescription>
                  قم بتغيير كلمة المرور وإدارة إعدادات الأمان
                </CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={handlePasswordSubmit} className="space-y-6">
                  <div>
                    <Label htmlFor="current_password">كلمة المرور الحالية *</Label>
                    <div className="relative">
                      <Lock className="absolute right-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                      <Input
                        id="current_password"
                        name="current_password"
                        type={showPasswords.current ? 'text' : 'password'}
                        value={passwordData.current_password}
                        onChange={handlePasswordChange}
                        className="pr-10 pl-10"
                        required
                      />
                      <button
                        type="button"
                        className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                        onClick={() => togglePasswordVisibility('current')}
                      >
                        {showPasswords.current ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                      </button>
                    </div>
                  </div>

                  <div>
                    <Label htmlFor="new_password">كلمة المرور الجديدة *</Label>
                    <div className="relative">
                      <Lock className="absolute right-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                      <Input
                        id="new_password"
                        name="new_password"
                        type={showPasswords.new ? 'text' : 'password'}
                        value={passwordData.new_password}
                        onChange={handlePasswordChange}
                        className="pr-10 pl-10"
                        placeholder="8 أحرف على الأقل"
                        required
                      />
                      <button
                        type="button"
                        className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                        onClick={() => togglePasswordVisibility('new')}
                      >
                        {showPasswords.new ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                      </button>
                    </div>
                  </div>

                  <div>
                    <Label htmlFor="confirm_password">تأكيد كلمة المرور الجديدة *</Label>
                    <div className="relative">
                      <Lock className="absolute right-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                      <Input
                        id="confirm_password"
                        name="confirm_password"
                        type={showPasswords.confirm ? 'text' : 'password'}
                        value={passwordData.confirm_password}
                        onChange={handlePasswordChange}
                        className="pr-10 pl-10"
                        placeholder="أعد إدخال كلمة المرور الجديدة"
                        required
                      />
                      <button
                        type="button"
                        className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                        onClick={() => togglePasswordVisibility('confirm')}
                      >
                        {showPasswords.confirm ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                      </button>
                    </div>
                  </div>

                  <div className="flex justify-end">
                    <Button type="submit" disabled={loading}>
                      {loading ? (
                        <>
                          <Loader2 className="ml-2 h-4 w-4 animate-spin" />
                          جاري التحديث...
                        </>
                      ) : (
                        <>
                          <Lock className="ml-2 h-4 w-4" />
                          تغيير كلمة المرور
                        </>
                      )}
                    </Button>
                  </div>
                </form>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default ProfilePage;

