import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { 
  Wrench, 
  Zap, 
  Sparkles, 
  Hammer, 
  Wind, 
  Paintbrush,
  MapPin,
  Star,
  Shield,
  Clock,
  Phone,
  Mail,
  CheckCircle,
  ArrowRight,
  Users,
  Award,
  Headphones
} from 'lucide-react';
import { apiClient } from '../lib/api';
import { formatCurrency } from '../lib/utils';

const LandingPage = () => {
  const [serviceCategories, setServiceCategories] = useState([]);
  const [location, setLocation] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadServiceCategories();
  }, []);

  const loadServiceCategories = async () => {
    try {
      const response = await apiClient.getServiceCategories('ar');
      setServiceCategories(response.categories || []);
    } catch (error) {
      console.error('Failed to load service categories:', error);
    } finally {
      setLoading(false);
    }
  };

  const categoryIcons = {
    'السباكة': Wrench,
    'الكهرباء': Zap,
    'التنظيف': Sparkles,
    'النجارة': Hammer,
    'صيانة التكييف': Wind,
    'الدهان': Paintbrush,
  };

  const features = [
    {
      icon: Shield,
      title: 'فنيون معتمدون',
      description: 'جميع مقدمي الخدمة معتمدون ومتحققون'
    },
    {
      icon: Clock,
      title: 'خدمة سريعة',
      description: 'وصول سريع في نفس اليوم أو اليوم التالي'
    },
    {
      icon: Star,
      title: 'جودة مضمونة',
      description: 'ضمان على جميع الخدمات مع إمكانية التقييم'
    },
    {
      icon: Headphones,
      title: 'دعم 24/7',
      description: 'خدمة عملاء متاحة على مدار الساعة'
    }
  ];

  const stats = [
    { number: '10,000+', label: 'عميل راض' },
    { number: '500+', label: 'فني معتمد' },
    { number: '50,000+', label: 'خدمة مكتملة' },
    { number: '4.8', label: 'تقييم العملاء' }
  ];

  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <h1 className="text-2xl font-bold text-blue-600">منصة الصيانة</h1>
              </div>
            </div>
            <div className="flex items-center space-x-4 space-x-reverse">
              <Link to="/login">
                <Button variant="ghost">تسجيل الدخول</Button>
              </Link>
              <Link to="/register">
                <Button>إنشاء حساب</Button>
              </Link>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="bg-gradient-to-br from-blue-600 via-blue-700 to-blue-800 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
          <div className="text-center">
            <h1 className="text-4xl md:text-6xl font-bold mb-6">
              خدمات الصيانة المنزلية
              <span className="block text-yellow-400">بضغطة زر واحدة</span>
            </h1>
            <p className="text-xl md:text-2xl mb-8 text-blue-100 max-w-3xl mx-auto">
              احصل على أفضل خدمات الصيانة من فنيين معتمدين في جميع أنحاء مصر
            </p>
            
            {/* Search Bar */}
            <div className="max-w-2xl mx-auto bg-white rounded-lg p-2 flex flex-col sm:flex-row gap-2">
              <div className="flex-1 flex items-center">
                <MapPin className="h-5 w-5 text-gray-400 mr-3" />
                <Input
                  placeholder="أدخل موقعك (المحافظة أو المدينة)"
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                  className="border-0 focus:ring-0 text-gray-900"
                />
              </div>
              <Button size="lg" className="bg-blue-600 hover:bg-blue-700">
                ابحث عن خدمات
                <ArrowRight className="mr-2 h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Service Categories */}
      <section className="py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">خدماتنا</h2>
            <p className="text-lg text-gray-600">نوفر مجموعة شاملة من خدمات الصيانة المنزلية</p>
          </div>
          
          {loading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {[...Array(6)].map((_, index) => (
                <Card key={index} className="animate-pulse">
                  <CardHeader>
                    <div className="h-12 w-12 bg-gray-200 rounded-lg mb-4"></div>
                    <div className="h-6 bg-gray-200 rounded w-3/4"></div>
                  </CardHeader>
                  <CardContent>
                    <div className="h-4 bg-gray-200 rounded w-full mb-2"></div>
                    <div className="h-4 bg-gray-200 rounded w-2/3"></div>
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {serviceCategories.map((category) => {
                const IconComponent = categoryIcons[category.name] || Wrench;
                return (
                  <Card key={category.id} className="hover:shadow-lg transition-shadow cursor-pointer group">
                    <CardHeader>
                      <div className="flex items-center justify-between">
                        <div className="p-3 bg-blue-100 rounded-lg group-hover:bg-blue-200 transition-colors">
                          <IconComponent className="h-8 w-8 text-blue-600" />
                        </div>
                        <Badge variant="secondary">{category.service_count} خدمة</Badge>
                      </div>
                      <CardTitle className="text-xl">{category.name}</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <CardDescription className="text-base">
                        {category.description}
                      </CardDescription>
                      <div className="mt-4 flex items-center text-sm text-blue-600">
                        <span>اطلب الآن</span>
                        <ArrowRight className="mr-2 h-4 w-4" />
                      </div>
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          )}
        </div>
      </section>

      {/* Features Section */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">لماذا تختارنا؟</h2>
            <p className="text-lg text-gray-600">نحن نضمن لك أفضل تجربة في خدمات الصيانة</p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, index) => (
              <div key={index} className="text-center">
                <div className="mx-auto w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mb-4">
                  <feature.icon className="h-8 w-8 text-blue-600" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">{feature.title}</h3>
                <p className="text-gray-600">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-16 bg-blue-600 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {stats.map((stat, index) => (
              <div key={index} className="text-center">
                <div className="text-4xl font-bold mb-2">{stat.number}</div>
                <div className="text-blue-200">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">كيف يعمل الأمر؟</h2>
            <p className="text-lg text-gray-600">احصل على خدمتك في 3 خطوات بسيطة</p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="mx-auto w-16 h-16 bg-blue-600 text-white rounded-full flex items-center justify-center mb-4 text-2xl font-bold">
                1
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">اختر الخدمة</h3>
              <p className="text-gray-600">حدد نوع الخدمة التي تحتاجها من قائمة خدماتنا المتنوعة</p>
            </div>
            
            <div className="text-center">
              <div className="mx-auto w-16 h-16 bg-blue-600 text-white rounded-full flex items-center justify-center mb-4 text-2xl font-bold">
                2
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">احجز موعد</h3>
              <p className="text-gray-600">اختر الفني المناسب والوقت الذي يناسبك</p>
            </div>
            
            <div className="text-center">
              <div className="mx-auto w-16 h-16 bg-blue-600 text-white rounded-full flex items-center justify-center mb-4 text-2xl font-bold">
                3
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">استمتع بالخدمة</h3>
              <p className="text-gray-600">سيصل الفني في الموعد المحدد لتقديم الخدمة بأعلى جودة</p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 bg-gradient-to-r from-blue-600 to-blue-800 text-white">
        <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold mb-4">جاهز لطلب خدمتك؟</h2>
          <p className="text-xl mb-8 text-blue-100">
            انضم إلى آلاف العملاء الراضين واحصل على أفضل خدمات الصيانة
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link to="/register">
              <Button size="lg" className="bg-white text-blue-600 hover:bg-gray-100">
                إنشاء حساب جديد
                <ArrowRight className="mr-2 h-5 w-5" />
              </Button>
            </Link>
            <Link to="/login">
              <Button size="lg" variant="outline" className="border-white text-white hover:bg-white hover:text-blue-600">
                تسجيل الدخول
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div>
              <h3 className="text-2xl font-bold mb-4">منصة الصيانة</h3>
              <p className="text-gray-400 mb-4">
                منصة رائدة في تقديم خدمات الصيانة المنزلية في مصر
              </p>
              <div className="flex space-x-4 space-x-reverse">
                <div className="flex items-center text-gray-400">
                  <Phone className="h-4 w-4 ml-2" />
                  <span>19999</span>
                </div>
              </div>
            </div>
            
            <div>
              <h4 className="text-lg font-semibold mb-4">الخدمات</h4>
              <ul className="space-y-2 text-gray-400">
                <li>السباكة</li>
                <li>الكهرباء</li>
                <li>التنظيف</li>
                <li>النجارة</li>
                <li>صيانة التكييف</li>
              </ul>
            </div>
            
            <div>
              <h4 className="text-lg font-semibold mb-4">الشركة</h4>
              <ul className="space-y-2 text-gray-400">
                <li>من نحن</li>
                <li>اتصل بنا</li>
                <li>الشروط والأحكام</li>
                <li>سياسة الخصوصية</li>
              </ul>
            </div>
            
            <div>
              <h4 className="text-lg font-semibold mb-4">للفنيين</h4>
              <ul className="space-y-2 text-gray-400">
                <li>انضم كفني</li>
                <li>متطلبات التسجيل</li>
                <li>دليل الفني</li>
                <li>الدعم الفني</li>
              </ul>
            </div>
          </div>
          
          <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400">
            <p>&copy; 2024 منصة الصيانة. جميع الحقوق محفوظة.</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;

