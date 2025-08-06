import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import {
  Users,
  UserCheck,
  Calendar,
  DollarSign,
  TrendingUp,
  TrendingDown,
  Clock,
  CheckCircle,
  AlertCircle,
  XCircle,
  Eye,
  MoreHorizontal,
} from 'lucide-react';

// Mock data - replace with real API calls
const mockStats = {
  totalUsers: 15420,
  totalProviders: 2847,
  totalBookings: 8932,
  totalRevenue: 245680,
  userGrowth: 12.5,
  providerGrowth: 8.3,
  bookingGrowth: 15.2,
  revenueGrowth: 18.7,
};

const mockRecentBookings = [
  {
    id: 1,
    customer: 'Ahmed Hassan',
    provider: 'Mohamed Ali',
    service: 'Plumbing',
    status: 'completed',
    amount: 150,
    date: '2024-08-05',
  },
  {
    id: 2,
    customer: 'Fatima Omar',
    provider: 'Khaled Ahmed',
    service: 'Electrical',
    status: 'in_progress',
    amount: 200,
    date: '2024-08-05',
  },
  {
    id: 3,
    customer: 'Sara Mohamed',
    provider: 'Ali Hassan',
    service: 'Cleaning',
    status: 'pending',
    amount: 80,
    date: '2024-08-05',
  },
];

const mockChartData = [
  { name: 'Jan', bookings: 400, revenue: 24000, users: 240 },
  { name: 'Feb', bookings: 300, revenue: 18000, users: 220 },
  { name: 'Mar', bookings: 500, revenue: 30000, users: 280 },
  { name: 'Apr', bookings: 450, revenue: 27000, users: 300 },
  { name: 'May', bookings: 600, revenue: 36000, users: 350 },
  { name: 'Jun', bookings: 750, revenue: 45000, users: 400 },
  { name: 'Jul', bookings: 680, revenue: 40800, users: 380 },
];

const mockServiceData = [
  { name: 'Plumbing', value: 35, color: '#3b82f6' },
  { name: 'Electrical', value: 25, color: '#f59e0b' },
  { name: 'Cleaning', value: 20, color: '#10b981' },
  { name: 'AC Repair', value: 15, color: '#8b5cf6' },
  { name: 'Others', value: 5, color: '#6b7280' },
];

const StatCard = ({ title, value, change, icon: Icon, trend }) => (
  <Card>
    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
      <CardTitle className="text-sm font-medium">{title}</CardTitle>
      <Icon className="h-4 w-4 text-muted-foreground" />
    </CardHeader>
    <CardContent>
      <div className="text-2xl font-bold">{value.toLocaleString()}</div>
      <div className="flex items-center text-xs text-muted-foreground">
        {trend === 'up' ? (
          <TrendingUp className="mr-1 h-3 w-3 text-green-500" />
        ) : (
          <TrendingDown className="mr-1 h-3 w-3 text-red-500" />
        )}
        <span className={trend === 'up' ? 'text-green-500' : 'text-red-500'}>
          {change}%
        </span>
        <span className="ml-1">from last month</span>
      </div>
    </CardContent>
  </Card>
);

const getStatusBadge = (status) => {
  const statusConfig = {
    completed: { label: 'Completed', variant: 'default', icon: CheckCircle },
    in_progress: { label: 'In Progress', variant: 'secondary', icon: Clock },
    pending: { label: 'Pending', variant: 'outline', icon: AlertCircle },
    cancelled: { label: 'Cancelled', variant: 'destructive', icon: XCircle },
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

const Dashboard = () => {
  const [loading, setLoading] = useState(false);
  const [timeRange, setTimeRange] = useState('7d');

  useEffect(() => {
    // Simulate API call
    setLoading(true);
    setTimeout(() => setLoading(false), 1000);
  }, [timeRange]);

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {[...Array(4)].map((_, i) => (
            <Card key={i}>
              <CardHeader className="space-y-0 pb-2">
                <div className="h-4 bg-muted animate-pulse rounded"></div>
              </CardHeader>
              <CardContent>
                <div className="h-8 bg-muted animate-pulse rounded mb-2"></div>
                <div className="h-3 bg-muted animate-pulse rounded w-3/4"></div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-muted-foreground">
            Welcome back! Here's what's happening with your platform.
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Button
            variant={timeRange === '7d' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setTimeRange('7d')}
          >
            7 days
          </Button>
          <Button
            variant={timeRange === '30d' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setTimeRange('30d')}
          >
            30 days
          </Button>
          <Button
            variant={timeRange === '90d' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setTimeRange('90d')}
          >
            90 days
          </Button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Total Users"
          value={mockStats.totalUsers}
          change={mockStats.userGrowth}
          icon={Users}
          trend="up"
        />
        <StatCard
          title="Service Providers"
          value={mockStats.totalProviders}
          change={mockStats.providerGrowth}
          icon={UserCheck}
          trend="up"
        />
        <StatCard
          title="Total Bookings"
          value={mockStats.totalBookings}
          change={mockStats.bookingGrowth}
          icon={Calendar}
          trend="up"
        />
        <StatCard
          title="Revenue (EGP)"
          value={mockStats.totalRevenue}
          change={mockStats.revenueGrowth}
          icon={DollarSign}
          trend="up"
        />
      </div>

      {/* Charts */}
      <div className="grid gap-6 md:grid-cols-2">
        {/* Bookings Chart */}
        <Card>
          <CardHeader>
            <CardTitle>Bookings Overview</CardTitle>
            <CardDescription>Monthly booking trends</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={mockChartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Area
                  type="monotone"
                  dataKey="bookings"
                  stroke="#3b82f6"
                  fill="#3b82f6"
                  fillOpacity={0.3}
                />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Revenue Chart */}
        <Card>
          <CardHeader>
            <CardTitle>Revenue Trends</CardTitle>
            <CardDescription>Monthly revenue in EGP</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={mockChartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Line
                  type="monotone"
                  dataKey="revenue"
                  stroke="#10b981"
                  strokeWidth={2}
                />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 md:grid-cols-3">
        {/* Service Distribution */}
        <Card>
          <CardHeader>
            <CardTitle>Service Distribution</CardTitle>
            <CardDescription>Popular service categories</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie
                  data={mockServiceData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {mockServiceData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
            <div className="mt-4 space-y-2">
              {mockServiceData.map((item, index) => (
                <div key={index} className="flex items-center justify-between text-sm">
                  <div className="flex items-center">
                    <div
                      className="w-3 h-3 rounded-full mr-2"
                      style={{ backgroundColor: item.color }}
                    ></div>
                    {item.name}
                  </div>
                  <span className="font-medium">{item.value}%</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Recent Bookings */}
        <Card className="md:col-span-2">
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle>Recent Bookings</CardTitle>
              <CardDescription>Latest booking activities</CardDescription>
            </div>
            <Button variant="outline" size="sm">
              <Eye className="mr-2 h-4 w-4" />
              View All
            </Button>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {mockRecentBookings.map((booking) => (
                <div
                  key={booking.id}
                  className="flex items-center justify-between p-4 border rounded-lg"
                >
                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-medium">{booking.customer}</h4>
                      {getStatusBadge(booking.status)}
                    </div>
                    <div className="text-sm text-muted-foreground">
                      <p>Provider: {booking.provider}</p>
                      <p>Service: {booking.service}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="font-medium">EGP {booking.amount}</p>
                    <p className="text-sm text-muted-foreground">{booking.date}</p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
          <CardDescription>Common administrative tasks</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-4">
            <Button className="h-20 flex-col">
              <Users className="mb-2 h-6 w-6" />
              Manage Users
            </Button>
            <Button variant="outline" className="h-20 flex-col">
              <UserCheck className="mb-2 h-6 w-6" />
              Verify Providers
            </Button>
            <Button variant="outline" className="h-20 flex-col">
              <Calendar className="mb-2 h-6 w-6" />
              View Bookings
            </Button>
            <Button variant="outline" className="h-20 flex-col">
              <BarChart3 className="mb-2 h-6 w-6" />
              Analytics
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Dashboard;

