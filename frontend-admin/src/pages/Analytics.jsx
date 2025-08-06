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

// Mock data for analytics
const mockRevenueData = [
  { month: 'Jan', revenue: 45000, bookings: 320, customers: 180 },
  { month: 'Feb', revenue: 52000, bookings: 380, customers: 210 },
  { month: 'Mar', revenue: 48000, bookings: 350, customers: 195 },
  { month: 'Apr', revenue: 61000, bookings: 420, customers: 240 },
  { month: 'May', revenue: 58000, bookings: 390, customers: 225 },
  { month: 'Jun', revenue: 67000, bookings: 450, customers: 260 },
  { month: 'Jul', revenue: 72000, bookings: 480, customers: 280 },
  { month: 'Aug', revenue: 69000, bookings: 460, customers: 270 },
];

const mockServiceData = [
  { name: 'Plumbing', bookings: 1250, revenue: 125000, color: '#3b82f6' },
  { name: 'Electrical', bookings: 980, revenue: 117600, color: '#f59e0b' },
  { name: 'AC Repair', bookings: 750, revenue: 112500, color: '#10b981' },
  { name: 'Cleaning', bookings: 650, revenue: 52000, color: '#8b5cf6' },
  { name: 'Carpentry', bookings: 320, revenue: 28800, color: '#ef4444' },
];

const mockProviderPerformance = [
  { name: 'Mohamed Ali', rating: 4.9, bookings: 156, revenue: 23400 },
  { name: 'Ahmed Hassan', rating: 4.8, bookings: 142, revenue: 21300 },
  { name: 'Khaled Omar', rating: 4.7, bookings: 128, revenue: 19200 },
  { name: 'Ali Hassan', rating: 4.6, bookings: 115, revenue: 17250 },
  { name: 'Omar Youssef', rating: 4.5, bookings: 98, revenue: 14700 },
];

const mockHourlyData = [
  { hour: '6 AM', bookings: 5 },
  { hour: '7 AM', bookings: 12 },
  { hour: '8 AM', bookings: 25 },
  { hour: '9 AM', bookings: 45 },
  { hour: '10 AM', bookings: 38 },
  { hour: '11 AM', bookings: 42 },
  { hour: '12 PM', bookings: 35 },
  { hour: '1 PM', bookings: 40 },
  { hour: '2 PM', bookings: 48 },
  { hour: '3 PM', bookings: 52 },
  { hour: '4 PM', bookings: 46 },
  { hour: '5 PM', bookings: 38 },
  { hour: '6 PM', bookings: 32 },
  { hour: '7 PM', bookings: 28 },
  { hour: '8 PM', bookings: 18 },
  { hour: '9 PM', bookings: 12 },
];

const mockLocationData = [
  { governorate: 'Cairo', bookings: 2450, revenue: 294000 },
  { governorate: 'Giza', bookings: 1680, revenue: 201600 },
  { governorate: 'Alexandria', bookings: 1320, revenue: 158400 },
  { governorate: 'Qalyubia', bookings: 890, revenue: 106800 },
  { governorate: 'Sharqia', bookings: 650, revenue: 78000 },
];

const Analytics = () => {
  const [timeRange, setTimeRange] = useState('7d');
  const [selectedMetric, setSelectedMetric] = useState('revenue');

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
            {trend === 'up' ? (
              <TrendingUp className="mr-1 h-3 w-3 text-green-500" />
            ) : (
              <TrendingDown className="mr-1 h-3 w-3 text-red-500" />
            )}
            <span className={trend === 'up' ? 'text-green-500' : 'text-red-500'}>
              {change}%
            </span>
            <span className="ml-1">from last period</span>
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
          value={435600}
          change={18.7}
          icon={DollarSign}
          trend="up"
          format="currency"
        />
        <StatCard
          title="Total Bookings"
          value={3950}
          change={15.2}
          icon={Calendar}
          trend="up"
        />
        <StatCard
          title="Active Users"
          value={18267}
          change={12.5}
          icon={Users}
          trend="up"
        />
        <StatCard
          title="Avg. Rating"
          value={4.7}
          change={2.1}
          icon={Star}
          trend="up"
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
          <div className="grid gap-6 md:grid-cols-2">
            {/* Revenue Trend */}
            <Card>
              <CardHeader>
                <CardTitle>Revenue Trend</CardTitle>
                <CardDescription>Monthly revenue over time</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <AreaChart data={mockRevenueData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" />
                    <YAxis />
                    <Tooltip formatter={(value) => [`${value} EGP`, 'Revenue']} />
                    <Area
                      type="monotone"
                      dataKey="revenue"
                      stroke="#3b82f6"
                      fill="#3b82f6"
                      fillOpacity={0.3}
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* Bookings Trend */}
            <Card>
              <CardHeader>
                <CardTitle>Bookings Trend</CardTitle>
                <CardDescription>Monthly bookings over time</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={mockRevenueData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" />
                    <YAxis />
                    <Tooltip />
                    <Line
                      type="monotone"
                      dataKey="bookings"
                      stroke="#10b981"
                      strokeWidth={2}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>

          {/* Hourly Activity */}
          <Card>
            <CardHeader>
              <CardTitle>Hourly Booking Activity</CardTitle>
              <CardDescription>Peak hours for service bookings</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={mockHourlyData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="hour" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="bookings" fill="#8b5cf6" />
                </BarChart>
              </ResponsiveContainer>
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
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={mockServiceData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={120}
                      paddingAngle={5}
                      dataKey="bookings"
                    >
                      {mockServiceData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* Service Revenue */}
            <Card>
              <CardHeader>
                <CardTitle>Revenue by Service</CardTitle>
                <CardDescription>Revenue comparison across services</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={mockServiceData} layout="horizontal">
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis type="number" />
                    <YAxis dataKey="name" type="category" width={80} />
                    <Tooltip formatter={(value) => [`${value} EGP`, 'Revenue']} />
                    <Bar dataKey="revenue" fill="#f59e0b" />
                  </BarChart>
                </ResponsiveContainer>
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
              <div className="space-y-4">
                {mockServiceData.map((service, index) => (
                  <div key={index} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex items-center space-x-4">
                      <div
                        className="w-4 h-4 rounded-full"
                        style={{ backgroundColor: service.color }}
                      ></div>
                      <div>
                        <h4 className="font-medium">{service.name}</h4>
                        <p className="text-sm text-muted-foreground">
                          {service.bookings} bookings
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="font-medium">{(service.revenue / 1000).toFixed(0)}K EGP</p>
                      <p className="text-sm text-muted-foreground">Revenue</p>
                    </div>
                  </div>
                ))}
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
              <div className="space-y-4">
                {mockProviderPerformance.map((provider, index) => (
                  <div key={index} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex items-center space-x-4">
                      <div className="w-8 h-8 bg-primary rounded-full flex items-center justify-center text-primary-foreground font-medium">
                        {index + 1}
                      </div>
                      <div>
                        <h4 className="font-medium">{provider.name}</h4>
                        <div className="flex items-center text-sm text-muted-foreground">
                          <Star className="mr-1 h-3 w-3 text-yellow-500" />
                          {provider.rating}
                        </div>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="font-medium">{provider.bookings} bookings</p>
                      <p className="text-sm text-muted-foreground">
                        {(provider.revenue / 1000).toFixed(0)}K EGP revenue
                      </p>
                    </div>
                  </div>
                ))}
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
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={mockRevenueData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip />
                  <Area
                    type="monotone"
                    dataKey="customers"
                    stroke="#10b981"
                    fill="#10b981"
                    fillOpacity={0.3}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Customer Metrics */}
          <div className="grid gap-4 md:grid-cols-3">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Repeat Customers</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">68%</div>
                <p className="text-xs text-muted-foreground">+5% from last month</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Avg. Bookings per Customer</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">3.2</div>
                <p className="text-xs text-muted-foreground">+0.3 from last month</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Customer Satisfaction</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">4.7/5</div>
                <p className="text-xs text-muted-foreground">+0.1 from last month</p>
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
              <ResponsiveContainer width="100%" height={400}>
                <BarChart data={mockLocationData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="governorate" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="bookings" fill="#3b82f6" name="Bookings" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Location Details */}
          <Card>
            <CardHeader>
              <CardTitle>Location Details</CardTitle>
              <CardDescription>Detailed breakdown by governorate</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {mockLocationData.map((location, index) => (
                  <div key={index} className="flex items-center justify-between p-4 border rounded-lg">
                    <div>
                      <h4 className="font-medium">{location.governorate}</h4>
                      <p className="text-sm text-muted-foreground">
                        {location.bookings} bookings
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="font-medium">{(location.revenue / 1000).toFixed(0)}K EGP</p>
                      <p className="text-sm text-muted-foreground">Revenue</p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default Analytics;

