import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { 
  Users,
  DollarSign,
  Calendar,
  TrendingUp,
  UserCheck,
  UserX,
  Clock,
  Star,
  AlertCircle,
  CheckCircle,
  User,
  LogOut,
  Settings,
  Bell,
  Shield,
  BarChart3,
  FileText,
  Wrench
} from 'lucide-react';
import { useAuth } from '../lib/auth.jsx';
import { apiClient } from '../lib/api';
import { 
  formatCurrency, 
  formatDate, 
  getBookingStatusColor, 
  getBookingStatusText,
  getInitials 
} from '../lib/utils';

// Verification Queue Component
const VerificationQueue = () => {
  const [verificationQueue, setVerificationQueue] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedProvider, setSelectedProvider] = useState(null);
  const [viewingDocuments, setViewingDocuments] = useState(false);

  useEffect(() => {
    loadVerificationQueue();
  }, []);

  const loadVerificationQueue = async () => {
    try {
      const response = await apiClient.getVerificationQueue({ per_page: 50 });
      setVerificationQueue(response.providers || []);
    } catch (error) {
      console.error('Failed to load verification queue:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleVerification = async (providerId, action, reason = null) => {
    try {
      await apiClient.verifyProvider(providerId, action, reason);
      alert(`تم ${action === 'approve' ? 'قبول' : 'رفض'} مقدم الخدمة بنجاح`);
      await loadVerificationQueue();
      setSelectedProvider(null);
      setViewingDocuments(false);
    } catch (error) {
      console.error('Failed to verify provider:', error);
      alert('حدث خطأ أثناء عملية التحقق');
    }
  };

  const getDocumentStatusBadge = (status) => {
    const configs = {
      pending: { color: 'bg-yellow-100 text-yellow-800', text: 'قيد المراجعة' },
      approved: { color: 'bg-green-100 text-green-800', text: 'معتمدة' },
      rejected: { color: 'bg-red-100 text-red-800', text: 'مرفوضة' }
    };
    const config = configs[status] || configs.pending;
    return <Badge className={config.color}>{config.text}</Badge>;
  };

  const getDocumentTypeText = (type) => {
    const types = {
      national_id: 'البطاقة الشخصية',
      certificate: 'شهادة مهنية',
      license: 'رخصة مزاولة المهنة',
      insurance: 'بوليصة التأمين',
      background_check: 'فحص السجل الجنائي'
    };
    return types[type] || type;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (viewingDocuments && selectedProvider) {
    return (
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>مراجعة وثائق مقدم الخدمة</CardTitle>
              <CardDescription>
                {selectedProvider.business_name} - {selectedProvider.first_name} {selectedProvider.last_name}
              </CardDescription>
            </div>
            <Button variant="outline" onClick={() => setViewingDocuments(false)}>
              العودة للقائمة
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            {selectedProvider.documents?.length === 0 ? (
              <p className="text-center text-gray-500 py-8">لم يتم رفع أي وثائق بعد</p>
            ) : (
              selectedProvider.documents?.map((document) => (
                <div key={document.id} className="border rounded-lg p-4">
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <h4 className="font-medium">{getDocumentTypeText(document.document_type)}</h4>
                      <p className="text-sm text-gray-500">
                        تم الرفع في {new Date(document.created_at).toLocaleDateString('ar-EG')}
                      </p>
                    </div>
                    {getDocumentStatusBadge(document.verification_status)}
                  </div>

                  <div className="mb-4">
                    <img 
                      src={document.document_url.startsWith('/') 
                        ? `https://maintenance-platform-backend.onrender.com${document.document_url}` 
                        : document.document_url
                      } 
                      alt={getDocumentTypeText(document.document_type)}
                      className="max-w-full h-64 object-contain border rounded"
                      onError={(e) => {
                        e.target.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZGRkIi8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIxNCIgZmlsbD0iIzk5OSIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPkltYWdlIG5vdCBhdmFpbGFibGU8L3RleHQ+PC9zdmc+';
                      }}
                    />
                  </div>

                  {document.rejection_reason && (
                    <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded">
                      <p className="text-sm text-red-800">
                        <strong>سبب الرفض:</strong> {document.rejection_reason}
                      </p>
                    </div>
                  )}
                </div>
              ))
            )}

            <div className="flex justify-center space-x-4 space-x-reverse pt-6 border-t">
              <Button
                onClick={() => handleVerification(selectedProvider.id, 'approve')}
                className="bg-green-600 hover:bg-green-700"
              >
                <CheckCircle className="mr-2 h-4 w-4" />
                اعتماد مقدم الخدمة
              </Button>
              <Button
                variant="outline"
                onClick={() => {
                  const reason = prompt('سبب الرفض:');
                  if (reason) {
                    handleVerification(selectedProvider.id, 'reject', reason);
                  }
                }}
                className="border-red-300 text-red-700 hover:bg-red-50"
              >
                <AlertCircle className="mr-2 h-4 w-4" />
                رفض التحقق
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center">
          <Shield className="mr-2 h-5 w-5" />
          طوابير التحقق من الهوية
        </CardTitle>
        <CardDescription>
          مقدمو الخدمة بانتظار مراجعة وثائقهم ({verificationQueue.length} في الانتظار)
        </CardDescription>
      </CardHeader>
      <CardContent>
        {verificationQueue.length === 0 ? (
          <div className="text-center py-8">
            <CheckCircle className="mx-auto h-12 w-12 text-green-600 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">لا توجد طلبات تحقق</h3>
            <p className="text-gray-500">جميع مقدمي الخدمة تم التحقق منهم</p>
          </div>
        ) : (
          <div className="space-y-4">
            {verificationQueue.map((provider) => (
              <div key={provider.id} className="border rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4 space-x-reverse">
                    <Avatar className="h-12 w-12">
                      <AvatarImage src={provider.profile_image_url} />
                      <AvatarFallback>
                        {getInitials(`${provider.first_name} ${provider.last_name}`)}
                      </AvatarFallback>
                    </Avatar>
                    
                    <div>
                      <h3 className="font-medium">{provider.business_name}</h3>
                      <p className="text-sm text-gray-600">
                        {provider.first_name} {provider.last_name}
                      </p>
                      <div className="flex items-center space-x-4 space-x-reverse mt-1 text-xs text-gray-500">
                        <span>تاريخ التسجيل: {formatDate(provider.created_at)}</span>
                        <span>الوثائق: {provider.documents?.length || 0}</span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2 space-x-reverse">
                    <Badge variant="secondary">
                      {provider.documents?.length || 0} وثيقة
                    </Badge>
                    <Button
                      onClick={() => {
                        setSelectedProvider(provider);
                        setViewingDocuments(true);
                      }}
                    >
                      <FileText className="mr-2 h-4 w-4" />
                      مراجعة الوثائق
                    </Button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

const AdminDashboard = () => {
  const { user, logout } = useAuth();
  const [stats, setStats] = useState(null);
  const [recentUsers, setRecentUsers] = useState([]);
  const [recentBookings, setRecentBookings] = useState([]);
  const [revenueAnalytics, setRevenueAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      const [statsResponse, usersResponse, bookingsResponse, revenueResponse] = await Promise.all([
        apiClient.getDashboardStats(),
        apiClient.getUsers({ per_page: 10 }),
        apiClient.getAllBookings({ per_page: 10 }),
        apiClient.getRevenueAnalytics(30)
      ]);

      setStats(statsResponse);
      setRecentUsers(usersResponse.users || []);
      setRecentBookings(bookingsResponse.bookings || []);
      setRevenueAnalytics(revenueResponse);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    await logout();
  };

  const getUserTypeColor = (userType) => {
    switch (userType) {
      case 'customer':
        return 'bg-blue-100 text-blue-800';
      case 'service_provider':
        return 'bg-green-100 text-green-800';
      case 'admin':
        return 'bg-purple-100 text-purple-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getUserTypeText = (userType) => {
    switch (userType) {
      case 'customer':
        return 'عميل';
      case 'service_provider':
        return 'مقدم خدمة';
      case 'admin':
        return 'مدير';
      default:
        return userType;
    }
  };

  const getUserStatusColor = (status) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800';
      case 'inactive':
        return 'bg-gray-100 text-gray-800';
      case 'suspended':
        return 'bg-red-100 text-red-800';
      case 'pending_verification':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getUserStatusText = (status) => {
    switch (status) {
      case 'active':
        return 'نشط';
      case 'inactive':
        return 'غير نشط';
      case 'suspended':
        return 'موقوف';
      case 'pending_verification':
        return 'في انتظار التحقق';
      default:
        return status;
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-blue-600">منصة الصيانة</h1>
              <Badge className="mr-3 bg-purple-100 text-purple-800">
                <Shield className="h-3 w-3 mr-1" />
                لوحة الإدارة
              </Badge>
            </div>
            
            <div className="flex items-center space-x-4 space-x-reverse">
              <Button variant="ghost" size="sm">
                <Bell className="h-4 w-4" />
              </Button>
              
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" className="relative h-8 w-8 rounded-full">
                    <Avatar className="h-8 w-8">
                      <AvatarImage src={user?.profile?.profile_image_url} />
                      <AvatarFallback>
                        {getInitials(user?.profile?.full_name || user?.email)}
                      </AvatarFallback>
                    </Avatar>
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent className="w-56" align="end" forceMount>
                  <DropdownMenuLabel className="font-normal">
                    <div className="flex flex-col space-y-1">
                      <p className="text-sm font-medium leading-none">
                        {user?.profile?.full_name || 'المدير'}
                      </p>
                      <p className="text-xs leading-none text-muted-foreground">
                        {user?.email}
                      </p>
                    </div>
                  </DropdownMenuLabel>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem>
                    <User className="mr-2 h-4 w-4" />
                    <span>الملف الشخصي</span>
                  </DropdownMenuItem>
                  <DropdownMenuItem>
                    <Settings className="mr-2 h-4 w-4" />
                    <span>إعدادات النظام</span>
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem onClick={handleLogout}>
                    <LogOut className="mr-2 h-4 w-4" />
                    <span>تسجيل الخروج</span>
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome Section */}
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-2">
            لوحة التحكم الإدارية
          </h2>
          <p className="text-gray-600">إدارة ومراقبة منصة الصيانة</p>
        </div>

        {/* Main Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">إجمالي المستخدمين</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats?.users?.total || 0}</div>
              <p className="text-xs text-muted-foreground">
                +{stats?.users?.new_this_week || 0} هذا الأسبوع
              </p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">إجمالي الحجوزات</CardTitle>
              <Calendar className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats?.bookings?.total || 0}</div>
              <p className="text-xs text-muted-foreground">
                {stats?.bookings?.this_month || 0} هذا الشهر
              </p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">إيرادات المنصة</CardTitle>
              <DollarSign className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {formatCurrency(stats?.revenue?.platform_revenue || 0)}
              </div>
              <p className="text-xs text-muted-foreground">
                {formatCurrency(stats?.revenue?.monthly_revenue || 0)} هذا الشهر
              </p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">متوسط التقييم</CardTitle>
              <Star className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {stats?.services?.average_rating || 0}
                <span className="text-sm font-normal text-gray-500 mr-1">/ 5</span>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Provider Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">مقدمو الخدمة</CardTitle>
              <UserCheck className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats?.providers?.total || 0}</div>
              <div className="flex items-center text-xs text-muted-foreground space-x-4 space-x-reverse mt-2">
                <div className="flex items-center">
                  <CheckCircle className="h-3 w-3 text-green-600 mr-1" />
                  <span>{stats?.providers?.verified || 0} معتمد</span>
                </div>
                <div className="flex items-center">
                  <Clock className="h-3 w-3 text-yellow-600 mr-1" />
                  <span>{stats?.providers?.pending_verification || 0} في الانتظار</span>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">معدل الإكمال</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {stats?.bookings?.completion_rate || 0}%
              </div>
              <p className="text-xs text-muted-foreground">
                {stats?.bookings?.completed || 0} من {stats?.bookings?.total || 0} حجز
              </p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">الخدمات النشطة</CardTitle>
              <Wrench className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats?.services?.total_services || 0}</div>
              <p className="text-xs text-muted-foreground">
                {stats?.services?.total_categories || 0} فئة خدمة
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Tabs for detailed views */}
        <Tabs defaultValue="users" className="space-y-4">
                      <TabsList className="grid w-full grid-cols-5">
              <TabsTrigger value="users">المستخدمون</TabsTrigger>
              <TabsTrigger value="bookings">الحجوزات</TabsTrigger>
              <TabsTrigger value="providers">مقدمو الخدمة</TabsTrigger>
              <TabsTrigger value="verification">التحقق من الهوية</TabsTrigger>
              <TabsTrigger value="analytics">التحليلات</TabsTrigger>
            </TabsList>
          
          <TabsContent value="users" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>المستخدمون الجدد</CardTitle>
                <CardDescription>آخر المستخدمين المسجلين في المنصة</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {recentUsers.map((user) => (
                    <div key={user.id} className="flex items-center justify-between p-4 border rounded-lg">
                      <div className="flex items-center space-x-4 space-x-reverse">
                        <Avatar className="h-10 w-10">
                          <AvatarImage src={user.profile?.profile_image_url} />
                          <AvatarFallback>
                            {getInitials(user.profile?.full_name || user.email)}
                          </AvatarFallback>
                        </Avatar>
                        <div>
                          <p className="font-medium text-gray-900">
                            {user.profile?.full_name || 'مستخدم جديد'}
                          </p>
                          <p className="text-sm text-gray-500">{user.email}</p>
                          <p className="text-xs text-gray-400">
                            انضم في {formatDate(user.created_at)}
                          </p>
                        </div>
                      </div>
                      <div className="flex flex-col items-end space-y-2">
                        <Badge className={getUserTypeColor(user.user_type)}>
                          {getUserTypeText(user.user_type)}
                        </Badge>
                        <Badge variant="secondary" className={getUserStatusColor(user.status)}>
                          {getUserStatusText(user.status)}
                        </Badge>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
          
          <TabsContent value="bookings" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>الحجوزات الأخيرة</CardTitle>
                <CardDescription>آخر الحجوزات في المنصة</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {recentBookings.map((booking) => (
                    <div key={booking.id} className="flex items-center justify-between p-4 border rounded-lg">
                      <div className="flex-1">
                        <p className="font-medium text-gray-900">
                          {booking.service?.name || 'خدمة'}
                        </p>
                        <p className="text-sm text-gray-500">
                          العميل: {booking.customer?.full_name || 'غير محدد'}
                        </p>
                        <p className="text-sm text-gray-500">
                          مقدم الخدمة: {booking.provider?.full_name || 'غير محدد'}
                        </p>
                        <p className="text-xs text-gray-400">
                          {formatDate(booking.created_at)}
                        </p>
                      </div>
                      <div className="flex flex-col items-end space-y-2">
                        <Badge 
                          variant="secondary" 
                          className={getBookingStatusColor(booking.booking_status)}
                        >
                          {getBookingStatusText(booking.booking_status)}
                        </Badge>
                        <span className="text-sm font-medium">
                          {formatCurrency(booking.total_amount)}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
          
          <TabsContent value="providers" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>مقدمو الخدمة في انتظار التحقق</CardTitle>
                <CardDescription>مقدمو الخدمة الذين يحتاجون موافقة إدارية</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {recentUsers
                    .filter(user => user.user_type === 'service_provider' && user.status === 'pending_verification')
                    .map((provider) => (
                    <div key={provider.id} className="flex items-center justify-between p-4 border rounded-lg">
                      <div className="flex items-center space-x-4 space-x-reverse">
                        <Avatar className="h-10 w-10">
                          <AvatarImage src={provider.profile?.profile_image_url} />
                          <AvatarFallback>
                            {getInitials(provider.profile?.full_name || provider.email)}
                          </AvatarFallback>
                        </Avatar>
                        <div>
                          <p className="font-medium text-gray-900">
                            {provider.profile?.full_name || 'مقدم خدمة'}
                          </p>
                          <p className="text-sm text-gray-500">{provider.email}</p>
                          <p className="text-xs text-gray-400">
                            طلب التحقق في {formatDate(provider.created_at)}
                          </p>
                        </div>
                      </div>
                      <div className="flex space-x-2 space-x-reverse">
                        <Button size="sm" variant="outline">
                          <FileText className="h-4 w-4 mr-1" />
                          مراجعة الوثائق
                        </Button>
                        <Button size="sm">
                          <CheckCircle className="h-4 w-4 mr-1" />
                          موافقة
                        </Button>
                      </div>
                    </div>
                  ))}
                  
                  {recentUsers.filter(user => user.user_type === 'service_provider' && user.status === 'pending_verification').length === 0 && (
                    <div className="text-center py-8">
                      <p className="text-gray-500">لا توجد طلبات تحقق في الانتظار</p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="verification" className="space-y-4">
            <VerificationQueue />
          </TabsContent>
          
          <TabsContent value="analytics" className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>الإيرادات حسب الفئة</CardTitle>
                  <CardDescription>توزيع الإيرادات على فئات الخدمات</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {revenueAnalytics?.category_revenue?.map((category, index) => (
                      <div key={index} className="flex items-center justify-between">
                        <span className="text-sm text-gray-600">{category.category}</span>
                        <div className="flex items-center space-x-2 space-x-reverse">
                          <span className="text-sm font-medium">
                            {formatCurrency(category.revenue)}
                          </span>
                          <span className="text-xs text-gray-500">
                            ({category.bookings} حجز)
                          </span>
                        </div>
                      </div>
                    )) || (
                      <p className="text-gray-500 text-center py-4">لا توجد بيانات متاحة</p>
                    )}
                  </div>
                </CardContent>
              </Card>
              
              <Card>
                <CardHeader>
                  <CardTitle>أفضل مقدمي الخدمة</CardTitle>
                  <CardDescription>مقدمو الخدمة الأكثر نشاطاً</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {revenueAnalytics?.top_providers?.map((provider, index) => (
                      <div key={index} className="flex items-center justify-between">
                        <div className="flex items-center space-x-2 space-x-reverse">
                          <span className="text-sm font-medium">#{index + 1}</span>
                          <span className="text-sm text-gray-600">{provider.name}</span>
                        </div>
                        <div className="flex items-center space-x-2 space-x-reverse">
                          <span className="text-sm font-medium">
                            {formatCurrency(provider.earnings)}
                          </span>
                          <div className="flex items-center">
                            <Star className="h-3 w-3 text-yellow-400 mr-1" />
                            <span className="text-xs text-gray-500">
                              {provider.avg_rating}
                            </span>
                          </div>
                        </div>
                      </div>
                    )) || (
                      <p className="text-gray-500 text-center py-4">لا توجد بيانات متاحة</p>
                    )}
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default AdminDashboard;

