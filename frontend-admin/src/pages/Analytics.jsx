import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
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
  TrendingUp,
  TrendingDown,
  Users,
  Calendar,
  DollarSign,
  Star,
  Download,
  Filter,
  BarChart3,
} from 'lucide-react';

import { apiClient } from '../lib/api';
import { useEffect } from 'react';

const Analytics = () => {
  const [timeRange, setTimeRange] = useState('7d');
  const [selectedMetric, setSelectedMetric] = useState('revenue');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [analyticsData, setAnalyticsData] = useState({
    stats: {
      totalRevenue: 0,
      totalBookings: 0,
      activeUsers: 0,
      avgRating: 0
    },
    charts: {
      revenue: [],
      services: [],
      providers: [],
      hourly: [],
      locations: []
    }
  });

  // Load analytics data
  useEffect(() => {
    loadAnalyticsData();
  }, [timeRange]);

  const loadAnalyticsData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // For now, we don't have real analytics endpoints yet
      // In production, this would call multiple API endpoints:
      // - await apiClient.getAnalyticsStats(timeRange);
      // - await apiClient.getRevenueData(timeRange);
      // - await apiClient.getServiceAnalytics(timeRange);
      setAnalyticsData({
        stats: {
          totalRevenue: 0,
          totalBookings: 0,
          activeUsers: 0,
          avgRating: 0
        },
        charts: {
          revenue: [],
          services: [],
          providers: [],
          hourly: [],
          locations: []
        }
      });
      
    } catch (error) {
      console.error('Failed to load analytics:', error);
      setError('Failed to load analytics data');
    } finally {
      setLoading(false);
    }
  };

  const StatCard = ({ title, value, change, icon: Icon, trend, format = 'number' }) => {
    const formatValue = (val) => {
      if (format === 'currency') return `${(val / 1000).toFixed(0)}K EGP`;
      if (format === 'percentage') return `${val}%`;
      return val.toLocaleString();
    };

    return (
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">{title}</CardTitle>
          <Icon className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{formatValue(value)}</div>
          <div className="flex items-center text-xs text-muted-foreground">
            {trend === 'up' && <TrendingUp className="mr-1 h-3 w-3 text-green-500" />}
            {trend === 'down' && <TrendingDown className="mr-1 h-3 w-3 text-red-500" />}
            <span>
              {typeof change === 'number' 
                ? `${change >= 0 ? '+' : ''}${change}% from last period`
                : change || 'No data available'
              }
            </span>
          </div>
        </CardContent>
      </Card>
    );
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Analytics</h1>
          <p className="text-muted-foreground">
            Comprehensive insights into your platform performance
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Select value={timeRange} onValueChange={setTimeRange}>
            <SelectTrigger className="w-32">
              <SelectValue placeholder="Time Range" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="7d">7 days</SelectItem>
              <SelectItem value="30d">30 days</SelectItem>
              <SelectItem value="90d">90 days</SelectItem>
              <SelectItem value="1y">1 year</SelectItem>
            </SelectContent>
          </Select>
          <Button variant="outline">
            <Download className="mr-2 h-4 w-4" />
            Export
          </Button>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid gap-4 md:grid-cols-4">
        <StatCard
          title="Total Revenue"
          value={analyticsData.stats.totalRevenue}
          change="No historical data"
          icon={DollarSign}
          trend="neutral"
          format="currency"
        />
        <StatCard
          title="Total Bookings"
          value={analyticsData.stats.totalBookings}
          change="No historical data"
          icon={Calendar}
          trend="neutral"
        />
        <StatCard
          title="Active Users"
          value={analyticsData.stats.activeUsers}
          change="No historical data"
          icon={Users}
          trend="neutral"
        />
        <StatCard
          title="Avg. Rating"
          value={analyticsData.stats.avgRating}
          change="No historical data"
          icon={Star}
          trend="neutral"
        />
      </div>

      {/* Analytics Tabs */}
      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="services">Services</TabsTrigger>
          <TabsTrigger value="providers">Providers</TabsTrigger>
          <TabsTrigger value="customers">Customers</TabsTrigger>
          <TabsTrigger value="locations">Locations</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          {loading ? (
            <div className="grid gap-6 md:grid-cols-2">
              <Card>
                <CardContent className="p-6">
                  <div className="text-center py-8">
                    <p className="text-muted-foreground">Loading analytics...</p>
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-6">
                  <div className="text-center py-8">
                    <p className="text-muted-foreground">Loading analytics...</p>
                  </div>
                </CardContent>
              </Card>
            </div>
          ) : error ? (
            <div className="text-center py-8">
              <p className="text-red-600">{error}</p>
              <Button onClick={loadAnalyticsData} className="mt-2">Try Again</Button>
            </div>
          ) : (
            <div className="grid gap-6 md:grid-cols-2">
              {/* Revenue Trend */}
              <Card>
                <CardHeader>
                  <CardTitle>Revenue Trend</CardTitle>
                  <CardDescription>Historical revenue data</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="text-center py-8">
                    <BarChart3 className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                    <p className="text-muted-foreground">No revenue data available</p>
                    <p className="text-sm text-muted-foreground">Data will appear here as your platform grows</p>
                  </div>
                </CardContent>
              </Card>

              {/* Bookings Trend */}
              <Card>
                <CardHeader>
                  <CardTitle>Bookings Trend</CardTitle>
                  <CardDescription>Historical booking data</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="text-center py-8">
                    <BarChart3 className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                    <p className="text-muted-foreground">No booking data available</p>
                    <p className="text-sm text-muted-foreground">Data will appear here as bookings are made</p>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}

          {/* Hourly Activity */}
          <Card>
            <CardHeader>
              <CardTitle>Hourly Booking Activity</CardTitle>
              <CardDescription>Peak hours for service bookings</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8">
                <BarChart3 className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                <p className="text-muted-foreground">No hourly data available</p>
                <p className="text-sm text-muted-foreground">Analytics will appear here as bookings accumulate</p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="services" className="space-y-4">
          <div className="grid gap-6 md:grid-cols-2">
            {/* Service Distribution */}
            <Card>
              <CardHeader>
                <CardTitle>Service Distribution</CardTitle>
                <CardDescription>Bookings by service category</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-center py-8">
                  <BarChart3 className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                  <p className="text-muted-foreground">No service data available</p>
                  <p className="text-sm text-muted-foreground">Service analytics will appear here</p>
                </div>
              </CardContent>
            </Card>

            {/* Service Revenue */}
            <Card>
              <CardHeader>
                <CardTitle>Revenue by Service</CardTitle>
                <CardDescription>Revenue comparison across services</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-center py-8">
                  <BarChart3 className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                  <p className="text-muted-foreground">No revenue data available</p>
                  <p className="text-sm text-muted-foreground">Service revenue data will appear here</p>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Service Performance Table */}
          <Card>
            <CardHeader>
              <CardTitle>Service Performance</CardTitle>
              <CardDescription>Detailed metrics for each service category</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8">
                <BarChart3 className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                <p className="text-muted-foreground">No service performance data available</p>
                <p className="text-sm text-muted-foreground">Performance metrics will appear here as services are used</p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="providers" className="space-y-4">
          {/* Top Providers */}
          <Card>
            <CardHeader>
              <CardTitle>Top Performing Providers</CardTitle>
              <CardDescription>Providers ranked by performance metrics</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8">
                <Users className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                <p className="text-muted-foreground">No provider performance data available</p>
                <p className="text-sm text-muted-foreground">Provider rankings will appear here as they complete more jobs</p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="customers" className="space-y-4">
          {/* Customer Growth */}
          <Card>
            <CardHeader>
              <CardTitle>Customer Growth</CardTitle>
              <CardDescription>New customer acquisition over time</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8">
                <Users className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                <p className="text-muted-foreground">No customer growth data available</p>
                <p className="text-sm text-muted-foreground">Customer analytics will appear here over time</p>
              </div>
            </CardContent>
          </Card>

          {/* Customer Metrics */}
          <div className="grid gap-4 md:grid-cols-3">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Repeat Customers</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">0%</div>
                <p className="text-xs text-muted-foreground">No data yet</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Avg. Bookings per Customer</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">0</div>
                <p className="text-xs text-muted-foreground">No data yet</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Customer Satisfaction</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">0/5</div>
                <p className="text-xs text-muted-foreground">No data yet</p>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="locations" className="space-y-4">
          {/* Location Performance */}
          <Card>
            <CardHeader>
              <CardTitle>Performance by Governorate</CardTitle>
              <CardDescription>Bookings and revenue by location</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8">
                <BarChart3 className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                <p className="text-muted-foreground">No location data available</p>
                <p className="text-sm text-muted-foreground">Location performance will appear here as bookings are made</p>
              </div>
            </CardContent>
          </Card>

          {/* Location Details */}
          <Card>
            <CardHeader>
              <CardTitle>Location Details</CardTitle>
              <CardDescription>Detailed breakdown by governorate</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8">
                <BarChart3 className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                <p className="text-muted-foreground">No location details available</p>
                <p className="text-sm text-muted-foreground">Geographic analytics will appear here over time</p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default Analytics;

