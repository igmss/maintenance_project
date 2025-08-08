import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Switch } from '@/components/ui/switch';
import { 
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { 
  Calendar,
  Clock,
  MapPin,
  Star,
  DollarSign,
  User,
  LogOut,
  Settings,
  Bell,
  CheckCircle,
  AlertCircle,
  TrendingUp,
  Users,
  Briefcase,
  FileText
} from 'lucide-react';
import { useAuth } from '../lib/auth.jsx';
import { apiClient } from '../lib/api';
import { 
  formatCurrency, 
  formatDate, 
  formatTime, 
  getBookingStatusColor, 
  getBookingStatusText,
  getInitials 
} from '../lib/utils';

const ProviderDashboard = () => {
  const { user, logout } = useAuth();
  const [profile, setProfile] = useState(null);
  const [bookings, setBookings] = useState([]);
  const [isAvailable, setIsAvailable] = useState(true);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    totalBookings: 0,
    completedBookings: 0,
    activeBookings: 0,
    totalEarnings: 0,
    averageRating: 0,
    completionRate: 0
  });

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      const [profileResponse, bookingsResponse] = await Promise.all([
        apiClient.getProviderProfile(),
        apiClient.getBookings({ per_page: 10 })
      ]);

      setProfile(profileResponse.profile);
      setBookings(bookingsResponse.bookings || []);
      setIsAvailable(profileResponse.profile?.is_available || false);

      // Calculate stats
      const totalBookings = bookingsResponse.bookings?.length || 0;
      const completedBookings = bookingsResponse.bookings?.filter(b => b.booking_status === 'completed').length || 0;
      const activeBookings = bookingsResponse.bookings?.filter(b => 
        ['confirmed', 'in_progress'].includes(b.booking_status)
      ).length || 0;
      const totalEarnings = bookingsResponse.bookings?.reduce((sum, booking) => 
        booking.booking_status === 'completed' ? sum + parseFloat(booking.provider_earnings || 0) : sum, 0
      ) || 0;
      const averageRating = profileResponse.profile?.average_rating || 0;
      const completionRate = totalBookings > 0 ? (completedBookings / totalBookings * 100) : 0;

      setStats({
        totalBookings,
        completedBookings,
        activeBookings,
        totalEarnings,
        averageRating,
        completionRate
      });
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAvailabilityToggle = async (available) => {
    try {
      await apiClient.updateAvailability({ is_available: available });
      setIsAvailable(available);
    } catch (error) {
      console.error('Failed to update availability:', error);
    }
  };

  const handleLogout = async () => {
    await logout();
  };

  const getVerificationStatusColor = (status) => {
    switch (status) {
      case 'approved':
      case 'verified':
        return 'bg-green-100 text-green-800';
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      case 'rejected':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getVerificationStatusText = (status) => {
    switch (status) {
      case 'approved':
      case 'verified':
        return 'معتمد';
      case 'pending':
        return 'قيد المراجعة';
      case 'rejected':
        return 'مرفوض';
      default:
        return 'غير محدد';
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
              <Badge className="mr-3 bg-blue-100 text-blue-800">مقدم خدمة</Badge>
            </div>
            
            <div className="flex items-center space-x-4 space-x-reverse">
              {/* Availability Toggle */}
              <div className="flex items-center space-x-2 space-x-reverse">
                <span className="text-sm text-gray-600">متاح للعمل</span>
                <Switch
                  checked={isAvailable}
                  onCheckedChange={handleAvailabilityToggle}
                />
              </div>
              
              <Button variant="ghost" size="sm">
                <Bell className="h-4 w-4" />
              </Button>
              
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" className="relative h-8 w-8 rounded-full">
                    <Avatar className="h-8 w-8">
                      <AvatarImage src={profile?.profile_image_url} />
                      <AvatarFallback>
                        {getInitials(profile?.full_name || user?.email)}
                      </AvatarFallback>
                    </Avatar>
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent className="w-56" align="end" forceMount>
                  <DropdownMenuLabel className="font-normal">
                    <div className="flex flex-col space-y-1">
                      <p className="text-sm font-medium leading-none">
                        {profile?.full_name || 'مقدم الخدمة'}
                      </p>
                      <p className="text-xs leading-none text-muted-foreground">
                        {user?.email}
                      </p>
                    </div>
                  </DropdownMenuLabel>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem asChild>
                    <Link to="/profile">
                      <User className="mr-2 h-4 w-4" />
                      <span>الملف الشخصي</span>
                    </Link>
                  </DropdownMenuItem>
                  <DropdownMenuItem>
                    <Settings className="mr-2 h-4 w-4" />
                    <span>الإعدادات</span>
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
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-3xl font-bold text-gray-900 mb-2">
                مرحباً، {profile?.first_name || 'عزيزي المقدم'}
              </h2>
              <p className="text-gray-600">إدارة خدماتك وحجوزاتك</p>
            </div>
            
            {/* Verification Status */}
            <div className="text-right">
              <div className="flex items-center space-x-2 space-x-reverse mb-2">
                <Badge className={getVerificationStatusColor(profile?.verification_status)}>
                  {getVerificationStatusText(profile?.verification_status)}
                </Badge>
                {profile?.verification_status === 'approved' && (
                  <CheckCircle className="h-4 w-4 text-green-600" />
                )}
                {profile?.verification_status === 'pending' && (
                  <AlertCircle className="h-4 w-4 text-yellow-600" />
                )}
              </div>
              {profile?.verification_status !== 'approved' && (
                <Button variant="outline" size="sm" asChild>
                  <Link to="/verification">
                    <FileText className="mr-2 h-4 w-4" />
                    إكمال التحقق
                  </Link>
                </Button>
              )}
              {profile?.verification_status === 'approved' && (
                <p className="text-sm text-green-600 font-medium">
                  ✅ تم التحقق من حسابك بنجاح
                </p>
              )}
            </div>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">إجمالي الحجوزات</CardTitle>
              <Calendar className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.totalBookings}</div>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">الحجوزات النشطة</CardTitle>
              <Clock className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.activeBookings}</div>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">إجمالي الأرباح</CardTitle>
              <DollarSign className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{formatCurrency(stats.totalEarnings)}</div>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">متوسط التقييم</CardTitle>
              <Star className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {stats.averageRating.toFixed(1)}
                <span className="text-sm font-normal text-gray-500 mr-1">/ 5</span>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Additional Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">معدل إكمال الخدمات</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.completionRate.toFixed(1)}%</div>
              <p className="text-xs text-muted-foreground">
                {stats.completedBookings} من {stats.totalBookings} حجز
              </p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">الخدمات المقدمة</CardTitle>
              <Briefcase className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{profile?.services?.length || 0}</div>
              <p className="text-xs text-muted-foreground">
                خدمة نشطة
              </p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">مناطق الخدمة</CardTitle>
              <MapPin className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{profile?.service_areas?.length || 0}</div>
              <p className="text-xs text-muted-foreground">
                منطقة مغطاة
              </p>
            </CardContent>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Recent Bookings */}
          <div className="lg:col-span-2">
            <Card>
              <CardHeader>
                <CardTitle>الحجوزات الأخيرة</CardTitle>
                <CardDescription>آخر الحجوزات المطلوبة منك</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {bookings.length === 0 ? (
                    <div className="text-center py-8">
                      <p className="text-gray-500 mb-4">لا توجد حجوزات بعد</p>
                      <p className="text-sm text-gray-400">
                        تأكد من أن ملفك الشخصي مكتمل ومعتمد لتلقي الحجوزات
                      </p>
                    </div>
                  ) : (
                    bookings.slice(0, 5).map((booking) => (
                      <div key={booking.id} className="flex items-center justify-between p-4 border rounded-lg">
                        <div className="flex-1">
                          <div className="flex items-center space-x-4 space-x-reverse">
                            <div>
                              <p className="font-medium text-gray-900">
                                {booking.service?.name || 'خدمة'}
                              </p>
                              <p className="text-sm text-gray-500">
                                العميل: {booking.customer?.full_name || 'غير محدد'}
                              </p>
                              <div className="flex items-center text-xs text-gray-500 space-x-2 space-x-reverse mt-1">
                                <Calendar className="h-3 w-3" />
                                <span>{formatDate(booking.scheduled_date)}</span>
                                <Clock className="h-3 w-3" />
                                <span>{formatTime(booking.scheduled_date)}</span>
                              </div>
                            </div>
                          </div>
                        </div>
                        <div className="flex flex-col items-end space-y-2">
                          <Badge 
                            variant="secondary" 
                            className={getBookingStatusColor(booking.booking_status)}
                          >
                            {getBookingStatusText(booking.booking_status)}
                          </Badge>
                          <span className="text-sm font-medium text-green-600">
                            {formatCurrency(booking.provider_earnings || 0)}
                          </span>
                        </div>
                      </div>
                    ))
                  )}
                </div>
                
                {bookings.length > 0 && (
                  <div className="mt-6">
                    <Button variant="outline" className="w-full" asChild>
                      <Link to="/bookings">عرض جميع الحجوزات</Link>
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Quick Actions */}
          <div>
            <Card>
              <CardHeader>
                <CardTitle>إجراءات سريعة</CardTitle>
                <CardDescription>إدارة حسابك وخدماتك</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <Button className="w-full" asChild>
                  <Link to="/services/add">
                    <Briefcase className="mr-2 h-4 w-4" />
                    إضافة خدمة جديدة
                  </Link>
                </Button>
                
                <Button variant="outline" className="w-full" asChild>
                  <Link to="/service-areas">
                    <MapPin className="mr-2 h-4 w-4" />
                    إدارة مناطق الخدمة
                  </Link>
                </Button>
                
                <Button variant="outline" className="w-full" asChild>
                  <Link to="/profile">
                    <User className="mr-2 h-4 w-4" />
                    تحديث الملف الشخصي
                  </Link>
                </Button>
                
                {profile?.verification_status !== 'approved' && (
                  <Button variant="outline" className="w-full" asChild>
                    <Link to="/verification">
                      <FileText className="mr-2 h-4 w-4" />
                      إكمال التحقق
                    </Link>
                  </Button>
                )}
              </CardContent>
            </Card>

            {/* Performance Summary */}
            <Card className="mt-6">
              <CardHeader>
                <CardTitle>ملخص الأداء</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">الخدمات المكتملة</span>
                  <span className="font-medium">{stats.completedBookings}</span>
                </div>
                
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">متوسط التقييم</span>
                  <div className="flex items-center">
                    <Star className="h-4 w-4 text-yellow-400 mr-1" />
                    <span className="font-medium">{stats.averageRating.toFixed(1)}</span>
                  </div>
                </div>
                
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">معدل الإكمال</span>
                  <span className="font-medium">{stats.completionRate.toFixed(1)}%</span>
                </div>
                
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">إجمالي الأرباح</span>
                  <span className="font-medium text-green-600">
                    {formatCurrency(stats.totalEarnings)}
                  </span>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProviderDashboard;

