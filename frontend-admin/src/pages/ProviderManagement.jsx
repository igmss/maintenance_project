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
} from 'lucide-react';

import { apiClient } from '../lib/api';
import { useEffect } from 'react';

const ProviderManagement = () => {
  const [providers, setProviders] = useState([]);
  const [selectedProvider, setSelectedProvider] = useState(null);
  const [showVerificationDialog, setShowVerificationDialog] = useState(false);
  const [verificationAction, setVerificationAction] = useState('');
  const [verificationNotes, setVerificationNotes] = useState('');
  const [providerDocuments, setProviderDocuments] = useState([]);
  const [reviewingDocument, setReviewingDocument] = useState(null);
  const [loading, setLoading] = useState(true);
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
        documents: provider.documents || {},
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
    if (!doc.uploaded) return { status: 'missing', color: 'text-red-500', icon: XCircle };
    if (doc.verified) return { status: 'verified', color: 'text-green-500', icon: CheckCircle };
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
              <div className="grid grid-cols-3 gap-4 text-xs">
                {provider.documents && Object.entries(provider.documents).map(([docType, doc]) => {
                  const status = getDocumentStatus(doc);
                  const Icon = status.icon;
                  return (
                    <div key={docType} className="flex items-center">
                      <Icon className={`mr-1 h-3 w-3 ${status.color}`} />
                      <span className="capitalize">
                        {docType === 'criminalRecord' ? 'Criminal Record' : docType}
                      </span>
                    </div>
                  );
                })}
                {(!provider.documents || Object.keys(provider.documents).length === 0) && (
                  <div className="col-span-3 text-muted-foreground">
                    No documents uploaded
                  </div>
                )}
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
                ? 'Are you sure you want to approve this provider? They will be able to accept bookings.'
                : 'Please provide a reason for rejecting this provider application.'
              }
            </DialogDescription>
          </DialogHeader>
          
          {selectedProvider && (
            <div className="space-y-4">
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
    </div>
  );
};

export default ProviderManagement;

