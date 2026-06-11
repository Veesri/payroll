import React, { useEffect, useState, useContext } from 'react';
import axios from 'axios';
import { AuthContext } from '../context/AuthContext';
import { FaUsers, FaClipboardList } from 'react-icons/fa';
import Layout from '../components/Layout';

const HRDashboard = () => {
    const { user } = useContext(AuthContext);
    const [stats, setStats] = useState({ totalEmployees: 0, activeEmployees: 0 });
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const token = localStorage.getItem('token');
                const headers = { Authorization: `Bearer ${token}` };
                
                const empRes = await axios.get(`${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/api/employees/?per_page=1000`, { headers });
                const employees = empRes.data.employees;
                
                const reportRes = await axios.get(`${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/api/attendance/report`, { headers });
                const report = reportRes.data;
                
                setStats({
                    totalEmployees: employees.length,
                    activeEmployees: employees.filter(e => e.status === 'active').length,
                    presentToday: report.present_today,
                    absentToday: report.absent_today,
                    attendancePercentage: employees.length > 0 ? Math.round((report.present_today / employees.length) * 100) : 0
                });
            } catch (error) {
                console.error("Error fetching data", error);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, []);

    if (loading) return <Layout><div className="text-center mt-5"><div className="spinner-border text-primary" role="status"></div></div></Layout>;

    return (
        <Layout>
            <div className="slide-up-animation">
                <div className="mb-5">
                    <h1 className="fw-bold mb-0">HR Admin Portal</h1>
                    <p className="text-muted">Manage employees and track attendance</p>
                </div>

                <div className="row g-4 mb-5">
                    <div className="col-md-6 col-lg-3">
                        <div className="card h-100 border-0 p-4 dashboard-stat-card" style={{ background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.2) 0%, rgba(99, 102, 241, 0.05) 100%)', borderLeft: '4px solid var(--bs-primary) !important' }}>
                            <div className="d-flex align-items-center justify-content-between">
                                <div>
                                    <h6 className="text-muted text-uppercase fw-bold mb-2">Total Employees</h6>
                                    <h2 className="fw-bold mb-0">{stats.totalEmployees}</h2>
                                </div>
                                <div className="bg-primary text-white p-3 rounded-circle" style={{ opacity: 0.8 }}>
                                    <FaUsers size={24} />
                                </div>
                            </div>
                        </div>
                    </div>
                    <div className="col-md-6 col-lg-3">
                        <div className="card h-100 border-0 p-4 dashboard-stat-card" style={{ background: 'linear-gradient(135deg, rgba(32, 201, 151, 0.2) 0%, rgba(32, 201, 151, 0.05) 100%)', borderLeft: '4px solid #20c997 !important' }}>
                            <div className="d-flex align-items-center justify-content-between">
                                <div>
                                    <h6 className="text-muted text-uppercase fw-bold mb-2">Active Employees</h6>
                                    <h2 className="fw-bold mb-0">{stats.activeEmployees}</h2>
                                </div>
                                <div className="bg-success text-white p-3 rounded-circle" style={{ opacity: 0.8, backgroundColor: '#20c997 !important' }}>
                                    <FaClipboardList size={24} />
                                </div>
                            </div>
                        </div>
                    </div>
                    <div className="col-md-6 col-lg-3">
                        <div className="card h-100 border-0 p-4 dashboard-stat-card" style={{ background: 'linear-gradient(135deg, rgba(245, 158, 11, 0.2) 0%, rgba(245, 158, 11, 0.05) 100%)', borderLeft: '4px solid #f59e0b !important' }}>
                            <div className="d-flex align-items-center justify-content-between">
                                <div>
                                    <h6 className="text-muted text-uppercase fw-bold mb-2">Present Today</h6>
                                    <h2 className="fw-bold mb-0">{stats.presentToday || 0}</h2>
                                </div>
                                <div className="bg-warning text-white p-3 rounded-circle" style={{ opacity: 0.8, backgroundColor: '#f59e0b !important' }}>
                                    <FaUsers size={24} />
                                </div>
                            </div>
                        </div>
                    </div>
                    <div className="col-md-6 col-lg-3">
                        <div className="card h-100 border-0 p-4 dashboard-stat-card" style={{ background: 'linear-gradient(135deg, rgba(220, 53, 69, 0.2) 0%, rgba(220, 53, 69, 0.05) 100%)', borderLeft: '4px solid #dc3545 !important' }}>
                            <div className="d-flex align-items-center justify-content-between">
                                <div>
                                    <h6 className="text-muted text-uppercase fw-bold mb-2">Absent / Leave</h6>
                                    <h2 className="fw-bold mb-0">{stats.absentToday || 0}</h2>
                                </div>
                                <div className="bg-danger text-white p-3 rounded-circle" style={{ opacity: 0.8, backgroundColor: '#dc3545 !important' }}>
                                    <FaClipboardList size={24} />
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </Layout>
    );
};

export default HRDashboard;
