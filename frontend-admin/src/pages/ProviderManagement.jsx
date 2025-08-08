import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import {
  CheckCircle,
  XCircle,
  Clock,
  AlertTriangle,
  FileText,
  Download,
  Eye,
  Star,
  MapPin,
  Phone,
  Mail,
  Calendar,
  Wrench,
  ExternalLink,
} from 'lucide-react';

import { apiClient } from '../lib/api';
import { useEffect } from 'react';

const ProviderManagement = () => {
  const [providers, setProviders] = useState([]);
  const [selectedProvider, setSelectedProvider] = useState(null);
  const [showVerificationDialog, setShowVerificationDialog] = useState(false);
  const [showDocumentsDialog, setShowDocumentsDialog] = useState(false);
  const [providerDocuments, setProviderDocuments] = useState([]);
  const [verificationAction, setVerificationAction] = useState('');
  const [verificationNotes, setVerificationNotes] = useState('');
  const [providerDocuments, setProviderDocuments] = useState([]);
  const [reviewingDocument, setReviewingDocument] = useState(null);
  const [loading, setLoading] = useState(true);
  const [documentsLoading, setDocumentsLoading] = useState(false);
  const [error, setError] = useState(null);

  // Load providers data
  useEffect(() => {
    loadProviders();
  }, []);

  const loadProviders = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await apiClient.getProviders();
      
      // Ensure each provider has required properties with defaults
      const processedProviders = (response.providers || []).map(provider => ({
        ...provider,
        documents: provider.documents || [],
        services: provider.services || [],
        first_name: provider.first_name || '',
        last_name: provider.last_name || '',
        user: provider.user || null
      }));
      
      setProviders(processedProviders);
      
    } catch (error) {
      console.error('Failed to load providers:', error);
      setError('Failed to load providers');
      setProviders([]);
    } finally {
      setLoading(false);
    }
  };

  const loadProviderDocuments = async (providerId) => {
    try {
      setDocumentsLoading(true);
      const response = await apiClient.getProviderDocuments(providerId);
      setProviderDocuments(response.documents || []);
    } catch (error) {
      console.error('Failed to load provider documents:', error);
      setProviderDocuments([]);
    } finally {
      setDocumentsLoading(false);
    }
  };

  const viewProviderDocuments = async (provider) => {
    setSelectedProvider(provider);
    setShowDocumentsDialog(true);
    await loadProviderDocuments(provider.id);
  };

  const downloadDocument = async (documentUrl) => {
    try {
      // Create full URL for document
      const fullUrl = documentUrl.startsWith('/uploads') 
        ? `${apiClient.baseURL.replace('/api', '')}${documentUrl}`
        : documentUrl;
      
      // Open in new tab
      window.open(fullUrl, '_blank');
    } catch (error) {
      console.error('Failed to download document:', error);
    }
  };

  const reviewDocument = async (documentId, action) => {
    try {
      await apiClient.reviewDocument(documentId, action);
      
      // Reload documents for the current provider
      if (selectedProvider) {
        await loadProviderDocuments(selectedProvider.id);
      }
      
      // Also reload providers to update the main list
      await loadProviders();
    } catch (error) {
      console.error('Failed to review document:', error);
      setError('Failed to review document');
    }
  };

  const getStatusBadge = (status) => {
    const statusConfig = {
      approved: { 
        label: 'Verified', 
        variant: 'default', 
        icon: CheckCircle,
        color: 'text-green-600'
      },
      pending: { 
        label: 'Pending', 
        variant: 'secondary', 
        icon: Clock,
        color: 'text-yellow-600'
      },
      rejected: { 
        label: 'Rejected', 
        variant: 'destructive', 
        icon: XCircle,
        color: 'text-red-600'
      },
    };

    const config = statusConfig[status] || statusConfig.pending;
    const Icon = config.icon;

    return (
      <Badge variant={config.variant} className="flex items-center gap-1">
        <Icon className="w-3 h-3" />
        {config.label}
      </Badge>
    );
  };

  const getDocumentStatus = (doc) => {
    // More robust document validation
    if (!doc || !doc.document_url || doc.document_url.trim() === '') {
      return { status: 'missing', color: 'text-red-500', icon: XCircle };
    }
    
    // Check if document_url is just a placeholder or empty
    if (doc.document_url === '#' || doc.document_url === '' || doc.document_url === null) {
      return { status: 'missing', color: 'text-red-500', icon: XCircle };
    }
    
    if (doc.verification_status === 'approved') return { status: 'verified', color: 'text-green-500', icon: CheckCircle };
    if (doc.verification_status === 'rejected') return { status: 'rejected', color: 'text-red-500', icon: XCircle };
    return { status: 'pending', color: 'text-yellow-500', icon: Clock };
  };

  const handleVerificationAction = async (provider, action) => {
    setSelectedProvider(provider);
    setVerificationAction(action);
    setVerificationNotes('');
    
    // Load provider documents
    await loadProviderDocuments(provider.id);
    setShowVerificationDialog(true);
  };

<<<<<<< HEAD
  const loadProviderDocuments = async (providerId) => {
    try {
      const response = await apiClient.getProviderDocuments(providerId);
      setProviderDocuments(response.documents || []);
    } catch (error) {
      console.error('Failed to load provider documents:', error);
      setProviderDocuments([]);
    }
  };

  const handleDocumentReview = async (document, action, reason = null) => {
    try {
      await apiClient.reviewDocument(document.id, action, reason);
      // Reload documents for this provider
      await loadProviderDocuments(selectedProvider.id);
    } catch (error) {
      console.error('Failed to review document:', error);
      setError('Failed to review document');
    }
  };

  const submitVerification = async () => {
    if (!selectedProvider || !verificationAction) return;
    
    try {
      await apiClient.updateProviderVerification(selectedProvider.id, {
        verification_status: verificationAction,
        rejection_reason: verificationAction === 'rejected' ? verificationNotes : undefined
      });
      
      // Reload providers to get updated data from server
      await loadProviders();
      
      // Reset form
      setShowVerificationDialog(false);
      setSelectedProvider(null);
      setVerificationAction('');
      setVerificationNotes('');
      setProviderDocuments([]);
      
    } catch (error) {
      console.error('Failed to update verification:', error);
      setError('Failed to update provider verification');
=======
  const submitVerification = async () => {
    if (!selectedProvider) return;

    try {
      await apiClient.updateProviderVerificationStatus(selectedProvider.id, verificationAction, verificationNotes);
      setProviders(providers.map(p => 
        p.id === selectedProvider.id 
          ? { 
              ...p, 
              verification_status: verificationAction,
              ...(verificationAction === 'rejected' && { rejection_reason: verificationNotes })
            }
          : p
      ));
      setShowVerificationDialog(false);
      setVerificationNotes('');
      setSelectedProvider(null);
    } catch (error) {
      console.error('Failed to submit verification:', error);
      setError('Failed to update verification status');
>>>>>>> 4332b38f1c42420a4d78df3da88b3598b0db096f
    }
  };

  const pendingProviders = providers.filter(p => p.verification_status === 'pending');
  const verifiedProviders = providers.filter(p => p.verification_status === 'approved');
  const rejectedProviders = providers.filter(p => p.verification_status === 'rejected');

  const ProviderCard = ({ provider, showActions = true }) => (
    <Card className="mb-4">
      <CardContent className="p-6">
        <div className="flex items-start justify-between">
          <div className="flex items-start space-x-4">
            <Avatar className="h-12 w-12">
              <AvatarImage src={provider.avatar} alt={provider.name} />
              <AvatarFallback>
                {(provider.first_name && provider.last_name) ? 
                  `${provider.first_name[0]}${provider.last_name[0]}` : 
                  'SP'
                }
              </AvatarFallback>
            </Avatar>
            <div className="flex-1">
              <div className="flex items-center space-x-2 mb-2">
                <h3 className="text-lg font-semibold">{provider.first_name} {provider.last_name}</h3>
                {getStatusBadge(provider.verification_status)}
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm text-muted-foreground mb-3">
                <div className="flex items-center">
                  <Mail className="mr-2 h-4 w-4" />
                  {provider.user?.email || 'N/A'}
                </div>
                <div className="flex items-center">
                  <Phone className="mr-2 h-4 w-4" />
                  {provider.user?.phone || 'N/A'}
                </div>
                <div className="flex items-center">
                  <MapPin className="mr-2 h-4 w-4" />
                  {provider.business_name || 'N/A'}
                </div>
                <div className="flex items-center">
                  <Calendar className="mr-2 h-4 w-4" />
                  Joined {provider.created_at ? new Date(provider.created_at).toLocaleDateString() : 'N/A'}
                </div>
              </div>

              <div className="flex items-center space-x-4 mb-3">
                <div className="flex items-center">
                  <Star className="mr-1 h-4 w-4 text-yellow-500" />
                  <span className="font-medium">{provider.average_rating || 0}</span>
                </div>
                <div className="text-sm text-muted-foreground">
                  {provider.total_completed_jobs || 0} jobs completed
                </div>
              </div>

              <div className="flex flex-wrap gap-1 mb-3">
                {(provider.services || []).map((service, index) => (
                  <Badge key={index} variant="outline" className="text-xs">
                    <Wrench className="mr-1 h-3 w-3" />
                    {service.name || service}
                  </Badge>
                ))}
              </div>

              {/* Document Status */}
              <div className="flex items-center justify-between mb-3">
                <div className="grid grid-cols-3 gap-4 text-xs flex-1">
                  {provider.documents && provider.documents.length > 0 ? (
                    (() => {
                      // Filter out documents with invalid URLs
                      const validDocuments = provider.documents.filter(doc => {
                        const status = getDocumentStatus(doc);
                        return status.status !== 'missing';
                      });
                      
                      if (validDocuments.length === 0) {
                        return (
                          <div className="col-span-3 text-muted-foreground">
                            No valid documents uploaded
                          </div>
                        );
                      }
                      
                      return validDocuments.map((doc, index) => {
                        const status = getDocumentStatus(doc);
                        const Icon = status.icon;
                        return (
                          <div key={index} className="flex items-center">
                            <Icon className={`mr-1 h-3 w-3 ${status.color}`} />
                            <span className="capitalize">
                              {doc.document_type === 'background_check' ? 'Background Check' : doc.document_type}
                            </span>
                          </div>
                        );
                      });
                    })()
                  ) : (
                    <div className="col-span-3 text-muted-foreground">
                      No documents uploaded
                    </div>
                  )}
                </div>
                {(() => {
                  // Only show View Docs button if there are valid documents
                  const validDocuments = provider.documents?.filter(doc => {
                    const status = getDocumentStatus(doc);
                    return status.status !== 'missing';
                  }) || [];
                  
                  return validDocuments.length > 0 && (
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => viewProviderDocuments(provider)}
                      className="ml-4"
                    >
                      <Eye className="mr-1 h-3 w-3" />
                      View Docs ({validDocuments.length})
                    </Button>
                  );
                })()}
              </div>

              {provider.rejection_reason && (
                <div className="mt-3 p-2 bg-red-50 border border-red-200 rounded text-sm text-red-700">
                  <AlertTriangle className="inline mr-1 h-4 w-4" />
                  {provider.rejection_reason}
                </div>
              )}
            </div>
          </div>

          {showActions && provider.verification_status === 'pending' && (
            <div className="flex space-x-2">
              <Button
                size="sm"
                onClick={() => handleVerificationAction(provider, 'approved')}
                className="bg-green-600 hover:bg-green-700"
              >
                <CheckCircle className="mr-1 h-4 w-4" />
                Approve
              </Button>
              <Button
                size="sm"
                variant="destructive"
                onClick={() => handleVerificationAction(provider, 'rejected')}
              >
                <XCircle className="mr-1 h-4 w-4" />
                Reject
              </Button>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Provider Management</h1>
          <p className="text-muted-foreground">
            Manage and verify service providers on your platform
          </p>
        </div>
        <Button variant="outline">
          <Download className="mr-2 h-4 w-4" />
          Export Report
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Providers</CardTitle>
            <CheckCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{providers.length}</div>
            <p className="text-xs text-muted-foreground">
              Total registered providers
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Pending Verification</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{pendingProviders.length}</div>
            <p className="text-xs text-muted-foreground">
              Awaiting review
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Verified</CardTitle>
            <CheckCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{verifiedProviders.length}</div>
            <p className="text-xs text-muted-foreground">
              Active providers
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Rejected</CardTitle>
            <XCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{rejectedProviders.length}</div>
            <p className="text-xs text-muted-foreground">
              Need attention
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Provider Tabs */}
      <Tabs defaultValue="pending" className="space-y-4">
        <TabsList>
          <TabsTrigger value="pending" className="relative">
            Pending Verification
            {pendingProviders.length > 0 && (
              <Badge className="ml-2 h-5 w-5 rounded-full p-0 text-xs">
                {pendingProviders.length}
              </Badge>
            )}
          </TabsTrigger>
          <TabsTrigger value="verified">Verified Providers</TabsTrigger>
          <TabsTrigger value="rejected">Rejected Applications</TabsTrigger>
        </TabsList>

        <TabsContent value="pending" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Pending Verifications</CardTitle>
              <CardDescription>
                Service providers awaiting verification approval
              </CardDescription>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="text-center py-8">
                  <p className="text-muted-foreground">Loading providers...</p>
                </div>
              ) : error ? (
                <div className="text-center py-8">
                  <p className="text-red-600">{error}</p>
                  <Button onClick={loadProviders} className="mt-2">Try Again</Button>
                </div>
              ) : pendingProviders.length === 0 ? (
                <div className="text-center py-8">
                  <Clock className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                  <p className="text-muted-foreground">No pending verifications</p>
                  <p className="text-sm text-muted-foreground">New provider applications will appear here</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {pendingProviders.map(provider => (
                    <ProviderCard key={provider.id} provider={provider} />
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="verified" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Verified Providers</CardTitle>
              <CardDescription>
                Successfully verified and active service providers
              </CardDescription>
            </CardHeader>
            <CardContent>
              {verifiedProviders.length === 0 ? (
                <div className="text-center py-8">
                  <CheckCircle className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                  <p className="text-muted-foreground">No verified providers</p>
                  <p className="text-sm text-muted-foreground">Approved providers will appear here</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {verifiedProviders.map(provider => (
                    <ProviderCard key={provider.id} provider={provider} showActions={false} />
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="rejected" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Rejected Applications</CardTitle>
              <CardDescription>
                Provider applications that were rejected and need attention
              </CardDescription>
            </CardHeader>
            <CardContent>
              {rejectedProviders.length === 0 ? (
                <div className="text-center py-8">
                  <XCircle className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                  <p className="text-muted-foreground">No rejected applications</p>
                  <p className="text-sm text-muted-foreground">Rejected provider applications will appear here</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {rejectedProviders.map(provider => (
                    <ProviderCard key={provider.id} provider={provider} showActions={false} />
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Verification Dialog */}
      <Dialog open={showVerificationDialog} onOpenChange={setShowVerificationDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {verificationAction === 'approved' ? 'Approve' : 'Reject'} Provider
            </DialogTitle>
            <DialogDescription>
              {verificationAction === 'approved' 
                ? 'Are you sure you want to approve this provider? They will be able to accept bookings. Please ensure all required documents are uploaded and verified.'
                : 'Please provide a reason for rejecting this provider application.'
              }
            </DialogDescription>
          </DialogHeader>
          
          {selectedProvider && (
            <div className="space-y-4">
              <div className="space-y-3">
                <div className="flex items-center space-x-3">
                  <Avatar>
                    <AvatarImage src={selectedProvider.avatar} alt={selectedProvider.name} />
                    <AvatarFallback>
                      {(selectedProvider.first_name && selectedProvider.last_name) ? 
                        `${selectedProvider.first_name[0]}${selectedProvider.last_name[0]}` : 
                        'SP'
                      }
                    </AvatarFallback>
                  </Avatar>
                  <div>
                    <h4 className="font-medium">{selectedProvider.first_name} {selectedProvider.last_name}</h4>
                    <p className="text-sm text-muted-foreground">{selectedProvider.user?.email}</p>
                  </div>
                </div>
                
                {/* Document Status Summary */}
                {verificationAction === 'approved' && (
                  <div className="p-3 bg-gray-50 rounded-lg">
                    <h5 className="text-sm font-medium mb-2">Document Status:</h5>
                    <div className="space-y-1 text-xs">
                      {(() => {
                        const validDocuments = selectedProvider.documents?.filter(doc => {
                          const status = getDocumentStatus(doc);
                          return status.status !== 'missing';
                        }) || [];
                        
                        const requiredDocs = ['national_id', 'certificate', 'background_check'];
                        const approvedDocs = validDocuments.filter(doc => doc.verification_status === 'approved');
                        
                        return (
                          <div>
                            <p className="text-muted-foreground">
                              Valid Documents: {validDocuments.length} | Approved: {approvedDocs.length} | Required: {requiredDocs.length}
                            </p>
                            {approvedDocs.length < requiredDocs.length && (
                              <p className="text-red-600 font-medium">
                                ⚠️ Not all required documents are approved
                              </p>
                            )}
                          </div>
                        );
                      })()}
                    </div>
                  </div>
                )}
              </div>

              {verificationAction === 'rejected' && (
                <div className="space-y-2">
                  <Label htmlFor="rejection-reason">Rejection Reason</Label>
                  <Textarea
                    id="rejection-reason"
                    placeholder="Please explain why this application is being rejected..."
                    value={verificationNotes}
                    onChange={(e) => setVerificationNotes(e.target.value)}
                  />
                </div>
              )}
            </div>
          )}

          <DialogFooter>
            <Button variant="outline" onClick={() => setShowVerificationDialog(false)}>
              Cancel
            </Button>
            <Button
              onClick={submitVerification}
              className={verificationAction === 'approved' ? 'bg-green-600 hover:bg-green-700' : ''}
              variant={verificationAction === 'rejected' ? 'destructive' : 'default'}
              disabled={verificationAction === 'rejected' && !verificationNotes.trim()}
            >
              {verificationAction === 'approved' ? 'Approve Provider' : 'Reject Application'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Documents Dialog */}
      <Dialog open={showDocumentsDialog} onOpenChange={setShowDocumentsDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {selectedProvider ? `${selectedProvider.first_name} ${selectedProvider.last_name}'s Documents` : 'Provider Documents'}
            </DialogTitle>
            <DialogDescription>
              View and download documents for this provider.
            </DialogDescription>
          </DialogHeader>
                     <div className="space-y-4">
             {documentsLoading ? (
               <div className="text-center py-8">
                 <p className="text-muted-foreground">Loading documents...</p>
               </div>
             ) : providerDocuments.length === 0 ? (
               <div className="text-center py-8">
                 <FileText className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                 <p className="text-muted-foreground">No documents uploaded for this provider.</p>
               </div>
             ) : (
               <div className="space-y-4">
                 {providerDocuments.map((doc, index) => {
                   const status = getDocumentStatus(doc);
                   const StatusIcon = status.icon;
                   return (
                     <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                       <div className="flex items-center">
                         <FileText className="mr-2 h-5 w-5 text-blue-500" />
                         <div>
                           <span className="font-medium capitalize">
                             {doc.document_type === 'background_check' ? 'Background Check' : doc.document_type}
                           </span>
                           <div className="flex items-center mt-1">
                             <StatusIcon className={`mr-1 h-3 w-3 ${status.color}`} />
                             <span className="text-sm text-muted-foreground capitalize">{doc.verification_status}</span>
                           </div>
                         </div>
                       </div>
                       <div className="flex items-center space-x-2">
                                                 <Button
                          size="sm"
                          variant="outline"
                          onClick={() => downloadDocument(doc.document_url)}
                          disabled={!doc.document_url || doc.document_url === '#' || doc.document_url.trim() === ''}
                        >
                          <Download className="mr-1 h-4 w-4" />
                          {(!doc.document_url || doc.document_url === '#' || doc.document_url.trim() === '') ? 'No File' : 'View'}
                        </Button>
                         {doc.verification_status === 'pending' && (
                           <div className="flex space-x-1">
                             <Button
                               size="sm"
                               onClick={() => reviewDocument(doc.id, 'approve')}
                               className="bg-green-600 hover:bg-green-700"
                             >
                               <CheckCircle className="h-4 w-4" />
                             </Button>
                             <Button
                               size="sm"
                               variant="destructive"
                               onClick={() => reviewDocument(doc.id, 'reject')}
                             >
                               <XCircle className="h-4 w-4" />
                             </Button>
                           </div>
                         )}
                       </div>
                     </div>
                   );
                 })}
               </div>
             )}
           </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowDocumentsDialog(false)}>
              Close
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default ProviderManagement;

