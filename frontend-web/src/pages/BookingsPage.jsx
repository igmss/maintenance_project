import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { 
  Calendar,
  Clock,
  MapPin,
  Star,
  Phone,
  MessageSquare,
  Filter,
  Search,
  Eye,
  CheckCircle,
  XCircle,
  AlertCircle,
  DollarSign,
  User,
  Briefcase,
  ArrowLeft
} from 'lucide-react';
import { useAuth } from '../lib/auth.jsx';
import { apiClient } from '../lib/api';
import { 
  formatCurrency, 
  formatDate, 
  formatTime, 
  getBookingStatusColor, 
  getBookingStatusText
} from '../lib/utils';
import { useNavigate } from 'react-router-dom';

const BookingsPage = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [bookings, setBookings] = useState([]);
  const [filteredBookings, setFilteredBookings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [dateFilter, setDateFilter] = useState('all');

  const isProvider = user?.user_type === 'service_provider';

  useEffect(() => {
    loadBookings();
  }, []);

  useEffect(() => {
    filterBookings();
  }, [bookings, activeTab, searchTerm, statusFilter, dateFilter]);

  const loadBookings = async () => {
    try {
      const response = await apiClient.getBookings({ per_page: 100 });
      setBookings(response.bookings || []);
    } catch (error) {
      console.error('Failed to load bookings:', error);
    } finally {
      setLoading(false);
    }
  };

  const filterBookings = () => {
    let filtered = [...bookings];

    // Filter by tab
    if (activeTab !== 'all') {
      const tabFilters = {
        active: ['pending', 'confirmed', 'in_progress'],
        completed: ['completed'],
        cancelled: ['cancelled', 'disputed']
      };
      filtered = filtered.filter(booking => 
        tabFilters[activeTab]?.includes(booking.booking_status)
      );
    }

    // Filter by search term
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      filtered = filtered.filter(booking => 
        booking.service?.name?.toLowerCase().includes(term) ||
        booking.provider?.business_name?.toLowerCase().includes(term) ||
        booking.customer?.full_name?.toLowerCase().includes(term)
      );
    }

    // Filter by status
    if (statusFilter !== 'all') {
      filtered = filtered.filter(booking => booking.booking_status === statusFilter);
    }

    // Filter by date
    if (dateFilter !== 'all') {
      const now = new Date();
      const bookingDate = new Date(booking.scheduled_date);
      
      switch (dateFilter) {
        case 'today':
          filtered = filtered.filter(booking => {
            const bookingDate = new Date(booking.scheduled_date);
            return bookingDate.toDateString() === now.toDateString();
          });
          break;
        case 'week':
          const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
          filtered = filtered.filter(booking => {
            const bookingDate = new Date(booking.scheduled_date);
            return bookingDate >= weekAgo;
          });
          break;
        case 'month':
          const monthAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
          filtered = filtered.filter(booking => {
            const bookingDate = new Date(booking.scheduled_date);
            return bookingDate >= monthAgo;
          });
          break;
      }
    }

    // Sort by scheduled date (newest first)
    filtered.sort((a, b) => new Date(b.scheduled_date) - new Date(a.scheduled_date));

    setFilteredBookings(filtered);
  };

  const handleStatusUpdate = async (bookingId, newStatus) => {
    try {
      await apiClient.updateBookingStatus(bookingId, { status: newStatus });
      await loadBookings(); // Reload to get updated data
    } catch (error) {
      console.error('Failed to update booking status:', error);
      alert('حدث خطأ أثناء تحديث حالة الحجز');
    }
  };

  const getBookingActions = (booking) => {
    if (!isProvider) return null;

    const actions = [];
    
    switch (booking.booking_status) {
      case 'pending':
        actions.push(
          <Button 
            key="accept" 
            size="sm" 
            onClick={() => handleStatusUpdate(booking.id, 'confirmed')}
          >
            <CheckCircle className="h-4 w-4 mr-1" />
            قبول
          </Button>,
          <Button 
            key="reject" 
            size="sm" 
            variant="outline"
            onClick={() => handleStatusUpdate(booking.id, 'cancelled')}
          >
            <XCircle className="h-4 w-4 mr-1" />
            رفض
          </Button>
        );
        break;
      case 'confirmed':
        actions.push(
          <Button 
            key="start" 
            size="sm"
            onClick={() => handleStatusUpdate(booking.id, 'in_progress')}
          >
            بدء الخدمة
          </Button>
        );
        break;
      case 'in_progress':
        actions.push(
          <Button 
            key="complete" 
            size="sm"
            onClick={() => handleStatusUpdate(booking.id, 'completed')}
          >
            إنهاء الخدمة
          </Button>
        );
        break;
    }

    return actions;
  };

  const getContactInfo = (booking) => {
    if (isProvider) {
      return {
        name: booking.customer?.full_name || 'عميل',
        phone: booking.customer?.phone,
        type: 'العميل'
      };
    } else {
      return {
        name: booking.provider?.business_name || 'مقدم الخدمة',
        phone: booking.provider?.phone,
        type: 'مقدم الخدمة'
      };
    }
  };

  const getBookingStats = () => {
    const stats = {
      total: bookings.length,
      active: bookings.filter(b => ['pending', 'confirmed', 'in_progress'].includes(b.booking_status)).length,
      completed: bookings.filter(b => b.booking_status === 'completed').length,
      cancelled: bookings.filter(b => ['cancelled', 'disputed'].includes(b.booking_status)).length
    };

    if (isProvider) {
      stats.totalEarnings = bookings
        .filter(b => b.booking_status === 'completed')
        .reduce((sum, b) => sum + parseFloat(b.provider_earnings || 0), 0);
    } else {
      stats.totalSpent = bookings
        .filter(b => b.booking_status === 'completed')
        .reduce((sum, b) => sum + parseFloat(b.total_amount || 0), 0);
    }

    return stats;
  };

  const stats = getBookingStats();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              {isProvider ? 'طلبات الخدمة' : 'حجوزاتي'}
            </h1>
            <p className="text-gray-600">
              {isProvider 
                ? 'إدارة طلبات الخدمة الواردة إليك' 
                : 'تتبع جميع حجوزاتك وخدماتك'
              }
            </p>
          </div>
          <Button 
            variant="outline" 
            onClick={() => navigate(isProvider ? '/provider-dashboard' : '/dashboard')}
          >
            <ArrowLeft className="mr-2 h-4 w-4" />
            العودة للوحة التحكم
          </Button>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">إجمالي الحجوزات</p>
                  <p className="text-2xl font-bold">{stats.total}</p>
                </div>
                <Briefcase className="h-8 w-8 text-blue-600" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">نشطة</p>
                  <p className="text-2xl font-bold text-orange-600">{stats.active}</p>
                </div>
                <AlertCircle className="h-8 w-8 text-orange-600" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">مكتملة</p>
                  <p className="text-2xl font-bold text-green-600">{stats.completed}</p>
                </div>
                <CheckCircle className="h-8 w-8 text-green-600" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">
                    {isProvider ? 'إجمالي الأرباح' : 'إجمالي الإنفاق'}
                  </p>
                  <p className="text-2xl font-bold text-blue-600">
                    {formatCurrency(stats.totalEarnings || stats.totalSpent || 0)}
                  </p>
                </div>
                <DollarSign className="h-8 w-8 text-blue-600" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Filters */}
        <Card>
          <CardContent className="p-4">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                <Input
                  placeholder="البحث في الحجوزات..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>

              <Select value={statusFilter} onValueChange={setStatusFilter}>
                <SelectTrigger>
                  <SelectValue placeholder="الحالة" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">جميع الحالات</SelectItem>
                  <SelectItem value="pending">في الانتظار</SelectItem>
                  <SelectItem value="confirmed">مؤكدة</SelectItem>
                  <SelectItem value="in_progress">قيد التنفيذ</SelectItem>
                  <SelectItem value="completed">مكتملة</SelectItem>
                  <SelectItem value="cancelled">ملغية</SelectItem>
                </SelectContent>
              </Select>

              <Select value={dateFilter} onValueChange={setDateFilter}>
                <SelectTrigger>
                  <SelectValue placeholder="التاريخ" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">جميع التواريخ</SelectItem>
                  <SelectItem value="today">اليوم</SelectItem>
                  <SelectItem value="week">آخر أسبوع</SelectItem>
                  <SelectItem value="month">آخر شهر</SelectItem>
                </SelectContent>
              </Select>

              <Button variant="outline" onClick={() => {
                setSearchTerm('');
                setStatusFilter('all');
                setDateFilter('all');
                setActiveTab('all');
              }}>
                <Filter className="mr-2 h-4 w-4" />
                مسح الفلاتر
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Bookings Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="all">الكل ({stats.total})</TabsTrigger>
            <TabsTrigger value="active">نشطة ({stats.active})</TabsTrigger>
            <TabsTrigger value="completed">مكتملة ({stats.completed})</TabsTrigger>
            <TabsTrigger value="cancelled">ملغية ({stats.cancelled})</TabsTrigger>
          </TabsList>

          <TabsContent value={activeTab}>
            {filteredBookings.length === 0 ? (
              <Card>
                <CardContent className="p-8 text-center">
                  <Briefcase className="mx-auto h-12 w-12 text-gray-400 mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">لا توجد حجوزات</h3>
                  <p className="text-gray-500">
                    {activeTab === 'all' 
                      ? 'لم تقم بإجراء أي حجوزات بعد'
                      : `لا توجد حجوزات ${activeTab === 'active' ? 'نشطة' : activeTab === 'completed' ? 'مكتملة' : 'ملغية'}`
                    }
                  </p>
                </CardContent>
              </Card>
            ) : (
              <div className="space-y-4">
                {filteredBookings.map((booking) => {
                  const contact = getContactInfo(booking);
                  const actions = getBookingActions(booking);

                  return (
                    <Card key={booking.id}>
                      <CardContent className="p-6">
                        <div className="flex items-start justify-between mb-4">
                          <div className="flex-1">
                            <div className="flex items-center space-x-2 space-x-reverse mb-2">
                              <h3 className="text-lg font-semibold">
                                {booking.service?.name || 'خدمة'}
                              </h3>
                              <Badge className={getBookingStatusColor(booking.booking_status)}>
                                {getBookingStatusText(booking.booking_status)}
                              </Badge>
                            </div>
                            
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 text-sm text-gray-600">
                              <div className="flex items-center">
                                <Calendar className="h-4 w-4 mr-2" />
                                {formatDate(booking.scheduled_date)}
                              </div>
                              <div className="flex items-center">
                                <Clock className="h-4 w-4 mr-2" />
                                {formatTime(booking.scheduled_date)}
                              </div>
                              <div className="flex items-center">
                                <User className="h-4 w-4 mr-2" />
                                {contact.name}
                              </div>
                              <div className="flex items-center">
                                <DollarSign className="h-4 w-4 mr-2" />
                                {formatCurrency(booking.total_amount)}
                              </div>
                            </div>

                            {booking.service_address && (
                              <div className="flex items-start mt-2 text-sm text-gray-600">
                                <MapPin className="h-4 w-4 mr-2 mt-0.5 flex-shrink-0" />
                                <span>{booking.service_address.formatted_address || 'عنوان الخدمة'}</span>
                              </div>
                            )}

                            {booking.special_instructions && (
                              <div className="mt-2 text-sm text-gray-600">
                                <strong>ملاحظات خاصة:</strong> {booking.special_instructions}
                              </div>
                            )}
                          </div>

                          {/* Actions */}
                          <div className="flex flex-col space-y-2 mr-4">
                            {actions && actions.length > 0 && (
                              <div className="flex flex-col space-y-2">
                                {actions}
                              </div>
                            )}
                            
                            {contact.phone && (
                              <Button variant="outline" size="sm" asChild>
                                <a href={`tel:${contact.phone}`}>
                                  <Phone className="h-4 w-4 mr-1" />
                                  اتصال
                                </a>
                              </Button>
                            )}
                          </div>
                        </div>

                        {/* Provider Earnings (for providers) */}
                        {isProvider && booking.booking_status === 'completed' && (
                          <div className="mt-4 p-3 bg-green-50 rounded-lg">
                            <div className="flex justify-between items-center text-sm">
                              <span>إجمالي السعر: {formatCurrency(booking.total_amount)}</span>
                              <span>عمولة المنصة: {formatCurrency(booking.platform_commission)}</span>
                              <span className="font-medium text-green-700">
                                صافي الربح: {formatCurrency(booking.provider_earnings)}
                              </span>
                            </div>
                          </div>
                        )}
                      </CardContent>
                    </Card>
                  );
                })}
              </div>
            )}
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default BookingsPage;