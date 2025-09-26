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
  RefreshCw,
  Search,
  Edit3,
  Trash2
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

          <div className="bg-white rounded-b-xl shadow-sm border-l border-r border-b border-gray-200 p-6" style={{ height: 'calc(100vh - 380px)', overflowY: 'auto' }}>
            {renderContent()}
          </div>
        </div>
      </div>
    </div>
  );
};

// Tab Components
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
  const [doctors, setDoctors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [specializationFilter, setSpecializationFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');

  const fetchDoctors = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      
      const response = await fetch('http://localhost:8001/api/v1/admin/doctors', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setDoctors(data.doctors || []);
      } else {
        console.error('Failed to fetch doctors');
        setDoctors([]);
      }
    } catch (error) {
      console.error('Error fetching doctors:', error);
      setDoctors([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDoctors();
  }, []);

  const specializations = [...new Set(doctors.map(doctor => doctor.specialization))];

  const filteredDoctors = doctors.filter(doctor => {
    const matchesSearch = doctor.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         doctor.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         doctor.specialization.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesSpecialization = specializationFilter === 'all' || 
                                 doctor.specialization === specializationFilter;
    
    const matchesStatus = statusFilter === 'all' ||
                         (statusFilter === 'active' && !doctor.force_password_change) ||
                         (statusFilter === 'pending' && doctor.force_password_change);
    
    return matchesSearch && matchesSpecialization && matchesStatus;
  });

  const handleDeleteDoctor = async (doctorId) => {
    if (window.confirm('Are you sure you want to delete this doctor?')) {
      try {
        const token = localStorage.getItem('token');
        const response = await fetch(`http://localhost:8001/api/v1/admin/doctors/${doctorId}`, {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });

        if (response.ok) {
          alert('Doctor deleted successfully');
          fetchDoctors();
        } else {
          alert('Failed to delete doctor');
        }
      } catch (error) {
        console.error('Error deleting doctor:', error);
        alert('Error deleting doctor');
      }
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
      </div>
    );
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-2">
          <UserPlus size={20} className="text-gray-600" />
          <h2 className="text-lg font-semibold text-gray-900">Manage Doctors</h2>
          <span className="bg-gray-100 text-gray-600 px-2 py-1 rounded-full text-sm">
            {filteredDoctors.length} doctors
          </span>
        </div>
        <button
          onClick={() => setShowAddDoctor(!showAddDoctor)}
          className="flex items-center space-x-2 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors"
        >
          <Plus size={16} />
          <span>Add New Doctor</span>
        </button>
      </div>

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

      {/* Search and Filter Bar */}
      <div className="bg-white rounded-lg p-4 mb-6 border border-gray-200">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-2">Search Doctors</label>
            <div className="relative">
              <input
                type="text"
                placeholder="Search by name, email, or specialization..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full px-4 py-2 pl-10 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              />
              <div className="absolute left-3 top-2.5 text-gray-400">
                <Search size={16} />
              </div>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Specialization</label>
            <select
              value={specializationFilter}
              onChange={(e) => setSpecializationFilter(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            >
              <option value="all">All Specializations</option>
              {specializations.map(spec => (
                <option key={spec} value={spec}>{spec}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Status</label>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            >
              <option value="all">All Status</option>
              <option value="active">Active</option>
              <option value="pending">Pending Setup</option>
            </select>
          </div>
        </div>

        {(searchTerm || specializationFilter !== 'all' || statusFilter !== 'all') && (
          <div className="mt-3 flex justify-between items-center">
            <span className="text-sm text-gray-600">
              Showing {filteredDoctors.length} of {doctors.length} doctors
            </span>
            <button
              onClick={() => {
                setSearchTerm('');
                setSpecializationFilter('all');
                setStatusFilter('all');
              }}
              className="text-sm text-purple-600 hover:text-purple-800"
            >
              Clear all filters
            </button>
          </div>
        )}
      </div>

      {filteredDoctors.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-lg border border-gray-200">
          <UserPlus size={48} className="mx-auto mb-4 text-gray-400" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">No doctors found</h3>
          <p className="text-gray-600 mb-4">
            {doctors.length === 0 ? "No doctors have been added yet." : "No doctors match your search criteria."}
          </p>
          {doctors.length === 0 && (
            <button
              onClick={() => setShowAddDoctor(true)}
              className="bg-purple-600 text-white px-6 py-2 rounded-lg hover:bg-purple-700 transition-colors"
            >
              Add Your First Doctor
            </button>
          )}
        </div>
      ) : (
        <div className="grid gap-4">
          {filteredDoctors.map(doctor => (
            <div key={doctor.id} className="bg-white rounded-lg p-6 border border-gray-200 hover:shadow-md transition-shadow">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center">
                    <User size={20} className="text-purple-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900">{doctor.name}</h3>
                    <p className="text-sm text-gray-600">{doctor.email}</p>
                    <div className="flex items-center space-x-2 mt-1">
                      <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-xs font-medium">
                        {doctor.specialization}
                      </span>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        doctor.force_password_change 
                          ? 'bg-yellow-100 text-yellow-800' 
                          : 'bg-green-100 text-green-800'
                      }`}>
                        {doctor.force_password_change ? 'Pending Setup' : 'Active'}
                      </span>
                    </div>
                  </div>
                </div>
                
                <div className="flex items-center space-x-2">
                  <button className="text-blue-600 hover:text-blue-800 p-2">
                    <Edit3 size={16} />
                  </button>
                  <button 
                    onClick={() => handleDeleteDoctor(doctor.id)}
                    className="text-red-600 hover:text-red-800 p-2"
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
              </div>
              
              <div className="mt-4 pt-4 border-t border-gray-100 text-sm text-gray-500">
                <div className="flex justify-between">
                  <span>Joined: {new Date(doctor.created_at).toLocaleDateString()}</span>
                  <span>ID: {doctor.id.slice(-6)}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
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