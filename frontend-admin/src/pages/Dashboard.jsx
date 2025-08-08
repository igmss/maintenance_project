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

// Initial empty state for stats
const emptyStats = {
  users: { total: 0, customers: 0, providers: 0, new_this_week: 0 },
  providers: { total: 0, verified: 0, pending_verification: 0, verification_rate: 0 },
  bookings: { total: 0, completed: 0, active: 0, this_month: 0, completion_rate: 0 },
  revenue: { total_revenue: 0, platform_revenue: 0, monthly_revenue: 0, commission_rate: 0 },
  services: { total_services: 0, total_categories: 0, average_rating: 0 }
};

// Chart data will be generated from real API data
const generateChartData = (stats) => {
  // For now, return empty data until we have historical data
  // In production, this would come from a separate API endpoint with historical data
  return [
    { name: 'This Month', revenue: stats?.revenue?.monthly_revenue || 0, bookings: stats?.bookings?.this_month || 0 }
  ];
};

// No fallback data - dashboard will show real data or appropriate empty states

const StatCard = ({ title, value, change, icon: Icon, trend }) => (
  <Card>
    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
      <CardTitle className="text-sm font-medium">{title}</CardTitle>
      <Icon className="h-4 w-4 text-muted-foreground" />
    </CardHeader>
    <CardContent>
      <div className="text-2xl font-bold">
        {typeof value === 'number' ? value.toLocaleString() : value}
      </div>
      <div className="flex items-center text-xs text-muted-foreground">
        {trend === 'up' && <TrendingUp className="mr-1 h-3 w-3 text-green-500" />}
        {trend === 'down' && <TrendingDown className="mr-1 h-3 w-3 text-red-500" />}
        <span>
          {typeof change === 'number' 
            ? `${change >= 0 ? '+' : ''}${change}% from last month`
            : change
          }
        </span>
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
  // Removed timeRange since we don't have historical data endpoints yet
  const [stats, setStats] = useState(emptyStats);
  const [recentBookings, setRecentBookings] = useState([]);
  const [chartData, setChartData] = useState([]);
  const [serviceData, setServiceData] = useState([]);
  const [error, setError] = useState(null);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Load dashboard stats - this is the only real API endpoint we have
      const statsResponse = await apiClient.getDashboardStats();
      if (statsResponse) {
        setStats(statsResponse);
        // Generate chart data from the stats
        setChartData(generateChartData(statsResponse));
      }

      // For now, we don't have real booking or analytics endpoints
      // These will show empty states until those endpoints are implemented
      setRecentBookings([]);
      setServiceData([]);

    } catch (error) {
      console.error('Failed to load dashboard data:', error);
      setError('Failed to load dashboard data. Using fallback data.');
      
      // Keep empty stats on error
      setStats(emptyStats);
      setRecentBookings([]);
      setChartData(generateChartData(null));
      setServiceData([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboardData();
  }, []);

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
        {/* Time range buttons removed - will be added back when historical data is available */}
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
          value={stats.users?.total || 0}
          change={stats.users?.new_this_week || 0}
          icon={Users}
          trend="up"
        />
        <StatCard
          title="Service Providers"
          value={stats.providers?.total || 0}
          change={`${stats.providers?.verified || 0}/${stats.providers?.pending_verification || 0}`}
          icon={UserCheck}
          trend="neutral"
        />
        <StatCard
          title="Total Bookings"
          value={stats.bookings?.total || 0}
          change={stats.bookings?.this_month || 0}
          icon={Calendar}
          trend="up"
        />
        <StatCard
          title="Revenue (EGP)"
          value={stats.revenue?.total_revenue || 0}
          change={stats.revenue?.monthly_revenue || 0}
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
              <LineChart data={generateChartData(stats)}>
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

