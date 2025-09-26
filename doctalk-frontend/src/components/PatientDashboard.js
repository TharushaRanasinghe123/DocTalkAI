import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { 
  Calendar, 
  Phone, 
  Users, 
  FileText, 
  Bell,
  User,
  Clock,
  CheckCircle,
  XCircle,
  Mic,
  CalendarPlus,
  UserSearch
} from 'lucide-react';

const PatientDashboard = () => {
  const [user, setUser] = useState(null);
  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('appointments');
  const navigate = useNavigate();

  useEffect(() => {
    fetchUserData();
    fetchAppointments();
  }, []);

  const fetchUserData = async () => {
    try {
        const token = localStorage.getItem('token');
        const userId = localStorage.getItem('userId');
        
        // In real app, you'd have a user API endpoint
        const userData = {
            id: userId,
            name: localStorage.getItem('userName') || 'Patient',
            email: localStorage.getItem('userEmail') || '',
            role: 'patient'
        };
        setUser(userData);
        
    } catch (error) {
        console.error('Error fetching user data:', error);
    }
  };

  const fetchAppointments = async () => {
    try {
      const token = localStorage.getItem('token');
      
      // Simulate API call - replace with real endpoint
      setTimeout(() => {
        const mockAppointments = [
          {
            id: '1',
            doctor_name: 'Dr. Smith',
            date: '2024-01-15',
            time: '10:00 AM',
            status: 'booked',
            reason: 'General Checkup'
          },
          {
            id: '2', 
            doctor_name: 'Dr. Johnson',
            date: '2024-01-20',
            time: '2:30 PM',
            status: 'confirmed',
            reason: 'Follow-up Visit'
          }
        ];
        setAppointments(mockAppointments);
        setLoading(false);
      }, 1000);
      
    } catch (error) {
      console.error('Error fetching appointments:', error);
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('userRole');
    localStorage.removeItem('userId');
    localStorage.removeItem('userName');
    localStorage.removeItem('userEmail');
    navigate('/login');
  };

  const sidebarItems = [
    { id: 'appointments', label: 'Appointments', icon: Calendar },
    { id: 'voice-booking', label: 'Voice Booking', icon: Mic },
    { id: 'doctors', label: 'Find Doctors', icon: UserSearch },
    { id: 'records', label: 'Medical Records', icon: FileText },
  ];

  const quickStats = [
    { label: 'Upcoming', value: appointments.length.toString(), sublabel: 'Appointments', color: 'bg-blue-50 text-blue-600' },
    { label: 'Completed', value: '12', sublabel: 'This Year', color: 'bg-green-50 text-green-600' },
  ];

  const renderContent = () => {
    switch(activeTab) {
      case 'voice-booking':
        return <VoiceBookingTab />;
      case 'doctors':
        return <DoctorsTab />;
      case 'records':
        return <RecordsTab />;
      default:
        return <AppointmentsTab appointments={appointments} loading={loading} />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar */}
      <div className="w-64 bg-white shadow-sm border-r border-gray-200">
        {/* Logo */}
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
              <div className="w-6 h-6 bg-white rounded-full flex items-center justify-center">
                <div className="w-3 h-3 bg-blue-600 rounded-full"></div>
              </div>
            </div>
            <div>
              <h1 className="text-lg font-bold text-gray-900">DocTalk AI</h1>
              <p className="text-xs text-gray-500">Patient Portal</p>
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
              <h2 className="text-2xl font-bold text-gray-900">Welcome, {user?.name}</h2>
              <p className="text-sm text-gray-600 mt-1">
                Manage your health appointments with AI-powered booking
              </p>
            </div>
            <div className="flex items-center space-x-4">
              <button className="p-2 text-gray-400 hover:text-gray-600 transition-colors">
                <Bell size={20} />
              </button>
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
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
                    <Calendar size={16} className="text-gray-400" />
                  </div>
                  <p className="text-3xl font-bold text-gray-900">{appointments.length}</p>
                  <p className="text-sm text-gray-600">Upcoming</p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <div className="flex items-center space-x-2 mb-2">
                    <CheckCircle size={16} className="text-gray-400" />
                  </div>
                  <p className="text-3xl font-bold text-gray-900">12</p>
                  <p className="text-sm text-gray-600">Completed</p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <div className="flex items-center space-x-2 mb-2">
                    <UserSearch size={16} className="text-gray-400" />
                  </div>
                  <p className="text-3xl font-bold text-gray-900">5</p>
                  <p className="text-sm text-gray-600">Doctors</p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <div className="flex items-center space-x-2 mb-2">
                    <FileText size={16} className="text-gray-400" />
                  </div>
                  <p className="text-3xl font-bold text-gray-900">8</p>
                  <p className="text-sm text-gray-600">Records</p>
                </div>
              </div>
            </div>
          </div>

          {/* Tab Navigation */}
          <div className="bg-white rounded-t-xl border-b border-gray-200">
            <div className="flex space-x-8 px-6">
              {[
                { id: 'appointments', label: 'Your Appointments', icon: Calendar },
                { id: 'voice-booking', label: 'Voice Booking', icon: Mic },
                { id: 'doctors', label: 'Find Doctors', icon: UserSearch },
                { id: 'records', label: 'Medical Records', icon: FileText },
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
const AppointmentsTab = ({ appointments, loading }) => {
  if (loading) {
    return (
      <div className="text-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
        <p className="text-gray-600 mt-4">Loading appointments...</p>
      </div>
    );
  }

  if (appointments.length === 0) {
    return (
      <div className="text-center py-12">
        <Calendar size={48} className="text-gray-400 mx-auto mb-4" />
        <h3 className="text-xl font-semibold text-gray-900 mb-2">No appointments yet</h3>
        <p className="text-gray-600 mb-6">Book your first appointment to get started</p>
        <Link to="/voice-app">
          <button className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors">
            Book Now
          </button>
        </Link>
      </div>
    );
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-2">
          <Calendar size={20} className="text-gray-600" />
          <h2 className="text-lg font-semibold text-gray-900">Your Appointments</h2>
        </div>
        <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-medium">
          {appointments.length} Upcoming
        </span>
      </div>

      <div className="space-y-4">
        {appointments.map((appointment) => (
          <div key={appointment.id} className="border border-gray-200 rounded-lg p-5 hover:shadow-md transition-shadow">
            <div className="flex justify-between items-start mb-4">
              <div className="flex items-center space-x-4">
                <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                  <User size={16} className="text-blue-600" />
                </div>
                <div>
                  <h3 className="font-semibold text-lg text-gray-800">{appointment.doctor_name}</h3>
                  <p className="text-gray-600">{appointment.reason}</p>
                </div>
              </div>
              <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                appointment.status === 'booked' ? 'bg-blue-100 text-blue-800' :
                appointment.status === 'confirmed' ? 'bg-green-100 text-green-800' :
                appointment.status === 'cancelled' ? 'bg-red-100 text-red-800' :
                'bg-gray-100 text-gray-800'
              }`}>
                {appointment.status}
              </span>
            </div>
            
            <div className="grid grid-cols-2 gap-4 mb-4">
              <div>
                <p className="text-sm text-gray-500">Date</p>
                <p className="font-semibold">{appointment.date}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Time</p>
                <p className="font-semibold">{appointment.time}</p>
              </div>
            </div>
            
            <div className="flex space-x-3">
              <button className="bg-blue-500 text-white px-4 py-2 rounded-lg text-sm hover:bg-blue-600 transition-colors">
                Reschedule
              </button>
              <button className="bg-red-500 text-white px-4 py-2 rounded-lg text-sm hover:bg-red-600 transition-colors">
                Cancel
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

const VoiceBookingTab = () => {
  return (
    <div className="text-center py-12">
      <Mic size={48} className="text-gray-400 mx-auto mb-4" />
      <h2 className="text-xl font-semibold text-gray-900 mb-2">Voice Appointment Booking</h2>
      <p className="text-gray-600 mb-6">Book appointments using our AI voice assistant</p>
      <Link to="/voice-app">
        <button className="bg-gradient-to-r from-blue-500 to-indigo-500 text-white px-8 py-4 rounded-lg hover:from-blue-600 hover:to-indigo-600 transition-all duration-200 shadow-md hover:shadow-lg font-semibold">
          🎤 Start Voice Booking
        </button>
      </Link>
    </div>
  );
};

const DoctorsTab = () => {
  return (
    <div className="text-center py-12">
      <UserSearch size={48} className="text-gray-400 mx-auto mb-4" />
      <h2 className="text-xl font-semibold text-gray-900 mb-2">Find Doctors</h2>
      <p className="text-gray-600 mb-6">Search and connect with healthcare professionals</p>
      <button className="bg-purple-600 text-white px-6 py-3 rounded-lg hover:bg-purple-700 transition-colors">
        👨‍⚕️ Browse Doctors
      </button>
    </div>
  );
};

const RecordsTab = () => {
  return (
    <div className="text-center py-12">
      <FileText size={48} className="text-gray-400 mx-auto mb-4" />
      <h2 className="text-xl font-semibold text-gray-900 mb-2">Medical Records</h2>
      <p className="text-gray-600 mb-6">Access and manage your medical history</p>
      <button className="bg-orange-600 text-white px-6 py-3 rounded-lg hover:bg-orange-700 transition-colors">
        📋 View Records
      </button>
    </div>
  );
};

export default PatientDashboard;