import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Calendar } from '@/components/ui/calendar';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { 
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { 
  ArrowLeft,
  Calendar as CalendarIcon,
  Clock,
  MapPin,
  Star,
  Phone,
  Shield,
  CheckCircle,
  Loader2,
  CreditCard
} from 'lucide-react';
import { format } from 'date-fns';
import { ar } from 'date-fns/locale';
import { apiClient } from '../lib/api';
import { 
  formatCurrency, 
  formatDistance, 
  getCurrentLocation,
  getInitials 
} from '../lib/utils';
import { useLocation } from '../hooks/useLocation';

const BookingPage = () => {
  const { serviceId } = useParams();
  const navigate = useNavigate();
  
  const [service, setService] = useState(null);
  const [providers, setProviders] = useState([]);
  const [selectedProvider, setSelectedProvider] = useState(null);
  const [selectedDate, setSelectedDate] = useState(null);
  const [selectedTime, setSelectedTime] = useState('');
  const [bookingData, setBookingData] = useState({
    description: '',
    address: '',
    phone: '',
    emergency: false
  });
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [userLocation, setUserLocation] = useState(null);
  const [shareLocationEnabled, setShareLocationEnabled] = useState(false);
  
  // Use location hook for customer location sharing
  const { 
    location: liveLocation, 
    loading: locationLoading, 
    error: locationError,
    watching: locationWatching,
    getCurrentLocation: getLocation,
    startWatching,
    stopWatching,
    shareLocation,
    getNearbyProviders
  } = useLocation();

  useEffect(() => {
    loadServiceData();
    getUserLocation();
  }, [serviceId]);

  const loadServiceData = async () => {
    setLoading(true);
    setError('');
    console.log('Loading service data for ID:', serviceId);
    
    try {
      // First, try to get it as a service
      try {
        const serviceResponse = await apiClient.getService(serviceId, 'ar');
        setService(serviceResponse);
        await searchProviders();
        return;
      } catch (serviceError) {
        console.log('Not a service ID, trying as category...');
      }
      
      // If not a service, try as category and get services in it
      try {
        const categoryServicesResponse = await apiClient.getCategoryServices(serviceId, 'ar');
        
        if (categoryServicesResponse.services && categoryServicesResponse.services.length > 0) {
          // Use the first service in the category as default
          const firstService = categoryServicesResponse.services[0];
          setService({
            id: firstService.id,
            name: firstService.name,
            description: firstService.description,
            base_price: firstService.base_price,
            category: categoryServicesResponse.category
          });
          
          // Search for providers with the actual service ID
          await searchProviders(firstService.id);
        } else {
          setError('لا توجد خدمات متاحة في هذه الفئة');
        }
      } catch (categoryError) {
        console.error('Failed to load category services:', categoryError);
        setError('فئة الخدمة غير موجودة');
      }
    } catch (error) {
      console.error('Failed to load service data:', error);
      setError('فشل في تحميل بيانات الخدمة');
    } finally {
      setLoading(false);
    }
  };

  const getUserLocation = async () => {
    try {
      const location = await getCurrentLocation();
      setUserLocation(location);
    } catch (error) {
      console.log('Could not get user location:', error);
    }
  };

  const searchProviders = async (actualServiceId = null) => {
    try {
      const currentLocation = liveLocation || userLocation;
      
      if (shareLocationEnabled && currentLocation) {
        // Use new nearby providers API with customer location
        const nearbyResponse = await getNearbyProviders(
          actualServiceId || service?.id || serviceId,
          currentLocation
        );
        setProviders(nearbyResponse.providers || []);
      } else {
        // Fallback to original search
        const searchData = {
          service_id: actualServiceId || service?.id || serviceId,
          latitude: currentLocation?.latitude || 30.0444, // Default to Cairo
          longitude: currentLocation?.longitude || 31.2357,
          max_distance_km: 25
        };
        
        const response = await apiClient.searchProviders(searchData);
        setProviders(response.providers || []);
      }
    } catch (error) {
      console.error('Failed to search providers:', error);
    }
  };

  const handleInputChange = (e) => {
    setBookingData({
      ...bookingData,
      [e.target.name]: e.target.value
    });
  };

  const handleProviderSelect = (provider) => {
    setSelectedProvider(provider);
  };

  const calculateTotalPrice = () => {
    if (!service || !selectedProvider) return 0;
    
    let basePrice = parseFloat(service.base_price);
    
    // Add emergency surcharge if applicable
    if (bookingData.emergency && service.emergency_surcharge_percentage) {
      basePrice += basePrice * (service.emergency_surcharge_percentage / 100);
    }
    
    return basePrice;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setError('');

    try {
      // Validate form
      if (!selectedProvider) {
        throw new Error('يرجى اختيار مقدم خدمة');
      }
      
      if (!selectedDate || !selectedTime) {
        throw new Error('يرجى اختيار تاريخ ووقت الموعد');
      }
      
      if (!bookingData.address || !bookingData.phone) {
        throw new Error('يرجى ملء العنوان ورقم الهاتف');
      }

      // Prepare booking data
      const bookingPayload = {
        service_id: service.id,
        provider_id: selectedProvider.id,
        scheduled_date: `${format(selectedDate, 'yyyy-MM-dd')}T${selectedTime}:00`,
        special_instructions: bookingData.description,
        service_address: {
          street: bookingData.address,
          city: userLocation?.city || 'القاهرة',
          governorate: userLocation?.governorate || 'القاهرة',
          latitude: userLocation?.latitude || 30.0444,
          longitude: userLocation?.longitude || 31.2357,
          formatted_address: bookingData.address,
          phone: bookingData.phone
        },
        is_emergency: bookingData.emergency
      };

      const response = await apiClient.createBooking(bookingPayload);
      
      // Redirect to booking confirmation or dashboard
      navigate('/dashboard', { 
        state: { 
          message: 'تم إنشاء الحجز بنجاح! سيتم التواصل معك قريباً.',
          bookingId: response.booking.id 
        }
      });
    } catch (err) {
      setError(err.message || 'حدث خطأ أثناء إنشاء الحجز');
    } finally {
      setSubmitting(false);
    }
  };

  // Generate available time slots
  const timeSlots = [
    '09:00', '10:00', '11:00', '12:00',
    '13:00', '14:00', '15:00', '16:00',
    '17:00', '18:00', '19:00', '20:00'
  ];

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!service) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">الخدمة غير موجودة</h2>
          <Button onClick={() => navigate('/dashboard')}>
            العودة إلى الصفحة الرئيسية
          </Button>
        </div>
      </div>
    );
  }

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
            <h1 className="text-xl font-semibold text-gray-900">حجز خدمة: {service.name}</h1>
          </div>
        </div>
      </header>

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <form onSubmit={handleSubmit} className="space-y-8">
          {error && (
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {/* Service Information */}
          <Card>
            <CardHeader>
              <CardTitle>تفاصيل الخدمة</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-medium text-gray-900">{service.name}</h3>
                  <p className="text-gray-600">{service.description}</p>
                </div>
                <div className="text-right">
                  <p className="text-2xl font-bold text-blue-600">
                    {formatCurrency(service.base_price)}
                  </p>
                  <p className="text-sm text-gray-500">السعر الأساسي</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Location Sharing Controls */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <MapPin className="h-5 w-5" />
                مشاركة الموقع المباشر
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">تفعيل مشاركة الموقع المباشر</p>
                    <p className="text-sm text-gray-600">للعثور على أقرب مقدمي الخدمة إليك</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <Button
                      type="button"
                      variant={shareLocationEnabled ? "default" : "outline"}
                      size="sm"
                      onClick={async () => {
                        if (!shareLocationEnabled) {
                          try {
                            await getLocation();
                            await startWatching();
                            setShareLocationEnabled(true);
                            // Refresh providers with new location
                            await searchProviders();
                          } catch (err) {
                            console.error('Failed to start location sharing:', err);
                          }
                        } else {
                          stopWatching();
                          setShareLocationEnabled(false);
                        }
                      }}
                      disabled={locationLoading}
                    >
                      {locationLoading ? (
                        <Loader2 className="h-4 w-4 animate-spin mr-2" />
                      ) : shareLocationEnabled ? (
                        <>
                          <CheckCircle className="h-4 w-4 mr-2" />
                          مُفعل
                        </>
                      ) : (
                        'تفعيل'
                      )}
                    </Button>
                  </div>
                </div>
                
                {locationError && (
                  <Alert variant="destructive">
                    <AlertDescription>{locationError}</AlertDescription>
                  </Alert>
                )}
                
                {liveLocation && shareLocationEnabled && (
                  <div className="bg-green-50 p-3 rounded-lg">
                    <div className="flex items-center text-green-700">
                      <CheckCircle className="h-4 w-4 mr-2" />
                      <span className="text-sm font-medium">الموقع مُحدث ومُشارك</span>
                    </div>
                    <p className="text-xs text-green-600 mt-1">
                      دقة الموقع: {liveLocation.accuracy?.toFixed(0)} متر
                    </p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Provider Selection */}
          <Card>
            <CardHeader>
              <CardTitle>اختيار مقدم الخدمة</CardTitle>
              <CardDescription>
                {providers.length > 0 
                  ? `${providers.length} مقدم خدمة متاح في منطقتك`
                  : 'لا توجد مقدمو خدمة متاحون في منطقتك حالياً'
                }
              </CardDescription>
            </CardHeader>
            <CardContent>
              {providers.length === 0 ? (
                <div className="text-center py-8">
                  <p className="text-gray-500 mb-4">عذراً، لا توجد مقدمو خدمة متاحون في منطقتك حالياً</p>
                  <Button variant="outline" onClick={() => navigate('/dashboard')}>
                    العودة إلى الصفحة الرئيسية
                  </Button>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {providers.map((provider) => (
                    <div
                      key={provider.id}
                      className={`p-4 border-2 rounded-lg cursor-pointer transition-all ${
                        selectedProvider?.id === provider.id
                          ? 'border-blue-500 bg-blue-50'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                      onClick={() => handleProviderSelect(provider)}
                    >
                      <div className="flex items-center space-x-4 space-x-reverse">
                        <Avatar className="h-12 w-12">
                          <AvatarImage src={provider.profile_image_url} />
                          <AvatarFallback>
                            {getInitials(provider.full_name)}
                          </AvatarFallback>
                        </Avatar>
                        <div className="flex-1">
                          <div className="flex items-center space-x-2 space-x-reverse">
                            <h4 className="font-medium text-gray-900">{provider.full_name}</h4>
                            {provider.is_verified && (
                              <Shield className="h-4 w-4 text-green-600" />
                            )}
                            {provider.current_location && shareLocationEnabled && (
                              <Badge variant="secondary" className="bg-green-100 text-green-700 text-xs">
                                متصل الآن
                              </Badge>
                            )}
                          </div>
                          <div className="flex items-center space-x-4 space-x-reverse text-sm text-gray-500">
                            <div className="flex items-center">
                              <Star className="h-4 w-4 text-yellow-400 mr-1" />
                              <span>{provider.average_rating?.toFixed(1) || 'جديد'}</span>
                            </div>
                            <div className="flex items-center">
                              <MapPin className="h-4 w-4 mr-1" />
                              <span>
                                {provider.distance_km 
                                  ? `${provider.distance_km} كم`
                                  : formatDistance(provider.distance || 0)
                                }
                              </span>
                            </div>
                            {provider.current_location && shareLocationEnabled && (
                              <div className="flex items-center text-green-600">
                                <Clock className="h-4 w-4 mr-1" />
                                <span className="text-xs">
                                  آخر تحديث: {new Date(provider.current_location.last_updated).toLocaleTimeString('ar-EG', { hour: '2-digit', minute: '2-digit' })}
                                </span>
                              </div>
                            )}
                          </div>
                          <p className="text-xs text-gray-400 mt-1">
                            {provider.completed_jobs || 0} خدمة مكتملة
                          </p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Date and Time Selection */}
          {selectedProvider && (
            <Card>
              <CardHeader>
                <CardTitle>اختيار الموعد</CardTitle>
                <CardDescription>اختر التاريخ والوقت المناسب لك</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <Label>التاريخ</Label>
                    <Popover>
                      <PopoverTrigger asChild>
                        <Button
                          variant="outline"
                          className="w-full justify-start text-right font-normal"
                        >
                          <CalendarIcon className="ml-2 h-4 w-4" />
                          {selectedDate ? format(selectedDate, 'PPP', { locale: ar }) : 'اختر التاريخ'}
                        </Button>
                      </PopoverTrigger>
                      <PopoverContent className="w-auto p-0" align="start">
                        <Calendar
                          mode="single"
                          selected={selectedDate}
                          onSelect={setSelectedDate}
                          disabled={(date) => date < new Date()}
                          initialFocus
                        />
                      </PopoverContent>
                    </Popover>
                  </div>

                  <div>
                    <Label>الوقت</Label>
                    <Select value={selectedTime} onValueChange={setSelectedTime}>
                      <SelectTrigger>
                        <SelectValue placeholder="اختر الوقت" />
                      </SelectTrigger>
                      <SelectContent>
                        {timeSlots.map((time) => (
                          <SelectItem key={time} value={time}>
                            {time}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Booking Details */}
          {selectedProvider && selectedDate && selectedTime && (
            <Card>
              <CardHeader>
                <CardTitle>تفاصيل الحجز</CardTitle>
                <CardDescription>أدخل التفاصيل الإضافية للحجز</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label htmlFor="address">العنوان *</Label>
                  <Input
                    id="address"
                    name="address"
                    placeholder="أدخل عنوانك بالتفصيل"
                    value={bookingData.address}
                    onChange={handleInputChange}
                    required
                  />
                </div>

                <div>
                  <Label htmlFor="phone">رقم الهاتف *</Label>
                  <Input
                    id="phone"
                    name="phone"
                    type="tel"
                    placeholder="01012345678"
                    value={bookingData.phone}
                    onChange={handleInputChange}
                    required
                    dir="ltr"
                  />
                </div>

                <div>
                  <Label htmlFor="description">وصف المشكلة (اختياري)</Label>
                  <Textarea
                    id="description"
                    name="description"
                    placeholder="اشرح المشكلة أو الخدمة المطلوبة بالتفصيل"
                    value={bookingData.description}
                    onChange={handleInputChange}
                    rows={4}
                  />
                </div>

                {/* Emergency Option */}
                <div className="flex items-center space-x-2 space-x-reverse">
                  <input
                    type="checkbox"
                    id="emergency"
                    name="emergency"
                    checked={bookingData.emergency}
                    onChange={(e) => setBookingData({
                      ...bookingData,
                      emergency: e.target.checked
                    })}
                    className="rounded border-gray-300"
                  />
                  <Label htmlFor="emergency" className="text-sm">
                    خدمة طارئة (رسوم إضافية 50%)
                  </Label>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Booking Summary */}
          {selectedProvider && selectedDate && selectedTime && (
            <Card>
              <CardHeader>
                <CardTitle>ملخص الحجز</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600">الخدمة:</span>
                    <span className="font-medium">{service.name}</span>
                  </div>
                  
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600">مقدم الخدمة:</span>
                    <span className="font-medium">{selectedProvider.full_name}</span>
                  </div>
                  
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600">التاريخ والوقت:</span>
                    <span className="font-medium">
                      {format(selectedDate, 'PPP', { locale: ar })} - {selectedTime}
                    </span>
                  </div>
                  
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600">السعر الأساسي:</span>
                    <span className="font-medium">{formatCurrency(service.base_price)}</span>
                  </div>
                  
                  {bookingData.emergency && (
                    <div className="flex justify-between items-center">
                      <span className="text-gray-600">رسوم الطوارئ (50%):</span>
                      <span className="font-medium text-orange-600">
                        {formatCurrency(service.base_price * 0.5)}
                      </span>
                    </div>
                  )}
                  
                  <div className="border-t pt-4">
                    <div className="flex justify-between items-center">
                      <span className="text-lg font-semibold">الإجمالي:</span>
                      <span className="text-2xl font-bold text-blue-600">
                        {formatCurrency(calculateTotalPrice())}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="mt-6">
                  <Button 
                    type="submit" 
                    className="w-full" 
                    disabled={submitting}
                    size="lg"
                  >
                    {submitting ? (
                      <>
                        <Loader2 className="ml-2 h-4 w-4 animate-spin" />
                        جاري إنشاء الحجز...
                      </>
                    ) : (
                      <>
                        <CreditCard className="ml-2 h-4 w-4" />
                        تأكيد الحجز والدفع
                      </>
                    )}
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}
        </form>
      </div>
    </div>
  );
};

export default BookingPage;

