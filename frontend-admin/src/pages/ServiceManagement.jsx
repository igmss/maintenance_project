import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import {
  Wrench,
  Plus,
  Edit,
  Trash2,
  MoreHorizontal,
  Search,
  Eye,
  TrendingUp,
  Users,
  Calendar,
  DollarSign,
} from 'lucide-react';

import { apiClient } from '../lib/api';
import { useEffect } from 'react';

const ServiceManagement = () => {
  const [services, setServices] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [showAddDialog, setShowAddDialog] = useState(false);
  const [showEditDialog, setShowEditDialog] = useState(false);
  const [selectedService, setSelectedService] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [newService, setNewService] = useState({
    name: '',
    nameAr: '',
    description: '',
    descriptionAr: '',
    basePrice: '',
    emergencyPrice: '',
    category: 'maintenance',
    isActive: true,
  });

  // Load services data
  useEffect(() => {
    loadServices();
  }, []);

  const loadServices = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // For now, we don't have a real services endpoint yet
      // In production, this would call: await apiClient.getServices();
      setServices([]);
      
    } catch (error) {
      console.error('Failed to load services:', error);
      setError('Failed to load services');
      setServices([]);
    } finally {
      setLoading(false);
    }
  };

  const filteredServices = services.filter(service =>
    (service.name || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
    (service.name_ar || service.nameAr || '').includes(searchTerm) ||
    (service.description || '').toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleAddService = () => {
    const service = {
      id: Date.now(),
      ...newService,
      basePrice: parseFloat(newService.basePrice),
      emergencyPrice: parseFloat(newService.emergencyPrice),
      averageRating: 0,
      totalProviders: 0,
      totalBookings: 0,
      monthlyRevenue: 0,
      createdAt: new Date().toISOString().split('T')[0],
    };
    
    setServices([...services, service]);
    setNewService({
      name: '',
      nameAr: '',
      description: '',
      descriptionAr: '',
      basePrice: '',
      emergencyPrice: '',
      category: 'maintenance',
      isActive: true,
    });
    setShowAddDialog(false);
  };

  const handleEditService = (service) => {
    setSelectedService(service);
    setNewService({
      name: service.name,
      nameAr: service.nameAr,
      description: service.description,
      descriptionAr: service.descriptionAr,
      basePrice: service.basePrice.toString(),
      emergencyPrice: service.emergencyPrice.toString(),
      category: service.category,
      isActive: service.isActive,
    });
    setShowEditDialog(true);
  };

  const handleUpdateService = () => {
    setServices(services.map(s => 
      s.id === selectedService.id 
        ? {
            ...s,
            ...newService,
            basePrice: parseFloat(newService.basePrice),
            emergencyPrice: parseFloat(newService.emergencyPrice),
          }
        : s
    ));
    setShowEditDialog(false);
    setSelectedService(null);
    setNewService({
      name: '',
      nameAr: '',
      description: '',
      descriptionAr: '',
      basePrice: '',
      emergencyPrice: '',
      category: 'maintenance',
      isActive: true,
    });
  };

  const handleDeleteService = (serviceId) => {
    if (window.confirm('Are you sure you want to delete this service?')) {
      setServices(services.filter(s => s.id !== serviceId));
    }
  };

  const handleToggleStatus = (serviceId) => {
    setServices(services.map(s => 
      s.id === serviceId ? { 
        ...s, 
        is_active: s.is_active !== undefined ? !s.is_active : !s.isActive,
        isActive: s.is_active !== undefined ? !s.is_active : !s.isActive 
      } : s
    ));
  };

  const ServiceForm = ({ isEdit = false }) => (
    <div className="space-y-4">
      <div className="grid gap-4 md:grid-cols-2">
        <div className="space-y-2">
          <Label htmlFor="name">Service Name (English)</Label>
          <Input
            id="name"
            value={newService.name}
            onChange={(e) => setNewService({ ...newService, name: e.target.value })}
            placeholder="e.g., Plumbing"
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="nameAr">Service Name (Arabic)</Label>
          <Input
            id="nameAr"
            value={newService.nameAr}
            onChange={(e) => setNewService({ ...newService, nameAr: e.target.value })}
            placeholder="e.g., السباكة"
            dir="rtl"
          />
        </div>
      </div>

      <div className="space-y-2">
        <Label htmlFor="description">Description (English)</Label>
        <Textarea
          id="description"
          value={newService.description}
          onChange={(e) => setNewService({ ...newService, description: e.target.value })}
          placeholder="Describe the service in English"
          rows={3}
        />
      </div>

      <div className="space-y-2">
        <Label htmlFor="descriptionAr">Description (Arabic)</Label>
        <Textarea
          id="descriptionAr"
          value={newService.descriptionAr}
          onChange={(e) => setNewService({ ...newService, descriptionAr: e.target.value })}
          placeholder="وصف الخدمة بالعربية"
          rows={3}
          dir="rtl"
        />
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <div className="space-y-2">
          <Label htmlFor="basePrice">Base Price (EGP)</Label>
          <Input
            id="basePrice"
            type="number"
            value={newService.basePrice}
            onChange={(e) => setNewService({ ...newService, basePrice: e.target.value })}
            placeholder="100"
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="emergencyPrice">Emergency Price (EGP)</Label>
          <Input
            id="emergencyPrice"
            type="number"
            value={newService.emergencyPrice}
            onChange={(e) => setNewService({ ...newService, emergencyPrice: e.target.value })}
            placeholder="150"
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="category">Category</Label>
          <Select value={newService.category} onValueChange={(value) => setNewService({ ...newService, category: value })}>
            <SelectTrigger>
              <SelectValue placeholder="Select category" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="maintenance">Maintenance</SelectItem>
              <SelectItem value="cleaning">Cleaning</SelectItem>
              <SelectItem value="installation">Installation</SelectItem>
              <SelectItem value="repair">Repair</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      <div className="flex items-center space-x-2">
        <Switch
          id="isActive"
          checked={newService.isActive}
          onCheckedChange={(checked) => setNewService({ ...newService, isActive: checked })}
        />
        <Label htmlFor="isActive">Service is active</Label>
      </div>
    </div>
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Service Management</h1>
          <p className="text-muted-foreground">
            Manage service categories, pricing, and availability
          </p>
        </div>
        <Dialog open={showAddDialog} onOpenChange={setShowAddDialog}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              Add Service
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>Add New Service</DialogTitle>
              <DialogDescription>
                Create a new service category for your platform
              </DialogDescription>
            </DialogHeader>
            <ServiceForm />
            <DialogFooter>
              <Button variant="outline" onClick={() => setShowAddDialog(false)}>
                Cancel
              </Button>
              <Button onClick={handleAddService}>Add Service</Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Services</CardTitle>
            <Wrench className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
                                <div className="text-2xl font-bold">{services.length}</div>
                    <p className="text-xs text-muted-foreground">
                      {services.filter(s => s.is_active !== undefined ? s.is_active : s.isActive).length} active
                    </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Providers</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {services.reduce((sum, s) => sum + (s.total_providers || s.totalProviders || 0), 0)}
            </div>
            <p className="text-xs text-muted-foreground">
              Across all services
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Bookings</CardTitle>
            <Calendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {services.reduce((sum, s) => sum + (s.total_bookings || s.totalBookings || 0), 0)}
            </div>
            <p className="text-xs text-muted-foreground">
              This month
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Monthly Revenue</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {(services.reduce((sum, s) => sum + (s.monthly_revenue || s.monthlyRevenue || 0), 0) / 1000).toFixed(0)}K EGP
            </div>
            <p className="text-xs text-muted-foreground">
              Total monthly revenue
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Services Table */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Services</CardTitle>
              <CardDescription>
                Manage your service categories and their settings
              </CardDescription>
            </div>
            <div className="relative">
              <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search services..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-8 w-64"
              />
            </div>
          </div>
        </CardHeader>
        <CardContent>
                    {loading ? (
            <div className="text-center py-8">
              <p className="text-muted-foreground">Loading services...</p>
            </div>
          ) : error ? (
            <div className="text-center py-8">
              <p className="text-red-600">{error}</p>
              <Button onClick={loadServices} className="mt-2">Try Again</Button>
            </div>
          ) : services.length === 0 ? (
            <div className="text-center py-8">
              <Wrench className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
              <p className="text-muted-foreground">No services found</p>
              <p className="text-sm text-muted-foreground">Services will appear here once they are created</p>
            </div>
          ) : (
            <>
              <div className="rounded-md border">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Service</TableHead>
                      <TableHead>Category</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Pricing</TableHead>
                      <TableHead>Providers</TableHead>
                      <TableHead>Bookings</TableHead>
                      <TableHead>Rating</TableHead>
                      <TableHead>Revenue</TableHead>
                      <TableHead className="text-right">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {filteredServices.map((service) => (
                      <TableRow key={service.id}>
                        <TableCell>
                          <div>
                            <div className="font-medium">{service.name || 'N/A'}</div>
                            <div className="text-sm text-muted-foreground" dir="rtl">
                              {service.name_ar || service.nameAr || 'N/A'}
                            </div>
                          </div>
                        </TableCell>
                        <TableCell>
                          <Badge variant="outline" className="capitalize">
                            {service.category || 'N/A'}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <Badge variant={(service.is_active !== undefined ? service.is_active : service.isActive) ? 'default' : 'secondary'}>
                            {(service.is_active !== undefined ? service.is_active : service.isActive) ? 'Active' : 'Inactive'}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <div className="text-sm">
                            <div>Base: {service.base_price || service.basePrice || 0} EGP</div>
                            <div className="text-muted-foreground">
                              Emergency: {service.emergency_price || service.emergencyPrice || 0} EGP
                            </div>
                          </div>
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center">
                            <Users className="mr-1 h-4 w-4 text-muted-foreground" />
                            {service.total_providers || service.totalProviders || 0}
                          </div>
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center">
                            <Calendar className="mr-1 h-4 w-4 text-muted-foreground" />
                            {service.total_bookings || service.totalBookings || 0}
                          </div>
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center">
                            ⭐ {(service.average_rating || service.averageRating || 0).toFixed(1)}
                          </div>
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center">
                            <TrendingUp className="mr-1 h-4 w-4 text-muted-foreground" />
                            {((service.monthly_revenue || service.monthlyRevenue || 0) / 1000).toFixed(0)}K EGP
                          </div>
                        </TableCell>
                        <TableCell className="text-right">
                          <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                              <Button variant="ghost" className="h-8 w-8 p-0">
                                <MoreHorizontal className="h-4 w-4" />
                              </Button>
                            </DropdownMenuTrigger>
                            <DropdownMenuContent align="end">
                              <DropdownMenuLabel>Actions</DropdownMenuLabel>
                              <DropdownMenuItem onClick={() => handleEditService(service)}>
                                <Edit className="mr-2 h-4 w-4" />
                                Edit Service
                              </DropdownMenuItem>
                              <DropdownMenuItem onClick={() => handleToggleStatus(service.id)}>
                                {(service.is_active !== undefined ? service.is_active : service.isActive) ? 'Deactivate' : 'Activate'}
                              </DropdownMenuItem>
                              <DropdownMenuSeparator />
                              <DropdownMenuItem 
                                onClick={() => handleDeleteService(service.id)}
                                className="text-destructive"
                              >
                                <Trash2 className="mr-2 h-4 w-4" />
                                Delete Service
                              </DropdownMenuItem>
                            </DropdownMenuContent>
                          </DropdownMenu>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>

              {filteredServices.length === 0 && (
                <div className="text-center py-8">
                  <p className="text-muted-foreground">No services found matching your search.</p>
                </div>
              )}
            </>
          )}
        </CardContent>
      </Card>

      {/* Edit Service Dialog */}
      <Dialog open={showEditDialog} onOpenChange={setShowEditDialog}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Edit Service</DialogTitle>
            <DialogDescription>
              Update service information and settings
            </DialogDescription>
          </DialogHeader>
          <ServiceForm isEdit={true} />
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowEditDialog(false)}>
              Cancel
            </Button>
            <Button onClick={handleUpdateService}>Update Service</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default ServiceManagement;

