import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Users, 
  UserPlus, 
  Calendar, 
  DollarSign, 
  Bell,
  User,
  Settings,
  BarChart3,
  Activity,
  Plus,
  X,
  Check,
  RefreshCw
} from 'lucide-react';

const AdminDashboard = () => {
  const [stats, setStats] = useState({
    totalPatients: 0,
    totalDoctors: 0,
    todayAppointments: 0,
    monthlyRevenue: '$0'
  });
  const [loading, setLoading] = useState(true);
  const [showAddDoctor, setShowAddDoctor] = useState(false);
  const [newDoctor, setNewDoctor] = useState({
    name: '',
    email: '',
    specialization: '',
    password: ''
  });
  const [message, setMessage] = useState('');
  const [activeTab, setActiveTab] = useState('overview');
  const navigate = useNavigate();

  // Fetch real stats from API
  const fetchStats = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      
      const response = await fetch('http://localhost:8001/api/v1/admin/stats', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setStats({
          totalPatients: data.total_patients || 0,
          totalDoctors: data.total_doctors || 0,
          todayAppointments: data.today_appointments || 0,
          monthlyRevenue: data.monthly_revenue || '$0'
        });
      } else {
        console.error('Failed to fetch stats');
        // Fallback to placeholder values if API fails
        setStats({
          totalPatients: 0,
          totalDoctors: 0,
          todayAppointments: 0,
          monthlyRevenue: '$0'
        });
      }
    } catch (error) {
      console.error('Error fetching stats:', error);
      setStats({
        totalPatients: 0,
        totalDoctors: 0,
        todayAppointments: 0,
        monthlyRevenue: '$0'
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
  }, []);

  const handleAddDoctor = async (e) => {
    if (e && e.preventDefault) e.preventDefault();
    try {
      const token = localStorage.getItem('token');
      
      const response = await fetch('http://localhost:8001/api/v1/admin/doctors', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(newDoctor)
      });

      const data = await response.json();

      if (response.ok) {
        setMessage('Doctor added successfully!');
        setNewDoctor({ name: '', email: '', specialization: '', password: '' });
        setShowAddDoctor(false);
        // Refresh stats after adding a new doctor
        fetchStats();
      } else {
        setMessage('Error: ' + data.detail);
      }
    } catch (error) {
      setMessage('Network error. Please try again.');
    }
  };

  const handleLogout = () => {
    localStorage.clear();
    navigate('/login');
  };

  const sidebarItems = [
    { id: 'overview', label: 'Overview', icon: BarChart3 },
    { id: 'doctors', label: 'Manage Doctors', icon: UserPlus },
    { id: 'patients', label: 'Patients', icon: Users },
    { id: 'appointments', label: 'Appointments', icon: Calendar },
    { id: 'settings', label: 'Settings', icon: Settings },
  ];

  const quickStats = [
    { 
      label: 'Today', 
      value: stats.todayAppointments.toString(), 
      sublabel: 'Appointments', 
      color: 'bg-blue-50 text-blue-600' 
    },
    { 
      label: 'Revenue', 
      value: stats.monthlyRevenue, 
      sublabel: 'This Month', 
      color: 'bg-green-50 text-green-600' 
    },
  ];

  const renderContent = () => {
    switch(activeTab) {
      case 'doctors':
        return <DoctorsTab 
          showAddDoctor={showAddDoctor} 
          setShowAddDoctor={setShowAddDoctor} 
          newDoctor={newDoctor} 
          setNewDoctor={setNewDoctor} 
          handleAddDoctor={handleAddDoctor} 
          message={message} 
        />;
      case 'patients':
        return <PatientsTab />;
      case 'appointments':
        return <AppointmentsTab />;
      case 'settings':
        return <SettingsTab />;
      default:
        return <OverviewTab stats={stats} />;
    }
  };

  // Loading state
  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="animate-spin h-12 w-12 text-purple-600 mx-auto mb-4" />
          <p className="text-gray-600">Loading dashboard data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar */}
      <div className="w-64 bg-white shadow-sm border-r border-gray-200">
        {/* Logo */}
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-purple-600 rounded-lg flex items-center justify-center">
              <div className="w-6 h-6 bg-white rounded-full flex items-center justify-center">
                <div className="w-3 h-3 bg-purple-600 rounded-full"></div>
              </div>
            </div>
            <div>
              <h1 className="text-lg font-bold text-gray-900">DocTalk AI</h1>
              <p className="text-xs text-gray-500">Admin Portal</p>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <nav className="p-4 space-y-1">
          {sidebarItems.map((item) => {
            const Icon = item.icon;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-left transition-colors ${
                  activeTab === item.id
                    ? 'bg-purple-50 text-purple-600 font-medium'
                    : 'text-gray-700 hover:bg-gray-50'
                }`}
              >
                <Icon size={20} />
                <span className="text-sm">{item.label}</span>
              </button>
            );
          })}
        </nav>

        {/* Quick Stats in Sidebar */}
        <div className="p-4 mt-8">
          <h3 className="text-sm font-semibold text-gray-900 mb-3">Quick Stats</h3>
          <div className="space-y-3">
            {quickStats.map((stat, index) => (
              <div key={index} className={`p-3 rounded-lg ${stat.color}`}>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-xs font-medium opacity-80">{stat.label}</p>
                    <p className="text-sm font-medium">{stat.sublabel}</p>
                  </div>
                  <p className="text-2xl font-bold">{stat.value}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <header className="bg-white border-b border-gray-200 px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold text-gray-900">Admin Dashboard</h2>
              <p className="text-sm text-gray-600 mt-1">
                System administration and management panel
              </p>
            </div>
            <div className="flex items-center space-x-4">
              <button 
                onClick={fetchStats}
                className="flex items-center space-x-2 text-gray-600 hover:text-gray-900 transition-colors"
                title="Refresh data"
              >
                <RefreshCw size={20} />
                <span className="text-sm">Refresh</span>
              </button>
              <button className="p-2 text-gray-400 hover:text-gray-600 transition-colors">
                <Bell size={20} />
              </button>
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-purple-500 rounded-full flex items-center justify-center">
                  <User size={16} className="text-white" />
                </div>
                <button
                  onClick={handleLogout}
                  className="text-sm text-gray-700 hover:text-gray-900 transition-colors"
                >
                  Logout
                </button>
              </div>
            </div>
          </div>
        </header>

        {/* Stats Cards */}
        <div className="px-6 py-6">
          <div className="grid grid-cols-4 gap-6 mb-8">
            <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <div className="flex items-center space-x-2 mb-2">
                    <Users size={16} className="text-gray-400" />
                  </div>
                  <p className="text-3xl font-bold text-gray-900">{stats.totalPatients}</p>
                  <p className="text-sm text-gray-600">Total Patients</p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <div className="flex items-center space-x-2 mb-2">
                    <UserPlus size={16} className="text-gray-400" />
                  </div>
                  <p className="text-3xl font-bold text-gray-900">{stats.totalDoctors}</p>
                  <p className="text-sm text-gray-600">Total Doctors</p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <div className="flex items-center space-x-2 mb-2">
                    <Calendar size={16} className="text-gray-400" />
                  </div>
                  <p className="text-3xl font-bold text-gray-900">{stats.todayAppointments}</p>
                  <p className="text-sm text-gray-600">Today's Appointments</p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <div className="flex items-center space-x-2 mb-2">
                    <DollarSign size={16} className="text-gray-400" />
                  </div>
                  <p className="text-3xl font-bold text-gray-900">{stats.monthlyRevenue}</p>
                  <p className="text-sm text-gray-600">Revenue</p>
                </div>
              </div>
            </div>
          </div>

          {/* Tab Navigation */}
          <div className="bg-white rounded-t-xl border-b border-gray-200">
            <div className="flex space-x-8 px-6">
              {[
                { id: 'overview', label: 'Overview', icon: BarChart3 },
                { id: 'doctors', label: 'Manage Doctors', icon: UserPlus },
                { id: 'patients', label: 'Patients', icon: Users },
                { id: 'appointments', label: 'Appointments', icon: Calendar },
                { id: 'settings', label: 'Settings', icon: Settings },
              ].map((tab) => {
                const Icon = tab.icon;
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`flex items-center space-x-2 py-4 px-2 border-b-2 transition-colors ${
                      activeTab === tab.id
                        ? 'border-purple-600 text-purple-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700'
                    }`}
                  >
                    <Icon size={16} />
                    <span className="text-sm font-medium">{tab.label}</span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Content Area */}
          <div className="bg-white rounded-b-xl shadow-sm border-l border-r border-b border-gray-200 p-6">
            {renderContent()}
          </div>
        </div>
      </div>
    </div>
  );
};

// Tab Components (keep the same as before)
const OverviewTab = ({ stats }) => {
  return (
    <div>
      <div className="flex items-center space-x-2 mb-6">
        <Activity size={20} className="text-gray-600" />
        <h2 className="text-lg font-semibold text-gray-900">Recent Activity</h2>
      </div>
      
      <div className="space-y-3">
        <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
          <div className="flex items-center space-x-4">
            <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
              <UserPlus size={16} className="text-green-600" />
            </div>
            <div>
              <p className="font-semibold text-gray-800">New doctor registration</p>
              <p className="text-sm text-gray-600">Dr. Sarah Johnson - Cardiologist</p>
            </div>
          </div>
          <span className="text-sm text-gray-500">2 hours ago</span>
        </div>
        
        <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
          <div className="flex items-center space-x-4">
            <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
              <Calendar size={16} className="text-blue-600" />
            </div>
            <div>
              <p className="font-semibold text-gray-800">Patient appointment booked</p>
              <p className="text-sm text-gray-600">John Doe - General Checkup</p>
            </div>
          </div>
          <span className="text-sm text-gray-500">5 hours ago</span>
        </div>
        
        <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
          <div className="flex items-center space-x-4">
            <div className="w-10 h-10 bg-purple-100 rounded-full flex items-center justify-center">
              <Settings size={16} className="text-purple-600" />
            </div>
            <div>
              <p className="font-semibold text-gray-800">System maintenance</p>
              <p className="text-sm text-gray-600">Database backup completed</p>
            </div>
          </div>
          <span className="text-sm text-gray-500">1 day ago</span>
        </div>
      </div>
    </div>
  );
};

const DoctorsTab = ({ showAddDoctor, setShowAddDoctor, newDoctor, setNewDoctor, handleAddDoctor, message }) => {
  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-2">
          <UserPlus size={20} className="text-gray-600" />
          <h2 className="text-lg font-semibold text-gray-900">Manage Doctors</h2>
        </div>
        <button
          onClick={() => setShowAddDoctor(!showAddDoctor)}
          className="flex items-center space-x-2 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors"
        >
          <Plus size={16} />
          <span>Add New Doctor</span>
        </button>
      </div>

      {/* Add Doctor Form */}
      {showAddDoctor && (
        <div className="bg-gray-50 rounded-lg p-6 mb-6 border border-gray-200">
          <h3 className="text-lg font-semibold mb-4 text-gray-900">Add New Doctor</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <input
              type="text"
              placeholder="Full Name"
              value={newDoctor.name}
              onChange={(e) => setNewDoctor({...newDoctor, name: e.target.value})}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              required
            />
            
            <input
              type="email"
              placeholder="Email Address"
              value={newDoctor.email}
              onChange={(e) => setNewDoctor({...newDoctor, email: e.target.value})}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              required
            />
            
            <input
              type="text"
              placeholder="Specialization"
              value={newDoctor.specialization}
              onChange={(e) => setNewDoctor({...newDoctor, specialization: e.target.value})}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              required
            />
            
            <input
              type="password"
              placeholder="Temporary Password"
              value={newDoctor.password}
              onChange={(e) => setNewDoctor({...newDoctor, password: e.target.value})}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              required
            />
            
            <div className="md:col-span-2 flex space-x-4">
              <button
                onClick={handleAddDoctor}
                className="flex items-center space-x-2 bg-purple-600 text-white px-6 py-2 rounded-lg hover:bg-purple-700 transition-colors"
              >
                <Check size={16} />
                <span>Add Doctor</span>
              </button>
              <button
                onClick={() => setShowAddDoctor(false)}
                className="flex items-center space-x-2 bg-gray-500 text-white px-6 py-2 rounded-lg hover:bg-gray-600 transition-colors"
              >
                <X size={16} />
                <span>Cancel</span>
              </button>
            </div>
          </div>
          
          {message && (
            <div className={`mt-4 p-3 rounded-lg ${
              message.includes('Error') ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'
            }`}>
              {message}
            </div>
          )}
        </div>
      )}

      <div className="text-center py-8 text-gray-500">
        <UserPlus size={48} className="mx-auto mb-4 opacity-50" />
        <p>Doctor management features will be displayed here</p>
      </div>
    </div>
  );
};

const PatientsTab = () => {
  return (
    <div className="text-center py-12">
      <Users size={48} className="text-gray-400 mx-auto mb-4" />
      <h2 className="text-xl font-semibold text-gray-900 mb-2">Patient Management</h2>
      <p className="text-gray-600 mb-6">View and manage patient records and information</p>
      <button className="bg-purple-600 text-white px-6 py-3 rounded-lg hover:bg-purple-700 transition-colors">
        View All Patients
      </button>
    </div>
  );
};

const AppointmentsTab = () => {
  return (
    <div className="text-center py-12">
      <Calendar size={48} className="text-gray-400 mx-auto mb-4" />
      <h2 className="text-xl font-semibold text-gray-900 mb-2">Appointment Management</h2>
      <p className="text-gray-600 mb-6">Monitor and manage system-wide appointments</p>
      <button className="bg-purple-600 text-white px-6 py-3 rounded-lg hover:bg-purple-700 transition-colors">
        View All Appointments
      </button>
    </div>
  );
};

const SettingsTab = () => {
  return (
    <div className="text-center py-12">
      <Settings size={48} className="text-gray-400 mx-auto mb-4" />
      <h2 className="text-xl font-semibold text-gray-900 mb-2">System Settings</h2>
      <p className="text-gray-600 mb-6">Configure system-wide settings and preferences</p>
      <button className="bg-purple-600 text-white px-6 py-3 rounded-lg hover:bg-purple-700 transition-colors">
        Manage Settings
      </button>
    </div>
  );
};

export default AdminDashboard;