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

// Mock service data
const mockServices = [
  {
    id: 1,
    name: 'Plumbing',
    nameAr: 'السباكة',
    description: 'Professional plumbing services including repairs, installations, and maintenance',
    descriptionAr: 'خدمات السباكة المهنية تشمل الإصلاحات والتركيبات والصيانة',
    icon: 'plumbing',
    isActive: true,
    basePrice: 100,
    emergencyPrice: 150,
    averageRating: 4.7,
    totalProviders: 45,
    totalBookings: 1250,
    monthlyRevenue: 125000,
    category: 'maintenance',
    createdAt: '2024-01-15',
  },
  {
    id: 2,
    name: 'Electrical',
    nameAr: 'الكهرباء',
    description: 'Electrical services including wiring, repairs, and installations',
    descriptionAr: 'الخدمات الكهربائية تشمل الأسلاك والإصلاحات والتركيبات',
    icon: 'electrical',
    isActive: true,
    basePrice: 120,
    emergencyPrice: 180,
    averageRating: 4.8,
    totalProviders: 38,
    totalBookings: 980,
    monthlyRevenue: 117600,
    category: 'maintenance',
    createdAt: '2024-01-15',
  },
  {
    id: 3,
    name: 'Air Conditioning',
    nameAr: 'التكييف',
    description: 'AC repair, maintenance, and installation services',
    descriptionAr: 'خدمات إصلاح وصيانة وتركيب التكييف',
    icon: 'ac',
    isActive: true,
    basePrice: 150,
    emergencyPrice: 200,
    averageRating: 4.6,
    totalProviders: 32,
    totalBookings: 750,
    monthlyRevenue: 112500,
    category: 'maintenance',
    createdAt: '2024-01-20',
  },
  {
    id: 4,
    name: 'Cleaning',
    nameAr: 'التنظيف',
    description: 'Professional cleaning services for homes and offices',
    descriptionAr: 'خدمات التنظيف المهنية للمنازل والمكاتب',
    icon: 'cleaning',
    isActive: true,
    basePrice: 80,
    emergencyPrice: 100,
    averageRating: 4.5,
    totalProviders: 28,
    totalBookings: 650,
    monthlyRevenue: 52000,
    category: 'cleaning',
    createdAt: '2024-02-01',
  },
  {
    id: 5,
    name: 'Carpentry',
    nameAr: 'النجارة',
    description: 'Wood work, furniture repair, and custom carpentry',
    descriptionAr: 'أعمال الخشب وإصلاح الأثاث والنجارة المخصصة',
    icon: 'carpentry',
    isActive: false,
    basePrice: 90,
    emergencyPrice: 130,
    averageRating: 4.4,
    totalProviders: 15,
    totalBookings: 320,
    monthlyRevenue: 28800,
    category: 'maintenance',
    createdAt: '2024-02-15',
  },
];

const ServiceManagement = () => {
  const [services, setServices] = useState(mockServices);
  const [searchTerm, setSearchTerm] = useState('');
  const [showAddDialog, setShowAddDialog] = useState(false);
  const [showEditDialog, setShowEditDialog] = useState(false);
  const [selectedService, setSelectedService] = useState(null);
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

  const filteredServices = services.filter(service =>
    service.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    service.nameAr.includes(searchTerm) ||
    service.description.toLowerCase().includes(searchTerm.toLowerCase())
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
      s.id === serviceId ? { ...s, isActive: !s.isActive } : s
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
              {services.filter(s => s.isActive).length} active
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
              {services.reduce((sum, s) => sum + s.totalProviders, 0)}
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
              {services.reduce((sum, s) => sum + s.totalBookings, 0)}
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
              {(services.reduce((sum, s) => sum + s.monthlyRevenue, 0) / 1000).toFixed(0)}K EGP
            </div>
            <p className="text-xs text-muted-foreground">
              +15% from last month
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
                        <div className="font-medium">{service.name}</div>
                        <div className="text-sm text-muted-foreground" dir="rtl">
                          {service.nameAr}
                        </div>
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline" className="capitalize">
                        {service.category}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Badge variant={service.isActive ? 'default' : 'secondary'}>
                        {service.isActive ? 'Active' : 'Inactive'}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <div className="text-sm">
                        <div>Base: {service.basePrice} EGP</div>
                        <div className="text-muted-foreground">
                          Emergency: {service.emergencyPrice} EGP
                        </div>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center">
                        <Users className="mr-1 h-4 w-4 text-muted-foreground" />
                        {service.totalProviders}
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center">
                        <Calendar className="mr-1 h-4 w-4 text-muted-foreground" />
                        {service.totalBookings}
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center">
                        ⭐ {service.averageRating.toFixed(1)}
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center">
                        <TrendingUp className="mr-1 h-4 w-4 text-muted-foreground" />
                        {(service.monthlyRevenue / 1000).toFixed(0)}K EGP
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
                            {service.isActive ? 'Deactivate' : 'Activate'}
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

