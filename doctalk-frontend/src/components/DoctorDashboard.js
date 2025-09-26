import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Calendar, 
  Phone, 
  Users, 
  BarChart3, 
  Settings, 
  Bell,
  User,
  ChevronRight,
  CheckCircle,
  XCircle
} from 'lucide-react';
import { doctorAppointmentService } from "../services/doctorAppointmentService";

const DoctorDashboard = () => {
  const [activeTab, setActiveTab] = useState('appointments');
  const [stats, setStats] = useState({
    today: 0,
    voiceCalls: 0,
    patients: 0,
    satisfaction: '0%'
  });
  const navigate = useNavigate();
  const username = localStorage.getItem('userName') || "Doctor";
  const doctorId = localStorage.getItem('userId');

  // Fetch dashboard stats
  const fetchDashboardStats = React.useCallback(async () => {
    try {
      // Get today's appointments
      const today = new Date().toISOString().split('T')[0];
      const response = await doctorAppointmentService.getDoctorAppointments(doctorId, today, null);
      
      const appointments = response.appointments || [];
      const todayCount = appointments.length;
      
      // Get all appointments to calculate patient count (unique patients)
      const allAppointmentsResponse = await doctorAppointmentService.getDoctorAppointments(doctorId, null, null);
      const allAppointments = allAppointmentsResponse.appointments || [];
      
      // Calculate unique patients
      const uniquePatients = new Set(allAppointments.map(app => app.patientId)).size;
      
      // Calculate satisfaction rate from completed appointments
      const completedAppointments = allAppointments.filter(app => app.status === 'completed');
      const satisfactionRate = completedAppointments.length > 0 
        ? Math.round((completedAppointments.length / allAppointments.length) * 100)
        : 0;

      // Update stats
      setStats({
        today: todayCount,
        voiceCalls: completedAppointments.length, // Using completed appointments as voice calls for now
        patients: uniquePatients,
        satisfaction: `${satisfactionRate}%`
      });
    } catch (error) {
      console.error('Error fetching dashboard stats:', error);
    }
  }, [doctorId]);

  useEffect(() => {
    fetchDashboardStats();
    // Refresh stats every 5 minutes
    const interval = setInterval(fetchDashboardStats, 300000);
    return () => clearInterval(interval);
  }, [doctorId, fetchDashboardStats]);

  const handleLogout = () => {
    localStorage.clear();
    navigate('/login');
  };

  const sidebarItems = [
    { id: 'appointments', label: 'Appointments', icon: Calendar },
    { id: 'voice-agent', label: 'Voice Agent', icon: Phone },
    { id: 'patients', label: 'Patients', icon: Users },
    { id: 'analytics', label: 'Analytics', icon: BarChart3 },
    { id: 'settings', label: 'Settings', icon: Settings },
  ];

  const quickStats = [
    { 
      label: 'Today', 
      value: stats.today.toString(), 
      sublabel: 'Appointments', 
      color: 'bg-blue-50 text-blue-600' 
    },
    { 
      label: 'Voice Calls', 
      value: stats.voiceCalls.toString(), 
      sublabel: 'Total', 
      color: 'bg-green-50 text-green-600' 
    },
  ];

  const renderContent = () => {
    switch(activeTab) {
      case 'voice-agent':
        return <VoiceAgentTab />;
      case 'patients':
        return <PatientsTab />;
      case 'analytics':
        return <AnalyticsTab />;
      case 'settings':
        return <SettingsTab />;
      default:
        return <AppointmentsTab />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar */}
      <div className="w-64 bg-white shadow-sm border-r border-gray-200 fixed h-screen flex flex-col">
        {/* Logo */}
        <div className="p-6 border-b border-gray-200 flex-shrink-0">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
              <div className="w-6 h-6 bg-white rounded-full flex items-center justify-center">
                <div className="w-3 h-3 bg-blue-600 rounded-full"></div>
              </div>
            </div>
            <div>
              <h1 className="text-lg font-bold text-gray-900">DocTalk AI</h1>
              <p className="text-xs text-gray-500">Doctor Portal</p>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <nav className="p-4 space-y-1 flex-shrink-0">
          {sidebarItems.map((item) => {
            const Icon = item.icon;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-left transition-colors ${
                  activeTab === item.id
                    ? 'bg-blue-50 text-blue-600 font-medium'
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
        <div className="p-4 mt-4 flex-1 overflow-y-auto">
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
      <div className="flex-1 flex flex-col ml-64">
        {/* Header */}
        <header className="bg-white border-b border-gray-200 px-6 py-4 fixed right-0 left-64 top-0 z-10">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold text-gray-900">Welcome, {username}</h2>
              <p className="text-sm text-gray-600 mt-1">
                Manage your practice with AI-powered appointment booking and patient care tools
              </p>
            </div>
            <div className="flex items-center space-x-4">
              <button className="p-2 text-gray-400 hover:text-gray-600 transition-colors">
                <Bell size={20} />
              </button>
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-orange-500 rounded-full flex items-center justify-center">
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
        <div className="px-6 py-6 mt-20">
          <div className="grid grid-cols-4 gap-6 mb-8">
            <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <div className="flex items-center space-x-2 mb-2">
                    <Calendar size={16} className="text-gray-400" />
                  </div>
                  <p className="text-3xl font-bold text-gray-900">{stats.today}</p>
                  <p className="text-sm text-gray-600">Today</p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <div className="flex items-center space-x-2 mb-2">
                    <Users size={16} className="text-gray-400" />
                  </div>
                  <p className="text-3xl font-bold text-gray-900">{stats.voiceCalls}</p>
                  <p className="text-sm text-gray-600">Voice Calls</p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <div className="flex items-center space-x-2 mb-2">
                    <Phone size={16} className="text-gray-400" />
                  </div>
                  <p className="text-3xl font-bold text-gray-900">{stats.patients}</p>
                  <p className="text-sm text-gray-600">Patients</p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <div className="flex items-center space-x-2 mb-2">
                    <BarChart3 size={16} className="text-gray-400" />
                  </div>
                  <p className="text-3xl font-bold text-gray-900">{stats.satisfaction}</p>
                  <p className="text-sm text-gray-600">Satisfaction Rate</p>
                </div>
              </div>
            </div>
          </div>

          {/* Tab Navigation */}
          <div className="bg-white rounded-t-xl border-b border-gray-200 sticky top-20 z-10">
            <div className="flex space-x-8 px-6">
              {[
                { id: 'appointments', label: 'Appointments', icon: Calendar },
                { id: 'voice-agent', label: 'Voice Agent', icon: Phone },
                { id: 'patients', label: 'Patient Records', icon: Users },
                { id: 'analytics', label: 'Call Analytics', icon: BarChart3 },
                { id: 'settings', label: 'Appointment Analytics', icon: Settings },
              ].map((tab) => {
                const Icon = tab.icon;
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`flex items-center space-x-2 py-4 px-2 border-b-2 transition-colors ${
                      activeTab === tab.id
                        ? 'border-blue-600 text-blue-600'
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
          <div className="bg-white rounded-b-xl shadow-sm border-l border-r border-b border-gray-200 p-6" style={{ height: 'calc(100vh - 380px)', overflowY: 'auto' }}>
            {renderContent()}
          </div>
        </div>
      </div>
    </div>
  );
};

// Tab Components
const AppointmentsTab = () => {
  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]); // Set today as default
  const [statusFilter, setStatusFilter] = useState('all');

  const doctorId = localStorage.getItem('userId');

  useEffect(() => {
    loadAppointments();
  }, [selectedDate, statusFilter]);

  const loadAppointments = async () => {
    try {
      setLoading(true);
      setError(null);
      
      console.log("Loading appointments for doctor:", doctorId);
      console.log("Date filter:", selectedDate);
      console.log("Status filter:", statusFilter);
      
      const response = await doctorAppointmentService.getDoctorAppointments(
        doctorId, 
        selectedDate === "all" ? null : selectedDate,
        statusFilter === "all" ? null : statusFilter
      );
      
      console.log("API response:", response);
      setAppointments(response.appointments || []);
    } catch (err) {
      setError(err.message);
      console.error('Failed to load appointments:', err);
    } finally {
      setLoading(false);
    }
  };

    const handleStatusUpdate = async (appointmentId, newStatus) => {
    try {
        console.log("Updating appointment:", appointmentId, "to status:", newStatus);
        
        const result = await doctorAppointmentService.updateAppointmentStatus(appointmentId, newStatus);
        console.log("Update successful:", result);
        
        await loadAppointments();
    } catch (err) {
        console.error('Failed to update appointment:', err);
        setError(`Failed to update appointment: ${err.message}`);
        
        // Show more detailed error to user
        alert(`Error: ${err.message}. Please check console for details.`);
    }
    };

  // Loading state
  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
        <span className="ml-3 text-gray-600">Loading appointments...</span>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg">
        Error loading appointments: {error}
        <button 
          onClick={loadAppointments}
          className="ml-4 bg-red-600 text-white px-3 py-1 rounded text-sm"
        >
          Try Again
        </button>
      </div>
    );
  }

  // Empty state
  if (appointments.length === 0) {
    return (
        <div>
            {/* Header Section (always visible) */}
            <div className="flex items-center justify-between mb-6">
            <div className="flex items-center space-x-2">
                <Calendar size={20} className="text-gray-600" />
                <h2 className="text-lg font-semibold text-gray-900">Appointment Management</h2>
            </div>
            
            <div className="flex items-center space-x-4">
                {/* Date Filter */}
                <div>
                <label htmlFor="date-filter" className="sr-only">Select date</label>
                <input
                    id="date-filter"
                    type="date"
                    value={selectedDate === "all" ? "" : selectedDate}
                    onChange={(e) => setSelectedDate(e.target.value || "all")}
                    className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
                />
                </div>

                {/* Status Filter */}
                <div>
                <label htmlFor="status-filter" className="sr-only">Filter by status</label>
                <select
                    id="status-filter"
                    value={statusFilter}
                    onChange={(e) => setStatusFilter(e.target.value)}
                    className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
                >
                    <option value="all">All Statuses</option>
                    <option value="booked">Booked</option>
                    <option value="scheduled">Scheduled</option>
                    <option value="completed">Completed</option>
                    <option value="cancelled">Cancelled</option>
                </select>
                </div>

                {/* Refresh Button */}
                <button
                onClick={loadAppointments}
                className="px-3 py-2 bg-blue-500 text-white rounded-lg text-sm hover:bg-blue-600"
                >
                Refresh
                </button>
            </div>
            </div>

            {/* Appointment List OR Empty Message */}
            <div className="space-y-3">
            {appointments.length === 0 ? (
                <div className="text-center py-12 text-gray-500">
                No appointments found for selected filters.
                </div>
            ) : (
                appointments.map((appt) => (
                <div
                    key={appt.appointment_id}
                    className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
                >
                    {/* existing appointment card UI */}
                </div>
                ))
            )}
            </div>
        </div>
        );

  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-2">
          <Calendar size={20} className="text-gray-600" />
          <h2 className="text-lg font-semibold text-gray-900">Appointment Management</h2>
        </div>
        
        <div className="flex items-center space-x-4">
          {/* Date Filter */}
          <div>
            <label htmlFor="date-filter" className="sr-only">Select date</label>
            <input
              id="date-filter"
              type="date"
              value={selectedDate === "all" ? "" : selectedDate}
              onChange={(e) => setSelectedDate(e.target.value || "all")}
              className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
            />
          </div>
          
          {/* Status Filter */}
          <div>
            <label htmlFor="status-filter" className="sr-only">Filter by status</label>
            <select
              id="status-filter"
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
            >
              <option value="all">All Statuses</option>
              <option value="booked">Booked</option>
              <option value="completed">Completed</option>
              <option value="cancelled">Cancelled</option>
            </select>
          </div>
          
          {/* Refresh Button */}
          <button
            onClick={loadAppointments}
            className="px-3 py-2 bg-blue-500 text-white rounded-lg text-sm hover:bg-blue-600"
          >
            Refresh
          </button>
        </div>
      </div>

      <div className="space-y-3">
        {appointments.map((appt) => (
          <div key={appt.appointment_id} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
            <div className="flex items-center space-x-4">
              <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                <User size={16} className="text-blue-600" />
              </div>
              <div>
                <h3 className="font-medium text-gray-900">{appt.patientName}</h3>
                <p className="text-sm text-gray-500">{appt.reason || 'No reason specified'}</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="text-right">
                <p className="text-sm font-medium text-gray-900">{appt.time}</p>
                <p className="text-xs text-gray-500">{appt.date}</p>
              </div>
              
              <span className={`px-3 py-1 text-xs font-medium rounded-full ${
                appt.status === 'completed' ? 'bg-green-100 text-green-700' : 
                appt.status === 'cancelled' ? 'bg-red-100 text-red-700' : 
                appt.status === 'booked' ? 'bg-yellow-100 text-yellow-700' : 
                'bg-blue-100 text-blue-700'
              }`}>
                {appt.status}
              </span>
              
              <div className="flex items-center space-x-2">
                {(appt.status === 'booked' || appt.status === 'scheduled') && (
                  <button 
                    onClick={() => handleStatusUpdate(appt.appointment_id, 'completed')}
                    className="p-1 text-green-600 hover:bg-green-50 rounded"
                    title="Mark as Completed"
                  >
                    <CheckCircle size={16} />
                  </button>
                )}
                
                {(appt.status === 'booked' || appt.status === 'scheduled') && (
                  <button 
                    onClick={() => handleStatusUpdate(appt.appointment_id, 'cancelled')}
                    className="p-1 text-red-600 hover:bg-red-50 rounded"
                    title="Cancel Appointment"
                  >
                    <XCircle size={16} />
                  </button>
                )}
                <ChevronRight size={16} className="text-gray-400" />
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

const VoiceAgentTab = () => {
  return (
    <div className="text-center py-12">
      <Phone size={48} className="text-gray-400 mx-auto mb-4" />
      <h2 className="text-xl font-semibold text-gray-900 mb-2">Voice Agent</h2>
      <p className="text-gray-600 mb-6">Manage your AI voice agent settings and performance metrics.</p>
      <button className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors">
        Configure Voice Agent
      </button>
    </div>
  );
};

const PatientsTab = () => {
  // Hardcoded patient data
  const patients = [
    {
      _id: '1',
      name: 'John Smith',
      email: 'john.smith@email.com',
      phone: '(555) 123-4567',
      status: 'active'
    },
    {
      _id: '2',
      name: 'Sarah Johnson',
      email: 'sarah.j@email.com',
      phone: '(555) 234-5678',
      status: 'active'
    },
    {
      _id: '3',
      name: 'Michael Brown',
      email: 'michael.b@email.com',
      phone: '(555) 345-6789',
      status: 'inactive'
    },
    {
      _id: '4',
      name: 'Emily Davis',
      email: 'emily.d@email.com',
      phone: '(555) 456-7890',
      status: 'active'
    }
  ];

  return (
    <div className="space-y-6">
      {/* Search and Filter Section */}
      <div className="flex justify-between items-center">
        <div className="flex-1 max-w-md">
          <div className="relative">
            <input
              type="text"
              placeholder="Search patients..."
              className="w-full px-4 py-2 border border-gray-300 rounded-lg pr-10"
              disabled
            />
            <button
              className="absolute right-2 top-1/2 transform -translate-y-1/2 text-gray-400"
            >
              🔍
            </button>
          </div>
        </div>
      </div>

      {/* Patients List */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Contact</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {patients.map((patient) => (
              <tr key={patient._id}>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center">
                    <div className="flex-shrink-0 h-10 w-10">
                      <div className="h-10 w-10 rounded-full bg-blue-100 flex items-center justify-center">
                        <User className="h-6 w-6 text-blue-600" />
                      </div>
                    </div>
                    <div className="ml-4">
                      <div className="text-sm font-medium text-gray-900">{patient.name}</div>
                      <div className="text-sm text-gray-500">{patient.email}</div>
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm text-gray-900">{patient.phone}</div>
                  <div className="text-sm text-gray-500">{patient.email}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full 
                    ${patient.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}`}>
                    {patient.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

const AnalyticsTab = () => {
  return (
    <div className="text-center py-12">
      <BarChart3 size={48} className="text-gray-400 mx-auto mb-4" />
      <h2 className="text-xl font-semibold text-gray-900 mb-2">Call Analytics</h2>
      <p className="text-gray-600 mb-6">View practice analytics and performance metrics.</p>
      <button className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors">
        View Analytics
      </button>
    </div>
  );
};

const SettingsTab = () => {
  return (
    <div className="text-center py-12">
      <Settings size={48} className="text-gray-400 mx-auto mb-4" />
      <h2 className="text-xl font-semibold text-gray-900 mb-2">Appointment Analytics</h2>
      <p className="text-gray-600 mb-6">Configure your appointment analytics and reporting settings.</p>
      <button className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors">
        Configure Settings
      </button>
    </div>
  );
};

export default DoctorDashboard;