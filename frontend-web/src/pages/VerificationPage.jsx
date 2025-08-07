import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { 
  FileText,
  Upload,
  CheckCircle,
  XCircle,
  Clock,
  AlertCircle,
  Camera,
  Download,
  Eye
} from 'lucide-react';
import { useAuth } from '../lib/auth.jsx';
import { apiClient } from '../lib/api';

const VerificationPage = () => {
  const { user } = useAuth();
  const [profile, setProfile] = useState(null);
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploadingDoc, setUploadingDoc] = useState(null);
  const [selectedDocType, setSelectedDocType] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);

  useEffect(() => {
    loadVerificationData();
  }, []);

  const loadVerificationData = async () => {
    try {
      const profileResponse = await apiClient.getProviderProfile();
      setProfile(profileResponse.profile);
      setDocuments(profileResponse.documents || []);
    } catch (error) {
      console.error('Failed to load verification data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      // Validate file type and size
      const allowedTypes = ['image/jpeg', 'image/png', 'application/pdf'];
      const maxSize = 5 * 1024 * 1024; // 5MB

      if (!allowedTypes.includes(file.type)) {
        alert('يرجى اختيار ملف صورة (JPEG, PNG) أو PDF فقط');
        return;
      }

      if (file.size > maxSize) {
        alert('يجب أن يكون حجم الملف أقل من 5 ميجابايت');
        return;
      }

      setSelectedFile(file);
    }
  };

  const handleUploadDocument = async () => {
    if (!selectedFile || !selectedDocType) {
      alert('يرجى اختيار نوع الوثيقة والملف');
      return;
    }

    setUploadingDoc(selectedDocType);
    
    try {
      // Create FormData for file upload
      const formData = new FormData();
      formData.append('document', selectedFile);
      formData.append('document_type', selectedDocType);

      // Upload using the API client
      await apiClient.uploadProviderDocument(formData);
      
      // Reload verification data
      await loadVerificationData();
      
      // Reset form
      setSelectedFile(null);
      setSelectedDocType('');
      document.getElementById('file-input').value = '';
      
      alert('تم رفع الوثيقة بنجاح! ستتم مراجعتها من قبل الإدارة خلال 24-48 ساعة.');
    } catch (error) {
      console.error('Failed to upload document:', error);
      alert('حدث خطأ أثناء رفع الوثيقة: ' + error.message);
    } finally {
      setUploadingDoc(null);
    }
  };

  const getVerificationStatusBadge = (status) => {
    const configs = {
      pending: { color: 'bg-yellow-100 text-yellow-800', text: 'قيد المراجعة', icon: Clock },
      approved: { color: 'bg-green-100 text-green-800', text: 'موافق عليها', icon: CheckCircle },
      rejected: { color: 'bg-red-100 text-red-800', text: 'مرفوضة', icon: XCircle }
    };
    
    const config = configs[status] || configs.pending;
    const Icon = config.icon;
    
    return (
      <Badge className={config.color}>
        <Icon className="w-3 h-3 mr-1" />
        {config.text}
      </Badge>
    );
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

  const documentTypes = [
    { value: 'national_id', label: 'البطاقة الشخصية', required: true },
    { value: 'certificate', label: 'شهادة مهنية', required: true },
    { value: 'license', label: 'رخصة مزاولة المهنة', required: false },
    { value: 'insurance', label: 'بوليصة التأمين', required: false },
    { value: 'background_check', label: 'فحص السجل الجنائي', required: true }
  ];

  const getRequiredDocuments = () => documentTypes.filter(doc => doc.required);
  const getUploadedDocuments = () => documents.map(doc => doc.document_type);
  const getMissingRequiredDocs = () => 
    getRequiredDocuments().filter(doc => !getUploadedDocuments().includes(doc.value));

  const calculateVerificationProgress = () => {
    const requiredDocs = getRequiredDocuments();
    const uploadedRequiredDocs = documents.filter(doc => 
      requiredDocs.some(req => req.value === doc.document_type)
    );
    const approvedRequiredDocs = uploadedRequiredDocs.filter(doc => 
      doc.verification_status === 'approved'
    );
    
    return {
      uploaded: (uploadedRequiredDocs.length / requiredDocs.length) * 100,
      approved: (approvedRequiredDocs.length / requiredDocs.length) * 100
    };
  };

  const progress = calculateVerificationProgress();
  const isFullyVerified = progress.approved === 100;
  const missingDocs = getMissingRequiredDocs();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div className="text-center">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">التحقق من الهوية</h1>
          <p className="text-gray-600">
            اكمل عملية التحقق لتتمكن من تلقي طلبات الخدمة
          </p>
        </div>

        {/* Verification Status Overview */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <FileText className="mr-2 h-5 w-5" />
              حالة التحقق العامة
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span>حالة الحساب:</span>
                {getVerificationStatusBadge(profile?.verification_status || 'pending')}
              </div>
              
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>الوثائق المرفوعة</span>
                  <span>{Math.round(progress.uploaded)}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-blue-600 h-2 rounded-full" 
                    style={{ width: `${progress.uploaded}%` }}
                  ></div>
                </div>
              </div>
              
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>الوثائق المعتمدة</span>
                  <span>{Math.round(progress.approved)}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-green-600 h-2 rounded-full" 
                    style={{ width: `${progress.approved}%` }}
                  ></div>
                </div>
              </div>

              {isFullyVerified && (
                <Alert>
                  <CheckCircle className="h-4 w-4" />
                  <AlertDescription>
                    تهانينا! تم التحقق من جميع الوثائق المطلوبة. يمكنك الآن تلقي طلبات الخدمة.
                  </AlertDescription>
                </Alert>
              )}

              {missingDocs.length > 0 && (
                <Alert>
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription>
                    يجب رفع الوثائق التالية لإكمال عملية التحقق: {missingDocs.map(doc => doc.label).join('، ')}
                  </AlertDescription>
                </Alert>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Upload New Document */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Upload className="mr-2 h-5 w-5" />
              رفع وثيقة جديدة
            </CardTitle>
            <CardDescription>
              اختر نوع الوثيقة ثم ارفع ملف صورة واضحة أو PDF
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="doc-type">نوع الوثيقة</Label>
                <Select value={selectedDocType} onValueChange={setSelectedDocType}>
                  <SelectTrigger>
                    <SelectValue placeholder="اختر نوع الوثيقة" />
                  </SelectTrigger>
                  <SelectContent>
                    {documentTypes.map((type) => (
                      <SelectItem key={type.value} value={type.value}>
                        {type.label} {type.required && '*'}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="file-input">ملف الوثيقة</Label>
                <Input
                  id="file-input"
                  type="file"
                  accept="image/*,.pdf"
                  onChange={handleFileSelect}
                  className="cursor-pointer"
                />
              </div>
            </div>

            {selectedFile && (
              <Alert>
                <Camera className="h-4 w-4" />
                <AlertDescription>
                  تم اختيار الملف: {selectedFile.name} ({(selectedFile.size / 1024 / 1024).toFixed(2)} MB)
                </AlertDescription>
              </Alert>
            )}

            <Button
              onClick={handleUploadDocument}
              disabled={!selectedFile || !selectedDocType || uploadingDoc}
              className="w-full"
            >
              {uploadingDoc ? (
                <>
                  <Clock className="mr-2 h-4 w-4 animate-spin" />
                  جاري الرفع...
                </>
              ) : (
                <>
                  <Upload className="mr-2 h-4 w-4" />
                  رفع الوثيقة
                </>
              )}
            </Button>
          </CardContent>
        </Card>

        {/* Uploaded Documents */}
        <Card>
          <CardHeader>
            <CardTitle>الوثائق المرفوعة</CardTitle>
            <CardDescription>
              قائمة بجميع الوثائق التي تم رفعها وحالة التحقق منها
            </CardDescription>
          </CardHeader>
          <CardContent>
            {documents.length === 0 ? (
              <div className="text-center py-8">
                <FileText className="mx-auto h-12 w-12 text-gray-400 mb-4" />
                <p className="text-gray-500">لم يتم رفع أي وثائق بعد</p>
              </div>
            ) : (
              <div className="space-y-4">
                {documents.map((document) => (
                  <div key={document.id} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex items-center space-x-4 space-x-reverse">
                      <FileText className="h-8 w-8 text-blue-600" />
                      <div>
                        <h3 className="font-medium">{getDocumentTypeText(document.document_type)}</h3>
                        <p className="text-sm text-gray-500">
                          تم الرفع في {new Date(document.created_at).toLocaleDateString('ar-EG')}
                        </p>
                        {document.rejection_reason && (
                          <p className="text-sm text-red-600 mt-1">
                            سبب الرفض: {document.rejection_reason}
                          </p>
                        )}
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-2 space-x-reverse">
                      {getVerificationStatusBadge(document.verification_status)}
                      <Button variant="outline" size="sm" asChild>
                        <a href={document.document_url} target="_blank" rel="noopener noreferrer">
                          <Eye className="h-4 w-4" />
                        </a>
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Requirements Guide */}
        <Card>
          <CardHeader>
            <CardTitle>متطلبات الوثائق</CardTitle>
            <CardDescription>
              تأكد من أن الوثائق تستوفي المتطلبات التالية
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-3">
                <h4 className="font-medium">الوثائق المطلوبة:</h4>
                <ul className="space-y-2 text-sm">
                  {getRequiredDocuments().map((doc) => (
                    <li key={doc.value} className="flex items-center">
                      <CheckCircle className="h-4 w-4 text-green-600 mr-2" />
                      {doc.label}
                    </li>
                  ))}
                </ul>
              </div>
              
              <div className="space-y-3">
                <h4 className="font-medium">شروط جودة الصورة:</h4>
                <ul className="space-y-2 text-sm text-gray-600">
                  <li>• صورة واضحة وغير مشوشة</li>
                  <li>• إضاءة جيدة وبدون ظلال</li>
                  <li>• جميع النصوص مقروءة</li>
                  <li>• حجم الملف أقل من 5 ميجابايت</li>
                  <li>• تنسيق JPEG, PNG, أو PDF</li>
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default VerificationPage;