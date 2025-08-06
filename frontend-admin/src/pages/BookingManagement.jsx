import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
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
  Calendar,
  Clock,
  CheckCircle,
  XCircle,
  AlertCircle,
  Search,
  Filter,
  Eye,
  MapPin,
  User,
  Wrench,
  DollarSign,
  Phone,
  MessageSquare,
} from 'lucide-react';

// Mock booking data
const mockBookings = [
  {
    id: 'BK001',
    customer: {
      name: 'Ahmed Hassan',
      phone: '+20 100 123 4567',
      email: 'ahmed.hassan@email.com'
    },
    provider: {
      name: 'Mohamed Ali',
      phone: '+20 101 234 5678',
      rating: 4.8
    },
    service: 'Plumbing',
    description: 'Kitchen sink repair - water leakage issue',
    status: 'completed',
    priority: 'normal',
    amount: 150,
    bookingDate: '2024-08-05',
    scheduledTime: '10:00 AM',
    completedTime: '11:30 AM',
    address: 'Nasr City, Cairo',
    paymentStatus: 'paid',
    rating: 5,
    customerNotes: 'Excellent service, very professional',
  },
  {
    id: 'BK002',
    customer: {
      name: 'Fatima Omar',
      phone: '+20 102 345 6789',
      email: 'fatima.omar@email.com'
    },
    provider: {
      name: 'Khaled Ahmed',
      phone: '+20 103 456 7890',
      rating: 4.6
    },
    service: 'Electrical',
    description: 'Power outlet installation in living room',
    status: 'in_progress',
    priority: 'normal',
    amount: 200,
    bookingDate: '2024-08-05',
    scheduledTime: '2:00 PM',
    address: 'Maadi, Cairo',
    paymentStatus: 'pending',
  },
  {
    id: 'BK003',
    customer: {
      name: 'Sara Mohamed',
      phone: '+20 104 567 8901',
      email: 'sara.mohamed@email.com'
    },
    provider: {
      name: 'Ali Hassan',
      phone: '+20 105 678 9012',
      rating: 4.9
    },
    service: 'AC Repair',
    description: 'Air conditioner not cooling properly',
    status: 'pending',
    priority: 'urgent',
    amount: 300,
    bookingDate: '2024-08-06',
    scheduledTime: '9:00 AM',
    address: 'Heliopolis, Cairo',
    paymentStatus: 'pending',
  },
  {
    id: 'BK004',
    customer: {
      name: 'Omar Youssef',
      phone: '+20 106 789 0123',
      email: 'omar.youssef@email.com'
    },
    provider: {
      name: 'Hassan Ali',
      phone: '+20 107 890 1234',
      rating: 4.7
    },
    service: 'Cleaning',
    description: 'Deep cleaning for 3-bedroom apartment',
    status: 'cancelled',
    priority: 'normal',
    amount: 120,
    bookingDate: '2024-08-04',
    scheduledTime: '8:00 AM',
    address: 'Zamalek, Cairo',
    paymentStatus: 'refunded',
    cancellationReason: 'Customer requested cancellation',
  },
];

const BookingManagement = () => {
  const [bookings, setBookings] = useState(mockBookings);
  const [selectedBooking, setSelectedBooking] = useState(null);
  const [showBookingDialog, setShowBookingDialog] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [filterPriority, setFilterPriority] = useState('all');

  const getStatusBadge = (status) => {
    const statusConfig = {
      pending: { label: 'Pending', variant: 'secondary', icon: Clock, color: 'text-yellow-600' },
      confirmed: { label: 'Confirmed', variant: 'default', icon: CheckCircle, color: 'text-blue-600' },
      in_progress: { label: 'In Progress', variant: 'default', icon: AlertCircle, color: 'text-blue-600' },
      completed: { label: 'Completed', variant: 'default', icon: CheckCircle, color: 'text-green-600' },
      cancelled: { label: 'Cancelled', variant: 'destructive', icon: XCircle, color: 'text-red-600' },
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

  const getPriorityBadge = (priority) => {
    const priorityConfig = {
      normal: { label: 'Normal', variant: 'outline' },
      urgent: { label: 'Urgent', variant: 'destructive' },
      emergency: { label: 'Emergency', variant: 'destructive' },
    };

    const config = priorityConfig[priority] || priorityConfig.normal;
    return <Badge variant={config.variant}>{config.label}</Badge>;
  };

  const getPaymentStatusBadge = (status) => {
    const statusConfig = {
      pending: { label: 'Pending', variant: 'secondary' },
      paid: { label: 'Paid', variant: 'default' },
      refunded: { label: 'Refunded', variant: 'outline' },
      failed: { label: 'Failed', variant: 'destructive' },
    };

    const config = statusConfig[status] || statusConfig.pending;
    return <Badge variant={config.variant}>{config.label}</Badge>;
  };

  const filteredBookings = bookings.filter(booking => {
    const matchesSearch = 
      booking.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      booking.customer.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      booking.provider.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      booking.service.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesStatus = filterStatus === 'all' || booking.status === filterStatus;
    const matchesPriority = filterPriority === 'all' || booking.priority === filterPriority;
    
    return matchesSearch && matchesStatus && matchesPriority;
  });

  const handleViewBooking = (booking) => {
    setSelectedBooking(booking);
    setShowBookingDialog(true);
  };

  const bookingsByStatus = {
    all: bookings,
    pending: bookings.filter(b => b.status === 'pending'),
    in_progress: bookings.filter(b => b.status === 'in_progress'),
    completed: bookings.filter(b => b.status === 'completed'),
    cancelled: bookings.filter(b => b.status === 'cancelled'),
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Booking Management</h1>
          <p className="text-muted-foreground">
            Monitor and manage all service bookings on your platform
          </p>
        </div>
        <Button variant="outline">
          <Calendar className="mr-2 h-4 w-4" />
          Export Report
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-5">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Bookings</CardTitle>
            <Calendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{bookings.length}</div>
            <p className="text-xs text-muted-foreground">
              +12% from last month
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Pending</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{bookingsByStatus.pending.length}</div>
            <p className="text-xs text-muted-foreground">
              Awaiting confirmation
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">In Progress</CardTitle>
            <AlertCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{bookingsByStatus.in_progress.length}</div>
            <p className="text-xs text-muted-foreground">
              Currently active
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Completed</CardTitle>
            <CheckCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{bookingsByStatus.completed.length}</div>
            <p className="text-xs text-muted-foreground">
              Successfully finished
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Cancelled</CardTitle>
            <XCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{bookingsByStatus.cancelled.length}</div>
            <p className="text-xs text-muted-foreground">
              Cancelled bookings
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Bookings Table */}
      <Card>
        <CardHeader>
          <CardTitle>All Bookings</CardTitle>
          <CardDescription>
            Complete list of all service bookings with their current status
          </CardDescription>
        </CardHeader>
        <CardContent>
          {/* Filters */}
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-2">
              <div className="relative">
                <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search bookings..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-8 w-64"
                />
              </div>
              <Select value={filterStatus} onValueChange={setFilterStatus}>
                <SelectTrigger className="w-32">
                  <SelectValue placeholder="Status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Status</SelectItem>
                  <SelectItem value="pending">Pending</SelectItem>
                  <SelectItem value="confirmed">Confirmed</SelectItem>
                  <SelectItem value="in_progress">In Progress</SelectItem>
                  <SelectItem value="completed">Completed</SelectItem>
                  <SelectItem value="cancelled">Cancelled</SelectItem>
                </SelectContent>
              </Select>
              <Select value={filterPriority} onValueChange={setFilterPriority}>
                <SelectTrigger className="w-32">
                  <SelectValue placeholder="Priority" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Priority</SelectItem>
                  <SelectItem value="normal">Normal</SelectItem>
                  <SelectItem value="urgent">Urgent</SelectItem>
                  <SelectItem value="emergency">Emergency</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <Button variant="outline" size="sm">
              <Filter className="mr-2 h-4 w-4" />
              More Filters
            </Button>
          </div>

          {/* Table */}
          <div className="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Booking ID</TableHead>
                  <TableHead>Customer</TableHead>
                  <TableHead>Provider</TableHead>
                  <TableHead>Service</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Priority</TableHead>
                  <TableHead>Date & Time</TableHead>
                  <TableHead>Amount</TableHead>
                  <TableHead>Payment</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredBookings.map((booking) => (
                  <TableRow key={booking.id}>
                    <TableCell className="font-medium">{booking.id}</TableCell>
                    <TableCell>
                      <div>
                        <div className="font-medium">{booking.customer.name}</div>
                        <div className="text-sm text-muted-foreground">
                          {booking.customer.phone}
                        </div>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div>
                        <div className="font-medium">{booking.provider.name}</div>
                        <div className="text-sm text-muted-foreground">
                          ⭐ {booking.provider.rating}
                        </div>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center">
                        <Wrench className="mr-2 h-4 w-4 text-muted-foreground" />
                        {booking.service}
                      </div>
                    </TableCell>
                    <TableCell>{getStatusBadge(booking.status)}</TableCell>
                    <TableCell>{getPriorityBadge(booking.priority)}</TableCell>
                    <TableCell>
                      <div className="text-sm">
                        <div>{booking.bookingDate}</div>
                        <div className="text-muted-foreground">{booking.scheduledTime}</div>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center">
                        <DollarSign className="mr-1 h-4 w-4 text-muted-foreground" />
                        {booking.amount} EGP
                      </div>
                    </TableCell>
                    <TableCell>{getPaymentStatusBadge(booking.paymentStatus)}</TableCell>
                    <TableCell className="text-right">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleViewBooking(booking)}
                      >
                        <Eye className="h-4 w-4" />
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>

          {filteredBookings.length === 0 && (
            <div className="text-center py-8">
              <p className="text-muted-foreground">No bookings found matching your criteria.</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Booking Details Dialog */}
      <Dialog open={showBookingDialog} onOpenChange={setShowBookingDialog}>
        <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Booking Details - {selectedBooking?.id}</DialogTitle>
            <DialogDescription>
              Complete information about this service booking
            </DialogDescription>
          </DialogHeader>
          
          {selectedBooking && (
            <div className="space-y-6">
              {/* Status and Priority */}
              <div className="flex items-center space-x-4">
                {getStatusBadge(selectedBooking.status)}
                {getPriorityBadge(selectedBooking.priority)}
                {getPaymentStatusBadge(selectedBooking.paymentStatus)}
              </div>

              <div className="grid gap-6 md:grid-cols-2">
                {/* Customer Information */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center">
                      <User className="mr-2 h-5 w-5" />
                      Customer Information
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-2">
                    <div>
                      <strong>Name:</strong> {selectedBooking.customer.name}
                    </div>
                    <div className="flex items-center">
                      <Phone className="mr-2 h-4 w-4 text-muted-foreground" />
                      {selectedBooking.customer.phone}
                    </div>
                    <div>
                      <strong>Email:</strong> {selectedBooking.customer.email}
                    </div>
                    <div className="flex items-center">
                      <MapPin className="mr-2 h-4 w-4 text-muted-foreground" />
                      {selectedBooking.address}
                    </div>
                  </CardContent>
                </Card>

                {/* Provider Information */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center">
                      <Wrench className="mr-2 h-5 w-5" />
                      Provider Information
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-2">
                    <div>
                      <strong>Name:</strong> {selectedBooking.provider.name}
                    </div>
                    <div className="flex items-center">
                      <Phone className="mr-2 h-4 w-4 text-muted-foreground" />
                      {selectedBooking.provider.phone}
                    </div>
                    <div>
                      <strong>Rating:</strong> ⭐ {selectedBooking.provider.rating}
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Service Details */}
              <Card>
                <CardHeader>
                  <CardTitle>Service Details</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid gap-4 md:grid-cols-2">
                    <div>
                      <strong>Service Type:</strong> {selectedBooking.service}
                    </div>
                    <div>
                      <strong>Amount:</strong> {selectedBooking.amount} EGP
                    </div>
                    <div>
                      <strong>Booking Date:</strong> {selectedBooking.bookingDate}
                    </div>
                    <div>
                      <strong>Scheduled Time:</strong> {selectedBooking.scheduledTime}
                    </div>
                    {selectedBooking.completedTime && (
                      <div>
                        <strong>Completed Time:</strong> {selectedBooking.completedTime}
                      </div>
                    )}
                  </div>
                  <div>
                    <strong>Description:</strong>
                    <p className="mt-1 text-sm text-muted-foreground">
                      {selectedBooking.description}
                    </p>
                  </div>
                  {selectedBooking.customerNotes && (
                    <div>
                      <strong>Customer Notes:</strong>
                      <p className="mt-1 text-sm text-muted-foreground">
                        {selectedBooking.customerNotes}
                      </p>
                    </div>
                  )}
                  {selectedBooking.cancellationReason && (
                    <div>
                      <strong>Cancellation Reason:</strong>
                      <p className="mt-1 text-sm text-red-600">
                        {selectedBooking.cancellationReason}
                      </p>
                    </div>
                  )}
                  {selectedBooking.rating && (
                    <div>
                      <strong>Customer Rating:</strong> ⭐ {selectedBooking.rating}/5
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Actions */}
              <div className="flex justify-end space-x-2">
                <Button variant="outline">
                  <MessageSquare className="mr-2 h-4 w-4" />
                  Contact Customer
                </Button>
                <Button variant="outline">
                  <Phone className="mr-2 h-4 w-4" />
                  Contact Provider
                </Button>
                <Button>
                  Edit Booking
                </Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default BookingManagement;

