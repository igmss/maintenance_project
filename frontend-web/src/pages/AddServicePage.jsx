import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Checkbox } from '@/components/ui/checkbox';
import { 
  Plus,
  DollarSign,
  Clock,
  Award,
  AlertCircle,
  CheckCircle,
  ArrowLeft,
  Star,
  Briefcase
} from 'lucide-react';
import { useAuth } from '../lib/auth.jsx';
import { apiClient } from '../lib/api';

const AddServicePage = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [loading, setLoading] = useState(false);
  const [categories, setCategories] = useState([]);
  const [services, setServices] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('');
  const [selectedService, setSelectedService] = useState('');
  const [currentServices, setCurrentServices] = useState([]);
  const [formData, setFormData] = useState({
    service_id: '',
    custom_price: '',
    experience_years: 0,
    is_available: true,
    description: ''
  });

  useEffect(() => {
    loadInitialData();
  }, []);

  useEffect(() => {
    if (selectedCategory) {
      loadCategoryServices(selectedCategory);
    }
  }, [selectedCategory]);

  const loadInitialData = async () => {
    try {
      const [categoriesResponse, providerResponse] = await Promise.all([
        apiClient.getServiceCategories('ar'),
        apiClient.getProviderProfile()
      ]);
      
      setCategories(categoriesResponse.categories || []);
      setCurrentServices(providerResponse.services || []);
    } catch (error) {
      console.error('Failed to load data:', error);
    }
  };

  const loadCategoryServices = async (categoryId) => {
    try {
      const response = await apiClient.getCategoryServices(categoryId, 'ar');
      setServices(response.services || []);
      setSelectedService('');
    } catch (error) {
      console.error('Failed to load category services:', error);
    }
  };

  const handleServiceSelect = (serviceId) => {
    setSelectedService(serviceId);
    const service = services.find(s => s.id === serviceId);
    if (service) {
      setFormData(prev => ({
        ...prev,
        service_id: serviceId,
        custom_price: service.base_price || ''
      }));
    }
  };

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.service_id) {
      alert('يرجى اختيار الخدمة');
      return;
    }

    if (!formData.custom_price || parseFloat(formData.custom_price) <= 0) {
      alert('يرجى إدخال سعر صحيح للخدمة');
      return;
    }

    setLoading(true);
    
    try {
      const serviceData = {
        service_id: formData.service_id,
        custom_price: parseFloat(formData.custom_price),
        experience_years: parseInt(formData.experience_years) || 0,
        is_available: formData.is_available,
        description: formData.description.trim()
      };

      await apiClient.addProviderService(serviceData);
      
      alert('تم إضافة الخدمة بنجاح!');
      navigate('/provider-dashboard');
    } catch (error) {
      console.error('Failed to add service:', error);
      
      if (error.message?.includes('already added')) {
        alert('هذه الخدمة مضافة بالفعل إلى قائمة خدماتك');
      } else {
        alert('حدث خطأ أثناء إضافة الخدمة. يرجى المحاولة مرة أخرى.');
      }
    } finally {
      setLoading(false);
    }
  };

  const isServiceAlreadyAdded = (serviceId) => {
    return currentServices.some(service => service.service_id === serviceId);
  };

  const getSelectedServiceDetails = () => {
    return services.find(s => s.id === selectedService);
  };

  const calculateEstimatedEarnings = () => {
    const price = parseFloat(formData.custom_price) || 0;
    const platformCommission = price * 0.15; // 15% platform commission
    const providerEarnings = price - platformCommission;
    
    return {
      totalPrice: price,
      platformCommission,
      providerEarnings
    };
  };

  const earnings = calculateEstimatedEarnings();
  const selectedServiceDetails = getSelectedServiceDetails();

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">إضافة خدمة جديدة</h1>
            <p className="text-gray-600">
              أضف خدمة جديدة إلى قائمة الخدمات التي تقدمها
            </p>
          </div>
          <Button variant="outline" onClick={() => navigate('/provider-dashboard')}>
            <ArrowLeft className="mr-2 h-4 w-4" />
            العودة للوحة التحكم
          </Button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Service Selection */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Briefcase className="mr-2 h-5 w-5" />
                اختيار الخدمة
              </CardTitle>
              <CardDescription>
                اختر فئة الخدمة ثم الخدمة المحددة التي تريد إضافتها
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="category">فئة الخدمة</Label>
                  <Select value={selectedCategory} onValueChange={setSelectedCategory}>
                    <SelectTrigger>
                      <SelectValue placeholder="اختر فئة الخدمة" />
                    </SelectTrigger>
                    <SelectContent>
                      {categories.map((category) => (
                        <SelectItem key={category.id} value={category.id}>
                          {category.name} ({category.service_count} خدمة)
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="service">الخدمة</Label>
                  <Select value={selectedService} onValueChange={handleServiceSelect} disabled={!selectedCategory}>
                    <SelectTrigger>
                      <SelectValue placeholder="اختر الخدمة" />
                    </SelectTrigger>
                    <SelectContent>
                      {services.map((service) => (
                        <SelectItem 
                          key={service.id} 
                          value={service.id}
                          disabled={isServiceAlreadyAdded(service.id)}
                        >
                          <div className="flex items-center justify-between w-full">
                            <span>{service.name}</span>
                            {isServiceAlreadyAdded(service.id) && (
                              <Badge variant="secondary" className="mr-2">مضافة</Badge>
                            )}
                          </div>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>

              {selectedServiceDetails && (
                <Alert>
                  <CheckCircle className="h-4 w-4" />
                  <AlertDescription>
                    <strong>{selectedServiceDetails.name}</strong>
                    <br />
                    {selectedServiceDetails.description}
                    <br />
                    <span className="text-sm text-gray-600">
                      السعر الأساسي: {selectedServiceDetails.base_price} ج.م
                      {selectedServiceDetails.estimated_duration && 
                        ` • المدة المتوقعة: ${selectedServiceDetails.estimated_duration} دقيقة`
                      }
                    </span>
                  </AlertDescription>
                </Alert>
              )}
            </CardContent>
          </Card>

          {/* Pricing & Experience */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <DollarSign className="mr-2 h-5 w-5" />
                التسعير والخبرة
              </CardTitle>
              <CardDescription>
                حدد سعرك ومستوى خبرتك في هذه الخدمة
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="price">سعر الخدمة (ج.م)</Label>
                  <Input
                    id="price"
                    type="number"
                    min="1"
                    step="0.01"
                    placeholder="0.00"
                    value={formData.custom_price}
                    onChange={(e) => handleInputChange('custom_price', e.target.value)}
                    required
                  />
                  <p className="text-xs text-gray-500">
                    السعر الأساسي المقترح: {selectedServiceDetails?.base_price || '0'} ج.م
                  </p>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="experience">سنوات الخبرة</Label>
                  <Select 
                    value={formData.experience_years.toString()} 
                    onValueChange={(value) => handleInputChange('experience_years', parseInt(value))}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="اختر مستوى الخبرة" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="0">مبتدئ (أقل من سنة)</SelectItem>
                      <SelectItem value="1">سنة واحدة</SelectItem>
                      <SelectItem value="2">سنتان</SelectItem>
                      <SelectItem value="3">3 سنوات</SelectItem>
                      <SelectItem value="5">5 سنوات</SelectItem>
                      <SelectItem value="10">10 سنوات أو أكثر</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              {/* Earnings Breakdown */}
              {earnings.totalPrice > 0 && (
                <div className="p-4 bg-blue-50 rounded-lg space-y-2">
                  <h4 className="font-medium text-blue-900">تفاصيل الأرباح لكل خدمة:</h4>
                  <div className="grid grid-cols-3 gap-4 text-sm">
                    <div>
                      <span className="text-gray-600">إجمالي السعر:</span>
                      <p className="font-medium">{earnings.totalPrice.toFixed(2)} ج.م</p>
                    </div>
                    <div>
                      <span className="text-gray-600">عمولة المنصة (15%):</span>
                      <p className="font-medium text-red-600">-{earnings.platformCommission.toFixed(2)} ج.م</p>
                    </div>
                    <div>
                      <span className="text-gray-600">صافي الربح:</span>
                      <p className="font-medium text-green-600">{earnings.providerEarnings.toFixed(2)} ج.م</p>
                    </div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Additional Details */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Star className="mr-2 h-5 w-5" />
                تفاصيل إضافية
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="description">وصف الخدمة (اختياري)</Label>
                <Textarea
                  id="description"
                  placeholder="أضف وصفاً مفصلاً عن خدمتك، خبرتك، والمعدات التي تستخدمها..."
                  value={formData.description}
                  onChange={(e) => handleInputChange('description', e.target.value)}
                  rows={4}
                />
                <p className="text-xs text-gray-500">
                  هذا الوصف سيساعد العملاء على فهم خدمتك بشكل أفضل
                </p>
              </div>

              <div className="flex items-center space-x-2 space-x-reverse">
                <Checkbox
                  id="available"
                  checked={formData.is_available}
                  onCheckedChange={(checked) => handleInputChange('is_available', checked)}
                />
                <Label htmlFor="available" className="text-sm">
                  الخدمة متاحة للحجز فوراً
                </Label>
              </div>
            </CardContent>
          </Card>

          {/* Current Services Summary */}
          {currentServices.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>خدماتك الحالية</CardTitle>
                <CardDescription>
                  الخدمات التي تقدمها حالياً ({currentServices.length} خدمة)
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                  {currentServices.slice(0, 6).map((service) => (
                    <div key={service.id} className="p-3 border rounded-lg">
                      <h4 className="font-medium text-sm">{service.service?.name || 'خدمة'}</h4>
                      <div className="flex items-center justify-between mt-1">
                        <span className="text-xs text-gray-600">
                          {service.custom_price} ج.م
                        </span>
                        <Badge variant={service.is_available ? "default" : "secondary"} className="text-xs">
                          {service.is_available ? 'متاحة' : 'غير متاحة'}
                        </Badge>
                      </div>
                    </div>
                  ))}
                </div>
                {currentServices.length > 6 && (
                  <p className="text-sm text-gray-500 mt-3">
                    +{currentServices.length - 6} خدمة أخرى
                  </p>
                )}
              </CardContent>
            </Card>
          )}

          {/* Submit */}
          <div className="flex justify-end space-x-4 space-x-reverse">
            <Button type="button" variant="outline" onClick={() => navigate('/provider-dashboard')}>
              إلغاء
            </Button>
            <Button type="submit" disabled={loading || !formData.service_id}>
              {loading ? (
                <>
                  <Clock className="mr-2 h-4 w-4 animate-spin" />
                  جاري الإضافة...
                </>
              ) : (
                <>
                  <Plus className="mr-2 h-4 w-4" />
                  إضافة الخدمة
                </>
              )}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AddServicePage;