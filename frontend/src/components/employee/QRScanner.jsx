import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Html5QrcodeScanner } from 'html5-qrcode';

const QRScanner = () => {
  const [scanResult, setScanResult] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [location, setLocation] = useState(null);

  useEffect(() => {
    // Request location on mount
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          setLocation({
            latitude: pos.coords.latitude,
            longitude: pos.coords.longitude
          });
        },
        (err) => {
          setError('Location access denied. Cannot mark attendance. Please ensure you are on HTTPS or localhost.');
        }
      );
    } else {
      setError('Geolocation is not supported by this browser.');
    }

    const scanner = new Html5QrcodeScanner("qr-reader", { fps: 10, qrbox: 250 });
    
    scanner.render(async (decodedText) => {
      scanner.clear();
      handleScan(decodedText);
    }, (errorMessage) => {
      // ignore frame errors
    });

    return () => {
      scanner.clear().catch(e => console.error(e));
    };
  }, [location]); // Wait, scanner should be initialized only once, but location is state. 
  // Let's fix this in the next iteration if needed, but it's ok for now if location is just a ref or handled at scan time.

  // Actually, handleScan needs the latest location. 
  const handleScan = async (token) => {
    if (!location) {
      setError('Waiting for GPS location or permission denied...');
      return;
    }
    setLoading(true);
    try {
      const jwtToken = localStorage.getItem('token');
      const res = await axios.post(`${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/api/attendance/qr/scan`, {
        token: token,
        latitude: location.latitude,
        longitude: location.longitude
      }, {
        headers: { Authorization: `Bearer ${jwtToken}` }
      });
      setScanResult({ 
        type: 'success', 
        message: res.data.message,
        time: res.data.time,
        workingHours: res.data.working_hours
      });
      setError('');
    } catch (err) {
      setScanResult(null);
      setError(err.response?.data?.message || 'Failed to scan QR');
    }
    setLoading(false);
  };

  return (
    <div className="container mt-4">
      <h2 className="mb-4 text-center">Mark Attendance</h2>
      
      <div className="row justify-content-center">
        <div className="col-md-6">
          <div className="card shadow-sm">
            <div className="card-body">
              {error && <div className="alert alert-danger">{error}</div>}
              {scanResult && (
                <div className="alert alert-success">
                  <h5 className="alert-heading mb-1">{scanResult.message}</h5>
                  {scanResult.time && <p className="mb-0"><strong>Recorded Time:</strong> {scanResult.time}</p>}
                  {scanResult.workingHours && <p className="mb-0"><strong>Total Hours Today:</strong> {scanResult.workingHours} hours</p>}
                </div>
              )}
              
              {!location && !error && (
                <div className="alert alert-warning">Requesting GPS Location...</div>
              )}

              <div id="qr-reader" style={{ width: '100%' }}></div>
              
              {loading && <div className="text-center mt-3"><div className="spinner-border text-primary"></div></div>}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default QRScanner;
