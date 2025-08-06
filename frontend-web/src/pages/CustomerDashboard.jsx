import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
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
  Plus,
  User,
  LogOut,
  Settings,
  Bell,
  Search,
  Filter,
  Wrench,
  Zap,
  Sparkles,
  Hammer,
  Wind,
  Paintbrush
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

const CustomerDashboard = () => {
  const { user, logout } = useAuth();
  const [bookings, setBookings] = useState([]);
  const [serviceCategories, setServiceCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    totalBookings: 0,
    completedBookings: 0,
    activeBookings: 0,
    totalSpent: 0
  });

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      const [bookingsResponse, categoriesResponse] = await Promise.all([
        apiClient.getBookings({ per_page: 10 }),
        apiClient.getServiceCategories('ar')
      ]);

      setBookings(bookingsResponse.bookings || []);
      setServiceCategories(categoriesResponse.categories || []);

      // Calculate stats
      const totalBookings = bookingsResponse.bookings?.length || 0;
      const completedBookings = bookingsResponse.bookings?.filter(b => b.booking_status === 'completed').length || 0;
      const activeBookings = bookingsResponse.bookings?.filter(b => 
        ['pending', 'confirmed', 'in_progress'].includes(b.booking_status)
      ).length || 0;
      const totalSpent = bookingsResponse.bookings?.reduce((sum, booking) => 
        booking.booking_status === 'completed' ? sum + parseFloat(booking.total_amount) : sum, 0
      ) || 0;

      setStats({
        totalBookings,
        completedBookings,
        activeBookings,
        totalSpent
      });
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    await logout();
  };

  const categoryIcons = {
    'السباكة': Wrench,
    'الكهرباء': Zap,
    'التنظيف': Sparkles,
    'النجارة': Hammer,
    'صيانة التكييف': Wind,
    'الدهان': Paintbrush,
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
                        {user?.profile?.full_name || 'المستخدم'}
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
          <h2 className="text-3xl font-bold text-gray-900 mb-2">
            مرحباً، {user?.profile?.first_name || 'عزيزي العميل'}
          </h2>
          <p className="text-gray-600">إدارة حجوزاتك وطلب خدمات جديدة</p>
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
              <CardTitle className="text-sm font-medium">الخدمات المكتملة</CardTitle>
              <Star className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.completedBookings}</div>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">إجمالي المبلغ المدفوع</CardTitle>
              <span className="h-4 w-4 text-muted-foreground">ج.م</span>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{formatCurrency(stats.totalSpent)}</div>
            </CardContent>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Service Categories */}
          <div className="lg:col-span-2">
            <Card>
              <CardHeader>
                <CardTitle>اطلب خدمة جديدة</CardTitle>
                <CardDescription>اختر نوع الخدمة التي تحتاجها</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                  {serviceCategories.slice(0, 6).map((category) => {
                    const IconComponent = categoryIcons[category.name] || Wrench;
                    return (
                      <Link
                        key={category.id}
                        to={`/booking/${category.id}`}
                        className="p-4 border rounded-lg hover:shadow-md transition-shadow group"
                      >
                        <div className="flex flex-col items-center text-center space-y-2">
                          <div className="p-3 bg-blue-100 rounded-lg group-hover:bg-blue-200 transition-colors">
                            <IconComponent className="h-6 w-6 text-blue-600" />
                          </div>
                          <h3 className="font-medium text-sm">{category.name}</h3>
                          <Badge variant="secondary" className="text-xs">
                            {category.service_count} خدمة
                          </Badge>
                        </div>
                      </Link>
                    );
                  })}
                </div>
                
                <div className="mt-6 text-center">
                  <Button asChild>
                    <Link to="/services">
                      <Plus className="mr-2 h-4 w-4" />
                      عرض جميع الخدمات
                    </Link>
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Recent Bookings */}
          <div>
            <Card>
              <CardHeader>
                <CardTitle>الحجوزات الأخيرة</CardTitle>
                <CardDescription>آخر حجوزاتك</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {bookings.length === 0 ? (
                    <div className="text-center py-8">
                      <p className="text-gray-500 mb-4">لا توجد حجوزات بعد</p>
                      <Button asChild size="sm">
                        <Link to="/services">
                          <Plus className="mr-2 h-4 w-4" />
                          احجز خدمتك الأولى
                        </Link>
                      </Button>
                    </div>
                  ) : (
                    bookings.slice(0, 5).map((booking) => (
                      <div key={booking.id} className="flex items-center space-x-4 space-x-reverse">
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium text-gray-900 truncate">
                            {booking.service?.name || 'خدمة'}
                          </p>
                          <div className="flex items-center text-xs text-gray-500 space-x-2 space-x-reverse">
                            <Calendar className="h-3 w-3" />
                            <span>{formatDate(booking.scheduled_date)}</span>
                            <Clock className="h-3 w-3" />
                            <span>{formatTime(booking.scheduled_date)}</span>
                          </div>
                        </div>
                        <div className="flex flex-col items-end">
                          <Badge 
                            variant="secondary" 
                            className={getBookingStatusColor(booking.booking_status)}
                          >
                            {getBookingStatusText(booking.booking_status)}
                          </Badge>
                          <span className="text-xs text-gray-500 mt-1">
                            {formatCurrency(booking.total_amount)}
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
        </div>
      </div>
    </div>
  );
};

export default CustomerDashboard;

