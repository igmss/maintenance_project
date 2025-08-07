import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { 
  Search,
  MapPin,
  Star,
  DollarSign,
  Clock,
  Filter,
  Grid,
  List,
  Wrench,
  Zap,
  Sparkles,
  Hammer,
  Wind,
  Paintbrush,
  ArrowLeft,
  Users,
  TrendingUp
} from 'lucide-react';
import { useAuth } from '../lib/auth.jsx';
import { apiClient } from '../lib/api';
import { formatCurrency } from '../lib/utils';

const ServicesPage = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [categories, setCategories] = useState([]);
  const [services, setServices] = useState([]);
  const [filteredServices, setFilteredServices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [priceRange, setPriceRange] = useState('all');
  const [sortBy, setSortBy] = useState('popularity');
  const [viewMode, setViewMode] = useState('grid');

  useEffect(() => {
    loadServicesData();
  }, []);

  useEffect(() => {
    filterAndSortServices();
  }, [services, searchTerm, selectedCategory, priceRange, sortBy]);

  const loadServicesData = async () => {
    try {
      const [categoriesResponse] = await Promise.all([
        apiClient.getServiceCategories('ar')
      ]);
      
      setCategories(categoriesResponse.categories || []);
      
      // Load all services from all categories
      const allServices = [];
      for (const category of categoriesResponse.categories || []) {
        try {
          const categoryServices = await apiClient.getCategoryServices(category.id, 'ar');
          const servicesWithCategory = (categoryServices.services || []).map(service => ({
            ...service,
            category: category
          }));
          allServices.push(...servicesWithCategory);
        } catch (error) {
          console.error(`Failed to load services for category ${category.id}:`, error);
        }
      }
      
      setServices(allServices);
    } catch (error) {
      console.error('Failed to load services data:', error);
    } finally {
      setLoading(false);
    }
  };

  const filterAndSortServices = () => {
    let filtered = [...services];

    // Filter by search term
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      filtered = filtered.filter(service => 
        service.name?.toLowerCase().includes(term) ||
        service.description?.toLowerCase().includes(term) ||
        service.category?.name?.toLowerCase().includes(term)
      );
    }

    // Filter by category
    if (selectedCategory !== 'all') {
      filtered = filtered.filter(service => service.category?.id === selectedCategory);
    }

    // Filter by price range
    if (priceRange !== 'all') {
      const [min, max] = priceRange.split('-').map(Number);
      filtered = filtered.filter(service => {
        const price = parseFloat(service.base_price) || 0;
        if (max) {
          return price >= min && price <= max;
        } else {
          return price >= min;
        }
      });
    }

    // Sort services
    switch (sortBy) {
      case 'price_low':
        filtered.sort((a, b) => (parseFloat(a.base_price) || 0) - (parseFloat(b.base_price) || 0));
        break;
      case 'price_high':
        filtered.sort((a, b) => (parseFloat(b.base_price) || 0) - (parseFloat(a.base_price) || 0));
        break;
      case 'name':
        filtered.sort((a, b) => (a.name || '').localeCompare(b.name || '', 'ar'));
        break;
      case 'popularity':
      default:
        // Sort by popularity (services with more providers first)
        filtered.sort((a, b) => (b.provider_count || 0) - (a.provider_count || 0));
        break;
    }

    setFilteredServices(filtered);
  };

  const categoryIcons = {
    'السباكة': Wrench,
    'الكهرباء': Zap,
    'التنظيف': Sparkles,
    'النجارة': Hammer,
    'التكييف': Wind,
    'الدهان': Paintbrush
  };

  const getCategoryIcon = (categoryName) => {
    return categoryIcons[categoryName] || Wrench;
  };

  const getProviderCount = async (serviceId) => {
    try {
      // This would need to be implemented in the backend
      // For now, return a random number for demo
      return Math.floor(Math.random() * 20) + 1;
    } catch (error) {
      return 0;
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
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">تصفح الخدمات</h1>
            <p className="text-gray-600">
              اكتشف جميع الخدمات المتاحة واحجز خدمتك المفضلة
            </p>
          </div>
          <Button variant="outline" onClick={() => navigate('/dashboard')}>
            <ArrowLeft className="mr-2 h-4 w-4" />
            العودة للوحة التحكم
          </Button>
        </div>

        {/* Categories Quick Navigation */}
        <Card>
          <CardHeader>
            <CardTitle>الفئات الرئيسية</CardTitle>
            <CardDescription>تصفح الخدمات حسب الفئة</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
              {categories.map((category) => {
                const IconComponent = getCategoryIcon(category.name);
                return (
                  <button
                    key={category.id}
                    onClick={() => setSelectedCategory(category.id)}
                    className={`p-4 rounded-lg border text-center transition-all ${
                      selectedCategory === category.id 
                        ? 'bg-blue-50 border-blue-200 text-blue-700' 
                        : 'bg-white border-gray-200 hover:bg-gray-50'
                    }`}
                  >
                    <IconComponent className="h-8 w-8 mx-auto mb-2" />
                    <h3 className="font-medium text-sm">{category.name}</h3>
                    <Badge variant="secondary" className="text-xs mt-1">
                      {category.service_count} خدمة
                    </Badge>
                  </button>
                );
              })}
            </div>
          </CardContent>
        </Card>

        {/* Filters */}
        <Card>
          <CardContent className="p-4">
            <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                <Input
                  placeholder="البحث في الخدمات..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>

              <Select value={selectedCategory} onValueChange={setSelectedCategory}>
                <SelectTrigger>
                  <SelectValue placeholder="الفئة" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">جميع الفئات</SelectItem>
                  {categories.map((category) => (
                    <SelectItem key={category.id} value={category.id}>
                      {category.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>

              <Select value={priceRange} onValueChange={setPriceRange}>
                <SelectTrigger>
                  <SelectValue placeholder="النطاق السعري" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">جميع الأسعار</SelectItem>
                  <SelectItem value="0-100">أقل من 100 ج.م</SelectItem>
                  <SelectItem value="100-300">100 - 300 ج.م</SelectItem>
                  <SelectItem value="300-500">300 - 500 ج.م</SelectItem>
                  <SelectItem value="500-1000">500 - 1000 ج.م</SelectItem>
                  <SelectItem value="1000">أكثر من 1000 ج.م</SelectItem>
                </SelectContent>
              </Select>

              <Select value={sortBy} onValueChange={setSortBy}>
                <SelectTrigger>
                  <SelectValue placeholder="ترتيب حسب" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="popularity">الأكثر طلباً</SelectItem>
                  <SelectItem value="price_low">السعر (من الأقل للأعلى)</SelectItem>
                  <SelectItem value="price_high">السعر (من الأعلى للأقل)</SelectItem>
                  <SelectItem value="name">الاسم</SelectItem>
                </SelectContent>
              </Select>

              <div className="flex items-center space-x-2 space-x-reverse">
                <Button
                  variant={viewMode === 'grid' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setViewMode('grid')}
                >
                  <Grid className="h-4 w-4" />
                </Button>
                <Button
                  variant={viewMode === 'list' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setViewMode('list')}
                >
                  <List className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Results Count */}
        <div className="flex items-center justify-between">
          <p className="text-gray-600">
            تم العثور على <span className="font-medium">{filteredServices.length}</span> خدمة
          </p>
          
          {(searchTerm || selectedCategory !== 'all' || priceRange !== 'all') && (
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                setSearchTerm('');
                setSelectedCategory('all');
                setPriceRange('all');
                setSortBy('popularity');
              }}
            >
              <Filter className="mr-2 h-4 w-4" />
              مسح الفلاتر
            </Button>
          )}
        </div>

        {/* Services Grid/List */}
        {filteredServices.length === 0 ? (
          <Card>
            <CardContent className="p-8 text-center">
              <Search className="mx-auto h-12 w-12 text-gray-400 mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">لا توجد خدمات</h3>
              <p className="text-gray-500">
                لم يتم العثور على خدمات تطابق البحث الحالي
              </p>
            </CardContent>
          </Card>
        ) : (
          <div className={
            viewMode === 'grid' 
              ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6' 
              : 'space-y-4'
          }>
            {filteredServices.map((service) => {
              const IconComponent = getCategoryIcon(service.category?.name || '');
              
              if (viewMode === 'list') {
                return (
                  <Card key={service.id} className="hover:shadow-md transition-shadow">
                    <CardContent className="p-6">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-4 space-x-reverse flex-1">
                          <div className="p-3 bg-blue-100 rounded-lg">
                            <IconComponent className="h-6 w-6 text-blue-600" />
                          </div>
                          
                          <div className="flex-1 min-w-0">
                            <h3 className="text-lg font-semibold text-gray-900 mb-1">
                              {service.name}
                            </h3>
                            <p className="text-sm text-gray-600 mb-2 line-clamp-2">
                              {service.description}
                            </p>
                            
                            <div className="flex items-center space-x-4 space-x-reverse text-sm text-gray-500">
                              <div className="flex items-center">
                                <Badge variant="secondary">{service.category?.name}</Badge>
                              </div>
                              <div className="flex items-center">
                                <Users className="h-4 w-4 mr-1" />
                                <span>{Math.floor(Math.random() * 20) + 1} مقدم خدمة</span>
                              </div>
                              {service.estimated_duration && (
                                <div className="flex items-center">
                                  <Clock className="h-4 w-4 mr-1" />
                                  <span>{service.estimated_duration} دقيقة</span>
                                </div>
                              )}
                            </div>
                          </div>
                        </div>
                        
                        <div className="flex items-center space-x-4 space-x-reverse mr-4">
                          <div className="text-left">
                            <p className="text-sm text-gray-500">يبدأ من</p>
                            <p className="text-xl font-bold text-blue-600">
                              {formatCurrency(service.base_price)}
                            </p>
                          </div>
                          
                          <Button asChild>
                            <Link to={`/booking/${service.id}`}>
                              احجز الآن
                            </Link>
                          </Button>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                );
              }

              return (
                <Card key={service.id} className="hover:shadow-md transition-shadow group">
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between mb-4">
                      <div className="p-3 bg-blue-100 rounded-lg group-hover:bg-blue-200 transition-colors">
                        <IconComponent className="h-8 w-8 text-blue-600" />
                      </div>
                      <Badge variant="secondary">{service.category?.name}</Badge>
                    </div>
                    
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">
                      {service.name}
                    </h3>
                    
                    <p className="text-sm text-gray-600 mb-4 line-clamp-3">
                      {service.description}
                    </p>
                    
                    <div className="space-y-3">
                      <div className="flex items-center justify-between text-sm text-gray-500">
                        <div className="flex items-center">
                          <Users className="h-4 w-4 mr-1" />
                          <span>{Math.floor(Math.random() * 20) + 1} مقدم خدمة</span>
                        </div>
                        {service.estimated_duration && (
                          <div className="flex items-center">
                            <Clock className="h-4 w-4 mr-1" />
                            <span>{service.estimated_duration} دقيقة</span>
                          </div>
                        )}
                      </div>
                      
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-xs text-gray-500">يبدأ من</p>
                          <p className="text-lg font-bold text-blue-600">
                            {formatCurrency(service.base_price)}
                          </p>
                        </div>
                        
                        <Button asChild size="sm">
                          <Link to={`/booking/${service.id}`}>
                            احجز الآن
                          </Link>
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        )}

        {/* Popular Services Section */}
        {searchTerm === '' && selectedCategory === 'all' && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <TrendingUp className="mr-2 h-5 w-5" />
                الخدمات الأكثر طلباً
              </CardTitle>
              <CardDescription>
                الخدمات التي يطلبها العملاء بكثرة
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {filteredServices.slice(0, 4).map((service) => {
                  const IconComponent = getCategoryIcon(service.category?.name || '');
                  return (
                    <Link
                      key={service.id}
                      to={`/booking/${service.id}`}
                      className="p-4 border rounded-lg hover:shadow-md transition-all group"
                    >
                      <div className="flex items-center space-x-3 space-x-reverse">
                        <div className="p-2 bg-blue-100 rounded-lg group-hover:bg-blue-200 transition-colors">
                          <IconComponent className="h-5 w-5 text-blue-600" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <h4 className="font-medium text-sm truncate">{service.name}</h4>
                          <p className="text-xs text-gray-500">
                            من {formatCurrency(service.base_price)}
                          </p>
                        </div>
                      </div>
                    </Link>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
};

export default ServicesPage;