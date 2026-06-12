import React, { useState, useEffect } from 'react';
import axios from 'axios';

const EmailDashboard = () => {
    const [stats, setStats] = useState({ total: 0, delivered: 0, failed: 0, pending: 0 });
    const [logs, setLogs] = useState([]);
    const [queue, setQueue] = useState([]);

    const fetchData = async () => {
        try {
            const token = localStorage.getItem('token');
            const headers = { Authorization: `Bearer ${token}` };
            
            const [statsRes, logsRes, queueRes] = await Promise.all([
                axios.get(`${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/api/email/dashboard`, { headers }),
                axios.get(`${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/api/email/logs`, { headers }),
                axios.get(`${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/api/email/queue`, { headers })
            ]);
            
            setStats(statsRes.data);
            setLogs(logsRes.data);
            setQueue(queueRes.data);
        } catch (error) {
            console.error("Failed to fetch email dashboard data", error);
        }
    };

    useEffect(() => {
        fetchData();
        const interval = setInterval(fetchData, 10000); // refresh queue every 10s
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="container-fluid py-4">
            <h2 className="mb-4 text-primary fw-bold">Email Campaign Dashboard</h2>
            
            <div className="row mb-5">
                <div className="col-md-3">
                    <div className="card shadow-sm border-0 bg-primary text-white">
                        <div className="card-body">
                            <h6 className="card-title text-uppercase mb-1" style={{opacity: 0.8}}>Total Emails</h6>
                            <h2 className="mb-0 fw-bold">{stats.total}</h2>
                        </div>
                    </div>
                </div>
                <div className="col-md-3">
                    <div className="card shadow-sm border-0 bg-success text-white">
                        <div className="card-body">
                            <h6 className="card-title text-uppercase mb-1" style={{opacity: 0.8}}>Delivered</h6>
                            <h2 className="mb-0 fw-bold">{stats.delivered}</h2>
                        </div>
                    </div>
                </div>
                <div className="col-md-3">
                    <div className="card shadow-sm border-0 bg-warning text-dark">
                        <div className="card-body">
                            <h6 className="card-title text-uppercase mb-1" style={{opacity: 0.8}}>Pending / Queued</h6>
                            <h2 className="mb-0 fw-bold">{stats.pending}</h2>
                        </div>
                    </div>
                </div>
                <div className="col-md-3">
                    <div className="card shadow-sm border-0 bg-danger text-white">
                        <div className="card-body">
                            <h6 className="card-title text-uppercase mb-1" style={{opacity: 0.8}}>Failed</h6>
                            <h2 className="mb-0 fw-bold">{stats.failed}</h2>
                        </div>
                    </div>
                </div>
            </div>

            <div className="row">
                <div className="col-md-6 mb-4">
                    <div className="card shadow-sm border-0 h-100">
                        <div className="card-header bg-white border-bottom-0 pt-4">
                            <h5 className="mb-0 text-dark">Active Queue</h5>
                        </div>
                        <div className="card-body p-0">
                            <div className="table-responsive">
                                <table className="table table-hover align-middle mb-0">
                                    <thead className="table-light">
                                        <tr>
                                            <th>Recipient</th>
                                            <th>Subject</th>
                                            <th>Status</th>
                                            <th>Created</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {queue.length === 0 ? (
                                            <tr><td colSpan="4" className="text-center text-muted py-4">Queue is empty</td></tr>
                                        ) : queue.map(q => (
                                            <tr key={q.id}>
                                                <td>{q.recipient}</td>
                                                <td className="text-truncate" style={{maxWidth: '150px'}}>{q.subject}</td>
                                                <td><span className="badge bg-warning">{q.status}</span></td>
                                                <td className="text-muted small">{q.created_at}</td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>

                <div className="col-md-6 mb-4">
                    <div className="card shadow-sm border-0 h-100">
                        <div className="card-header bg-white border-bottom-0 pt-4">
                            <h5 className="mb-0 text-dark">Recent Delivery Logs</h5>
                        </div>
                        <div className="card-body p-0">
                            <div className="table-responsive">
                                <table className="table table-hover align-middle mb-0">
                                    <thead className="table-light">
                                        <tr>
                                            <th>Recipient</th>
                                            <th>Status</th>
                                            <th>Date</th>
                                            <th>Details</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {logs.length === 0 ? (
                                            <tr><td colSpan="4" className="text-center text-muted py-4">No logs available</td></tr>
                                        ) : logs.map(l => (
                                            <tr key={l.id}>
                                                <td>{l.recipient}</td>
                                                <td>
                                                    <span className={`badge ${l.status === 'sent' ? 'bg-success' : 'bg-danger'}`}>
                                                        {l.status}
                                                    </span>
                                                </td>
                                                <td className="text-muted small">{l.sent_at}</td>
                                                <td className="text-truncate small text-danger" style={{maxWidth: '150px'}} title={l.error_message}>
                                                    {l.error_message || 'OK'}
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default EmailDashboard;
