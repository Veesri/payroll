import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { QRCodeSVG } from 'qrcode.react';

const QRDashboard = () => {
  const [qrData, setQrData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [stats, setStats] = useState({ present_today: 0, absent_today: 0 });

  const fetchActiveQR = useCallback(async () => {
    try {
      const token = localStorage.getItem('token');
      const res = await axios.get(`${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/api/attendance/qr/active`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setQrData(res.data.qr_data);
      setError('');
    } catch (err) {
      if (err.response && err.response.status === 404) {
        setQrData(null);
      } else {
        setError('Failed to fetch QR');
      }
    }
  }, []);

  const generateQR = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const res = await axios.post(`${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/api/attendance/qr/generate`, 
        { expiry_minutes: 1 },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setQrData(res.data.qr_data);
      setError('');
    } catch (err) {
      setError('Failed to generate QR');
    }
    setLoading(false);
  };

  const fetchStats = async () => {
    try {
      const token = localStorage.getItem('token');
      const res = await axios.get(`${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/api/attendance/report`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setStats(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchActiveQR();
    fetchStats();
    const interval = setInterval(() => {
      fetchActiveQR();
      fetchStats();
    }, 10000); // refresh every 10s
    return () => clearInterval(interval);
  }, [fetchActiveQR]);

  return (
    <div className="container mt-4">
      <h2 className="mb-4">Attendance QR Dashboard</h2>
      {error && <div className="alert alert-danger">{error}</div>}
      
      <div className="row">
        <div className="col-md-6">
          <div className="card shadow-sm mb-4">
            <div className="card-body text-center">
              <h5 className="card-title">Dynamic QR Code</h5>
              {qrData ? (
                <div className="my-4">
                  <QRCodeSVG value={qrData.token} size={256} />
                  <p className="mt-3 text-muted">Session: {qrData.session_id}</p>
                  <p className="text-warning">Expires at: {new Date(qrData.expires_at).toLocaleTimeString()}</p>
                </div>
              ) : (
                <div className="my-4 p-5 bg-light rounded text-muted">
                  No active QR code.
                </div>
              )}
              <button 
                className="btn btn-primary btn-lg mt-2" 
                onClick={generateQR} 
                disabled={loading}
              >
                {loading ? 'Generating...' : 'Generate New QR'}
              </button>
            </div>
          </div>
        </div>
        
        <div className="col-md-6">
          <div className="card shadow-sm">
            <div className="card-body">
              <h5 className="card-title">Today's Attendance</h5>
              <div className="d-flex justify-content-around mt-4">
                <div className="text-center">
                  <h2 className="text-success">{stats.present_today}</h2>
                  <p className="text-muted">Present</p>
                </div>
                <div className="text-center">
                  <h2 className="text-danger">{stats.absent_today}</h2>
                  <p className="text-muted">Absent</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default QRDashboard;
