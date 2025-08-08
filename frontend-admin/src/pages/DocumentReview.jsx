import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { 
  FileText,
  CheckCircle,
  XCircle,
  Clock,
  Eye,
  User,
  Mail,
  Calendar,
  AlertTriangle
} from 'lucide-react';
import { apiClient } from '../lib/api';

const DocumentReview = () => {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedDocument, setSelectedDocument] = useState(null);
  const [reviewAction, setReviewAction] = useState('');
  const [rejectionReason, setRejectionReason] = useState('');
  const [reviewing, setReviewing] = useState(false);
  const [showReviewDialog, setShowReviewDialog] = useState(false);
  const [activeTab, setActiveTab] = useState('pending');

  useEffect(() => {
    loadDocuments();
  }, [activeTab]);

  const loadDocuments = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await apiClient.getPendingDocuments({ 
        status: activeTab,
        per_page: 50 
      });
      setDocuments(response.documents || []);
      
    } catch (error) {
      console.error('Failed to load documents:', error);
      setError('Failed to load documents');
      setDocuments([]);
    } finally {
      setLoading(false);
    }
  };

  const handleReviewDocument = async () => {
    if (!selectedDocument || !reviewAction) return;
    
    setReviewing(true);
    try {
      await apiClient.reviewDocument(
        selectedDocument.id, 
        reviewAction, 
        reviewAction === 'reject' ? rejectionReason : null
      );
      
      // Reload documents
      await loadDocuments();
      
      // Close dialog
      setShowReviewDialog(false);
      setSelectedDocument(null);
      setReviewAction('');
      setRejectionReason('');
      
    } catch (error) {
      console.error('Failed to review document:', error);
      setError('Failed to review document');
    } finally {
      setReviewing(false);
    }
  };

  const getDocumentStatusBadge = (status) => {
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

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('ar-EG', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const openReviewDialog = (document, action) => {
    setSelectedDocument(document);
    setReviewAction(action);
    setRejectionReason('');
    setShowReviewDialog(true);
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">مراجعة الوثائق</h1>
          <p className="text-gray-600">مراجعة وثائق مقدمي الخدمة للتحقق من صحتها</p>
        </div>
      </div>

      {error && (
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="pending">قيد المراجعة</TabsTrigger>
          <TabsTrigger value="approved">معتمدة</TabsTrigger>
          <TabsTrigger value="rejected">مرفوضة</TabsTrigger>
        </TabsList>

        <TabsContent value="pending" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Clock className="h-5 w-5" />
                الوثائق قيد المراجعة ({documents.length})
              </CardTitle>
              <CardDescription>
                الوثائق التي تحتاج إلى مراجعة وموافقة
              </CardDescription>
            </CardHeader>
            <CardContent>
              {documents.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  لا توجد وثائق قيد المراجعة
                </div>
              ) : (
                <div className="space-y-4">
                  {documents.map((document) => (
                    <div key={document.id} className="border rounded-lg p-4">
                      <div className="flex items-start justify-between mb-4">
                        <div className="flex-1">
                          <h4 className="font-medium mb-2">{getDocumentTypeText(document.document_type)}</h4>
                          
                          <div className="flex items-center gap-4 text-sm text-gray-600 mb-2">
                            <div className="flex items-center gap-1">
                              <User className="h-4 w-4" />
                              {document.provider?.first_name} {document.provider?.last_name}
                            </div>
                            <div className="flex items-center gap-1">
                              <Mail className="h-4 w-4" />
                              {document.provider?.email}
                            </div>
                            <div className="flex items-center gap-1">
                              <Calendar className="h-4 w-4" />
                              {formatDate(document.created_at)}
                            </div>
                          </div>
                          
                          {getDocumentStatusBadge(document.verification_status)}
                        </div>
                        
                        <div className="flex items-center gap-2 ml-4">
                          <Dialog>
                            <DialogTrigger asChild>
                              <Button variant="outline" size="sm">
                                <Eye className="h-4 w-4 mr-2" />
                                عرض الوثيقة
                              </Button>
                            </DialogTrigger>
                            <DialogContent className="max-w-4xl">
                              <DialogHeader>
                                <DialogTitle>{getDocumentTypeText(document.document_type)}</DialogTitle>
                                <DialogDescription>
                                  وثيقة من: {document.provider?.first_name} {document.provider?.last_name}
                                </DialogDescription>
                              </DialogHeader>
                              <div className="mt-4">
                                <img 
                                  src={document.document_url.startsWith('/') 
                                    ? `https://maintenance-platform-backend.onrender.com${document.document_url}` 
                                    : document.document_url
                                  } 
                                  alt={getDocumentTypeText(document.document_type)}
                                  className="max-w-full h-auto border rounded"
                                  onError={(e) => {
                                    e.target.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZGRkIi8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIxNCIgZmlsbD0iIzk5OSIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPkltYWdlIG5vdCBhdmFpbGFibGU8L3RleHQ+PC9zdmc+';
                                  }}
                                />
                              </div>
                            </DialogContent>
                          </Dialog>
                          
                          <Button 
                            variant="outline" 
                            size="sm"
                            className="text-green-600 border-green-600 hover:bg-green-50"
                            onClick={() => openReviewDialog(document, 'approve')}
                          >
                            <CheckCircle className="h-4 w-4 mr-2" />
                            قبول
                          </Button>
                          
                          <Button 
                            variant="outline" 
                            size="sm"
                            className="text-red-600 border-red-600 hover:bg-red-50"
                            onClick={() => openReviewDialog(document, 'reject')}
                          >
                            <XCircle className="h-4 w-4 mr-2" />
                            رفض
                          </Button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="approved" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <CheckCircle className="h-5 w-5 text-green-600" />
                الوثائق المعتمدة ({documents.length})
              </CardTitle>
            </CardHeader>
            <CardContent>
              {documents.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  لا توجد وثائق معتمدة
                </div>
              ) : (
                <div className="space-y-4">
                  {documents.map((document) => (
                    <div key={document.id} className="border rounded-lg p-4">
                      <div className="flex items-center justify-between">
                        <div>
                          <h4 className="font-medium">{getDocumentTypeText(document.document_type)}</h4>
                          <p className="text-sm text-gray-600">
                            {document.provider?.first_name} {document.provider?.last_name} - {formatDate(document.verified_at)}
                          </p>
                        </div>
                        {getDocumentStatusBadge(document.verification_status)}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="rejected" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <XCircle className="h-5 w-5 text-red-600" />
                الوثائق المرفوضة ({documents.length})
              </CardTitle>
            </CardHeader>
            <CardContent>
              {documents.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  لا توجد وثائق مرفوضة
                </div>
              ) : (
                <div className="space-y-4">
                  {documents.map((document) => (
                    <div key={document.id} className="border rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <div>
                          <h4 className="font-medium">{getDocumentTypeText(document.document_type)}</h4>
                          <p className="text-sm text-gray-600">
                            {document.provider?.first_name} {document.provider?.last_name} - {formatDate(document.verified_at)}
                          </p>
                        </div>
                        {getDocumentStatusBadge(document.verification_status)}
                      </div>
                      
                      {document.rejection_reason && (
                        <div className="mt-3 p-2 bg-red-50 border border-red-200 rounded text-sm text-red-700">
                          <AlertTriangle className="inline mr-1 h-4 w-4" />
                          سبب الرفض: {document.rejection_reason}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Review Dialog */}
      <Dialog open={showReviewDialog} onOpenChange={setShowReviewDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {reviewAction === 'approve' ? 'قبول الوثيقة' : 'رفض الوثيقة'}
            </DialogTitle>
            <DialogDescription>
              {selectedDocument && `${getDocumentTypeText(selectedDocument.document_type)} - ${selectedDocument.provider?.first_name} ${selectedDocument.provider?.last_name}`}
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4">
            {reviewAction === 'reject' && (
              <div>
                <Label htmlFor="rejection-reason">سبب الرفض</Label>
                <Textarea
                  id="rejection-reason"
                  value={rejectionReason}
                  onChange={(e) => setRejectionReason(e.target.value)}
                  placeholder="اكتب سبب رفض الوثيقة..."
                  rows={3}
                />
              </div>
            )}
            
            <div className="flex justify-end space-x-2 space-x-reverse">
              <Button 
                variant="outline" 
                onClick={() => setShowReviewDialog(false)}
                disabled={reviewing}
              >
                إلغاء
              </Button>
              <Button 
                onClick={handleReviewDocument}
                disabled={reviewing || (reviewAction === 'reject' && !rejectionReason.trim())}
                className={reviewAction === 'approve' ? 'bg-green-600 hover:bg-green-700' : 'bg-red-600 hover:bg-red-700'}
              >
                {reviewing ? 'جاري المراجعة...' : (reviewAction === 'approve' ? 'قبول الوثيقة' : 'رفض الوثيقة')}
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default DocumentReview;