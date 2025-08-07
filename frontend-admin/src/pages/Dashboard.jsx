import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { apiClient } from '../lib/api';
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
  BarChart3,
} from 'lucide-react';

// Fallback data for when API is loading or fails
const fallbackStats = {
  totalUsers: 0,
  totalProviders: 0,
  totalBookings: 0,
  totalRevenue: 0,
  userGrowth: 0,
  providerGrowth: 0,
  bookingGrowth: 0,
  revenueGrowth: 0,
};

const fallbackChartData = [
  { name: 'Jan', bookings: 0, revenue: 0, users: 0 },
  { name: 'Feb', bookings: 0, revenue: 0, users: 0 },
  { name: 'Mar', bookings: 0, revenue: 0, users: 0 },
  { name: 'Apr', bookings: 0, revenue: 0, users: 0 },
  { name: 'May', bookings: 0, revenue: 0, users: 0 },
  { name: 'Jun', bookings: 0, revenue: 0, users: 0 },
  { name: 'Jul', bookings: 0, revenue: 0, users: 0 },
];

const fallbackServiceData = [
  { name: 'Loading...', value: 100, color: '#e5e7eb' },
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
  const [loading, setLoading] = useState(true);
  const [timeRange, setTimeRange] = useState('7d');
  const [stats, setStats] = useState(fallbackStats);
  const [recentBookings, setRecentBookings] = useState([]);
  const [chartData, setChartData] = useState(fallbackChartData);
  const [serviceData, setServiceData] = useState(fallbackServiceData);
  const [error, setError] = useState(null);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Load dashboard stats
      const statsResponse = await apiClient.getDashboardStats();
      if (statsResponse) {
        setStats(statsResponse);
      }

      // Load recent bookings
      const bookingsResponse = await apiClient.getBookings({ 
        limit: 5, 
        sort: 'created_at:desc' 
      });
      if (bookingsResponse?.data) {
        setRecentBookings(bookingsResponse.data);
      }

      // Load analytics data for charts
      const analyticsResponse = await apiClient.getAnalytics({ 
        period: timeRange 
      });
      if (analyticsResponse?.chartData) {
        setChartData(analyticsResponse.chartData);
      }
      if (analyticsResponse?.serviceBreakdown) {
        setServiceData(analyticsResponse.serviceBreakdown);
      }

    } catch (error) {
      console.error('Failed to load dashboard data:', error);
      setError('Failed to load dashboard data. Using fallback data.');
      
      // Keep fallback data on error
      setStats(fallbackStats);
      setRecentBookings([]);
      setChartData(fallbackChartData);
      setServiceData(fallbackServiceData);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboardData();
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

      {/* Error Message */}
      {error && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <p className="text-yellow-800">{error}</p>
        </div>
      )}

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Total Users"
          value={stats.totalUsers}
          change={stats.userGrowth}
          icon={Users}
          trend={stats.userGrowth >= 0 ? "up" : "down"}
        />
        <StatCard
          title="Service Providers"
          value={stats.totalProviders}
          change={stats.providerGrowth}
          icon={UserCheck}
          trend={stats.providerGrowth >= 0 ? "up" : "down"}
        />
        <StatCard
          title="Total Bookings"
          value={stats.totalBookings}
          change={stats.bookingGrowth}
          icon={Calendar}
          trend={stats.bookingGrowth >= 0 ? "up" : "down"}
        />
        <StatCard
          title="Revenue (EGP)"
          value={stats.totalRevenue}
          change={stats.revenueGrowth}
          icon={DollarSign}
          trend={stats.revenueGrowth >= 0 ? "up" : "down"}
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
                  <AreaChart data={chartData}>
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
                  data={serviceData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {serviceData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
            <div className="mt-4 space-y-2">
              {serviceData.map((item, index) => (
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
              {recentBookings.length > 0 ? recentBookings.map((booking) => (
                <div
                  key={booking.id}
                  className="flex items-center justify-between p-4 border rounded-lg"
                >
                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-medium">
                        {booking.customer_name || booking.customer || 'Unknown Customer'}
                      </h4>
                      {getStatusBadge(booking.status)}
                    </div>
                    <div className="text-sm text-muted-foreground">
                      <p>Provider: {booking.provider_name || booking.provider || 'Unknown Provider'}</p>
                      <p>Service: {booking.service_name || booking.service || 'Unknown Service'}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="font-medium">EGP {booking.total_amount || booking.amount || 0}</p>
                    <p className="text-sm text-muted-foreground">
                      {booking.scheduled_date || booking.date || 'No date'}
                    </p>
                  </div>
                </div>
              )) : (
                <div className="text-center py-8 text-muted-foreground">
                  <Calendar className="mx-auto h-12 w-12 mb-4" />
                  <p>No recent bookings found</p>
                  <p className="text-sm">Bookings will appear here when customers make bookings</p>
                </div>
              )}
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

