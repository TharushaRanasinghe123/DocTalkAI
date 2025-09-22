// src/services/doctorAppointmentService.js
const API_BASE = 'http://localhost:8001/api/v1';

export const doctorAppointmentService = {
  // Get doctor's appointments with filters
  getDoctorAppointments: async (doctorId, date = null, status = null) => {
    try {
      const token = localStorage.getItem('token');
      let url = `${API_BASE}/doctors/${doctorId}/appointments`;
      
      // Add query parameters
      const params = new URLSearchParams();
      if (date) params.append('appointment_date', date);
      if (status && status !== 'all') params.append('status', status);
      
      if (params.toString()) {
        url += `?${params.toString()}`;
      }
      
      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${token}`,
        }
      });
      
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      return await response.json();
    } catch (error) {
      console.error('Error fetching appointments:', error);
      throw error;
    }
  },

  // Update appointment status
  updateAppointmentStatus: async (appointmentId, status) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_BASE}/appointments/${appointmentId}/status`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({ status })
      });
      
      if (!response.ok) {
        // Get more detailed error info
        const errorText = await response.text();
        throw new Error(`HTTP error! status: ${response.status}, details: ${errorText}`);
        }
      return await response.json();
    } catch (error) {
      console.error('Error updating appointment:', error);
      throw error;
    }
  }
};