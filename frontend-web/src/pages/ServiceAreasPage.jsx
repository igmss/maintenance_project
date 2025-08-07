import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { 
  MapPin,
  Plus,
  Edit2,
  Trash2,
  Clock,
  Radius,
  ArrowLeft,
  AlertCircle,
  CheckCircle,
  Navigation,
  Target
} from 'lucide-react';
import { useAuth } from '../lib/auth.jsx';
import { apiClient } from '../lib/api';

const ServiceAreasPage = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [serviceAreas, setServiceAreas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingArea, setEditingArea] = useState(null);
  const [formData, setFormData] = useState({
    area_name: '',
    center_latitude: '',
    center_longitude: '',
    radius_km: 10,
    is_primary_area: false,
    travel_time_minutes: 30
  });

  useEffect(() => {
    loadServiceAreas();
  }, []);

  const loadServiceAreas = async () => {
    try {
      const response = await apiClient.getProviderProfile();
      setServiceAreas(response.service_areas || []);
    } catch (error) {
      console.error('Failed to load service areas:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const resetForm = () => {
    setFormData({
      area_name: '',
      center_latitude: '',
      center_longitude: '',
      radius_km: 10,
      is_primary_area: false,
      travel_time_minutes: 30
    });
    setEditingArea(null);
    setShowAddForm(false);
  };

  const getCurrentLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setFormData(prev => ({
            ...prev,
            center_latitude: position.coords.latitude.toFixed(6),
            center_longitude: position.coords.longitude.toFixed(6)
          }));
        },
        (error) => {
          console.error('Error getting location:', error);
          alert('لا يمكن الحصول على الموقع الحالي. يرجى إدخال الإحداثيات يدوياً.');
        }
      );
    } else {
      alert('المتصفح لا يدعم خدمة تحديد المواقع');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validation
    if (!formData.area_name.trim()) {
      alert('يرجى إدخال اسم المنطقة');
      return;
    }

    if (!formData.center_latitude || !formData.center_longitude) {
      alert('يرجى إدخال إحداثيات المنطقة');
      return;
    }

    if (formData.radius_km < 1 || formData.radius_km > 50) {
      alert('نطاق الخدمة يجب أن يكون بين 1 و 50 كيلومتر');
      return;
    }

    setLoading(true);
    
    try {
      const areaData = {
        area_name: formData.area_name.trim(),
        center_latitude: parseFloat(formData.center_latitude),
        center_longitude: parseFloat(formData.center_longitude),
        radius_km: parseFloat(formData.radius_km),
        is_primary_area: formData.is_primary_area,
        travel_time_minutes: parseInt(formData.travel_time_minutes)
      };

      if (editingArea) {
        await apiClient.updateServiceArea(editingArea.id, areaData);
        alert('تم تحديث منطقة الخدمة بنجاح!');
      } else {
        await apiClient.addServiceArea(areaData);
        alert('تم إضافة منطقة الخدمة بنجاح!');
      }
      
      await loadServiceAreas();
      resetForm();
    } catch (error) {
      console.error('Failed to save service area:', error);
      alert('حدث خطأ أثناء حفظ منطقة الخدمة. يرجى المحاولة مرة أخرى.');
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (area) => {
    setFormData({
      area_name: area.area_name,
      center_latitude: area.center_latitude,
      center_longitude: area.center_longitude,
      radius_km: area.radius_km,
      is_primary_area: area.is_primary_area,
      travel_time_minutes: area.travel_time_minutes
    });
    setEditingArea(area);
    setShowAddForm(true);
  };

  const handleDelete = async (areaId) => {
    if (!confirm('هل أنت متأكد من حذف هذه المنطقة؟')) {
      return;
    }

    setLoading(true);
    
    try {
      await apiClient.deleteServiceArea(areaId);
      await loadServiceAreas();
      alert('تم حذف منطقة الخدمة بنجاح!');
    } catch (error) {
      console.error('Failed to delete service area:', error);
      alert('حدث خطأ أثناء حذف منطقة الخدمة');
    } finally {
      setLoading(false);
    }
  };

  const setPrimaryArea = async (areaId) => {
    setLoading(true);
    
    try {
      await apiClient.setPrimaryServiceArea(areaId);
      await loadServiceAreas();
      alert('تم تعيين المنطقة الرئيسية بنجاح!');
    } catch (error) {
      console.error('Failed to set primary area:', error);
      alert('حدث خطأ أثناء تعيين المنطقة الرئيسية');
    } finally {
      setLoading(false);
    }
  };

  const calculateCoverage = () => {
    const totalRadius = serviceAreas.reduce((sum, area) => sum + parseFloat(area.radius_km || 0), 0);
    const averageRadius = serviceAreas.length > 0 ? totalRadius / serviceAreas.length : 0;
    return {
      totalAreas: serviceAreas.length,
      averageRadius: averageRadius.toFixed(1),
      totalCoverage: (Math.PI * Math.pow(averageRadius, 2) * serviceAreas.length).toFixed(0)
    };
  };

  const coverage = calculateCoverage();

  if (loading && !showAddForm) {
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
            <h1 className="text-3xl font-bold text-gray-900 mb-2">مناطق الخدمة</h1>
            <p className="text-gray-600">
              حدد المناطق الجغرافية التي تقدم فيها خدماتك
            </p>
          </div>
          <Button variant="outline" onClick={() => navigate('/provider-dashboard')}>
            <ArrowLeft className="mr-2 h-4 w-4" />
            العودة للوحة التحكم
          </Button>
        </div>

        {/* Coverage Statistics */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">مناطق الخدمة</p>
                  <p className="text-2xl font-bold">{coverage.totalAreas}</p>
                </div>
                <MapPin className="h-8 w-8 text-blue-600" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">متوسط نطاق الخدمة</p>
                  <p className="text-2xl font-bold">{coverage.averageRadius} كم</p>
                </div>
                <Radius className="h-8 w-8 text-green-600" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">التغطية الإجمالية</p>
                  <p className="text-2xl font-bold">{coverage.totalCoverage} كم²</p>
                </div>
                <Target className="h-8 w-8 text-purple-600" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Add/Edit Form */}
        {showAddForm && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Plus className="mr-2 h-5 w-5" />
                {editingArea ? 'تعديل منطقة الخدمة' : 'إضافة منطقة خدمة جديدة'}
              </CardTitle>
              <CardDescription>
                حدد المنطقة الجغرافية ونطاق الخدمة بالكيلومتر
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="area_name">اسم المنطقة</Label>
                    <Input
                      id="area_name"
                      placeholder="مثال: وسط البلد، النزهة، المعادي"
                      value={formData.area_name}
                      onChange={(e) => handleInputChange('area_name', e.target.value)}
                      required
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="radius">نطاق الخدمة (كم)</Label>
                    <Select 
                      value={formData.radius_km.toString()} 
                      onValueChange={(value) => handleInputChange('radius_km', parseFloat(value))}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="اختر نطاق الخدمة" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="5">5 كيلومتر</SelectItem>
                        <SelectItem value="10">10 كيلومتر</SelectItem>
                        <SelectItem value="15">15 كيلومتر</SelectItem>
                        <SelectItem value="20">20 كيلومتر</SelectItem>
                        <SelectItem value="25">25 كيلومتر</SelectItem>
                        <SelectItem value="30">30 كيلومتر</SelectItem>
                        <SelectItem value="50">50 كيلومتر</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="latitude">خط العرض</Label>
                    <Input
                      id="latitude"
                      type="number"
                      step="0.000001"
                      placeholder="30.044420"
                      value={formData.center_latitude}
                      onChange={(e) => handleInputChange('center_latitude', e.target.value)}
                      required
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="longitude">خط الطول</Label>
                    <Input
                      id="longitude"
                      type="number"
                      step="0.000001"
                      placeholder="31.235712"
                      value={formData.center_longitude}
                      onChange={(e) => handleInputChange('center_longitude', e.target.value)}
                      required
                    />
                  </div>

                  <div className="space-y-2">
                    <Label>&nbsp;</Label>
                    <Button 
                      type="button" 
                      variant="outline" 
                      onClick={getCurrentLocation}
                      className="w-full"
                    >
                      <Navigation className="mr-2 h-4 w-4" />
                      الموقع الحالي
                    </Button>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="travel_time">وقت الوصول (دقيقة)</Label>
                    <Select 
                      value={formData.travel_time_minutes.toString()} 
                      onValueChange={(value) => handleInputChange('travel_time_minutes', parseInt(value))}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="وقت الوصول المتوقع" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="15">15 دقيقة</SelectItem>
                        <SelectItem value="30">30 دقيقة</SelectItem>
                        <SelectItem value="45">45 دقيقة</SelectItem>
                        <SelectItem value="60">60 دقيقة</SelectItem>
                        <SelectItem value="90">90 دقيقة</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label>&nbsp;</Label>
                    <div className="flex items-center space-x-2 space-x-reverse h-10">
                      <Switch
                        id="primary"
                        checked={formData.is_primary_area}
                        onCheckedChange={(checked) => handleInputChange('is_primary_area', checked)}
                      />
                      <Label htmlFor="primary" className="text-sm">
                        منطقة رئيسية
                      </Label>
                    </div>
                  </div>
                </div>

                <Alert>
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription>
                    <strong>نصائح لتحديد المناطق:</strong>
                    <br />
                    • استخدم أسماء مناطق معروفة لسهولة التعرف عليها
                    • حدد نطاق خدمة مناسب لوقت الانتقال
                    • يمكنك تعيين منطقة واحدة فقط كمنطقة رئيسية
                    • المنطقة الرئيسية تظهر أولاً في نتائج البحث
                  </AlertDescription>
                </Alert>

                <div className="flex justify-end space-x-4 space-x-reverse">
                  <Button type="button" variant="outline" onClick={resetForm}>
                    إلغاء
                  </Button>
                  <Button type="submit" disabled={loading}>
                    {loading ? (
                      <>
                        <Clock className="mr-2 h-4 w-4 animate-spin" />
                        جاري الحفظ...
                      </>
                    ) : (
                      <>
                        <CheckCircle className="mr-2 h-4 w-4" />
                        {editingArea ? 'تحديث المنطقة' : 'إضافة المنطقة'}
                      </>
                    )}
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        )}

        {/* Service Areas List */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>مناطق الخدمة الحالية</CardTitle>
                <CardDescription>
                  المناطق التي تقدم فيها خدماتك حالياً ({serviceAreas.length} منطقة)
                </CardDescription>
              </div>
              {!showAddForm && (
                <Button onClick={() => setShowAddForm(true)}>
                  <Plus className="mr-2 h-4 w-4" />
                  إضافة منطقة جديدة
                </Button>
              )}
            </div>
          </CardHeader>
          <CardContent>
            {serviceAreas.length === 0 ? (
              <div className="text-center py-8">
                <MapPin className="mx-auto h-12 w-12 text-gray-400 mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">لا توجد مناطق خدمة</h3>
                <p className="text-gray-500 mb-4">
                  أضف مناطق الخدمة لتتمكن من تلقي طلبات الخدمة
                </p>
                <Button onClick={() => setShowAddForm(true)}>
                  <Plus className="mr-2 h-4 w-4" />
                  إضافة منطقة الخدمة الأولى
                </Button>
              </div>
            ) : (
              <div className="space-y-4">
                {serviceAreas.map((area) => (
                  <div key={area.id} className="p-4 border rounded-lg">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 space-x-reverse mb-2">
                          <h3 className="text-lg font-semibold">{area.area_name}</h3>
                          {area.is_primary_area && (
                            <Badge variant="default">منطقة رئيسية</Badge>
                          )}
                        </div>
                        
                        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-sm text-gray-600">
                          <div className="flex items-center">
                            <Radius className="h-4 w-4 mr-2" />
                            نطاق الخدمة: {area.radius_km} كم
                          </div>
                          <div className="flex items-center">
                            <Clock className="h-4 w-4 mr-2" />
                            وقت الوصول: {area.travel_time_minutes} دقيقة
                          </div>
                          <div className="flex items-center">
                            <MapPin className="h-4 w-4 mr-2" />
                            {area.center_latitude}, {area.center_longitude}
                          </div>
                          <div className="flex items-center">
                            <Navigation className="h-4 w-4 mr-2" />
                            <a 
                              href={`https://maps.google.com/?q=${area.center_latitude},${area.center_longitude}`}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-blue-600 hover:underline"
                            >
                              عرض على الخريطة
                            </a>
                          </div>
                        </div>
                      </div>
                      
                      <div className="flex items-center space-x-2 space-x-reverse mr-4">
                        {!area.is_primary_area && (
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => setPrimaryArea(area.id)}
                          >
                            تعيين كرئيسية
                          </Button>
                        )}
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleEdit(area)}
                        >
                          <Edit2 className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleDelete(area.id)}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Tips Card */}
        <Card>
          <CardHeader>
            <CardTitle>نصائح لإدارة مناطق الخدمة</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-3">
                <h4 className="font-medium">تحسين التغطية:</h4>
                <ul className="space-y-2 text-sm text-gray-600">
                  <li>• أضف مناطق متنوعة لزيادة عدد الطلبات</li>
                  <li>• حدد نطاق خدمة مناسب لوقت انتقالك</li>
                  <li>• استخدم أسماء مناطق معروفة للعملاء</li>
                  <li>• اختر منطقة رئيسية تناسب موقعك</li>
                </ul>
              </div>
              
              <div className="space-y-3">
                <h4 className="font-medium">الحصول على المزيد من الطلبات:</h4>
                <ul className="space-y-2 text-sm text-gray-600">
                  <li>• قلل وقت الوصول المتوقع قدر الإمكان</li>
                  <li>• أضف مناطق ذات كثافة سكانية عالية</li>
                  <li>• حدث إحداثياتك بدقة للحصول على نتائج أفضل</li>
                  <li>• تأكد من تغطية مناطق العمل والسكن</li>
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default ServiceAreasPage;