import React, { useEffect, useState, useContext } from 'react';
import axios from 'axios';
import { AuthContext } from '../context/AuthContext';
import { FaClock, FaCalendarAlt, FaMoneyBillWave, FaFileInvoiceDollar, FaQrcode } from 'react-icons/fa';
import { useNavigate } from 'react-router-dom';
import Layout from '../components/Layout';

const EmployeeDashboard = () => {
    const { user } = useContext(AuthContext);
    const [stats, setStats] = useState({
        presentDays: 0,
        leaveBalance: 0,
        netSalary: 0,
        recentActivities: []
    });
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();

    useEffect(() => {
        const fetchDashboardData = async () => {
            try {
                const token = localStorage.getItem('token');
                const headers = { Authorization: `Bearer ${token}` };
                
                // Fetch Attendance
                const attRes = await axios.get(`${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/api/attendance/?per_page=100`, { headers });
                const attendances = attRes.data.attendance;
                const presentDays = attendances.filter(a => a.status === 'present').length;
                
                // Fetch Leaves
                const leaveRes = await axios.get(`${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/api/leaves/?per_page=100`, { headers });
                const leaves = leaveRes.data.leaves;
                const approvedLeaves = leaves.filter(l => l.status === 'approved').length;
                
                // Calculate leave balance (assuming 30 total allowed as an example)
                const totalAllowed = 30;
                const leaveBalance = totalAllowed - approvedLeaves;
                
                // Build recent activities
                let activities = [];
                attendances.slice(0, 3).forEach(a => activities.push({ id: `att-${a.id}`, action: `Checked In`, time: `${a.date} at ${a.check_in}` }));
                leaves.slice(0, 2).forEach(l => activities.push({ id: `lv-${l.id}`, action: `Leave ${l.status}`, time: `Applied on ${l.applied_at}` }));
                activities.sort((a,b) => b.id.localeCompare(a.id));
                
                setStats({
                    presentDays,
                    leaveBalance,
                    netSalary: 45000, // Still placeholder until Phase 5
                    recentActivities: activities.slice(0, 5)
                });
            } catch (error) {
                console.error("Failed to fetch dashboard stats", error);
            } finally {
                setLoading(false);
            }
        };
        fetchDashboardData();
    }, []);

    if (loading) return <Layout><div className="text-center mt-5"><div className="spinner-border text-primary" role="status"></div></div></Layout>;

    return (
        <Layout>
            <div className="slide-up-animation">
                <div className="mb-5">
                    <h1 className="fw-bold mb-0">Employee Dashboard</h1>
                    <p className="text-muted">Welcome back, {user?.username}</p>
                </div>

                <div className="row g-4 mb-5">
                    <div className="col-md-6 col-lg-3">
                        <div className="card h-100 border-0 p-4 dashboard-stat-card" style={{ background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.2) 0%, rgba(99, 102, 241, 0.05) 100%)', borderLeft: '4px solid var(--bs-primary) !important' }}>
                            <div className="d-flex align-items-center justify-content-between">
                                <div>
                                    <h6 className="text-muted text-uppercase fw-bold mb-2">Days Present</h6>
                                    <h2 className="fw-bold mb-0">{stats.presentDays} <small className="text-muted fs-6">/ 22</small></h2>
                                </div>
                                <div className="bg-primary text-white p-3 rounded-circle" style={{ opacity: 0.8 }}>
                                    <FaClock size={24} />
                                </div>
                            </div>
                        </div>
                    </div>
                    <div className="col-md-6 col-lg-3">
                        <div className="card h-100 border-0 p-4 dashboard-stat-card" style={{ background: 'linear-gradient(135deg, rgba(32, 201, 151, 0.2) 0%, rgba(32, 201, 151, 0.05) 100%)', borderLeft: '4px solid #20c997 !important' }}>
                            <div className="d-flex align-items-center justify-content-between">
                                <div>
                                    <h6 className="text-muted text-uppercase fw-bold mb-2">Leave Balance</h6>
                                    <h2 className="fw-bold mb-0">{stats.leaveBalance}</h2>
                                </div>
                                <div className="bg-success text-white p-3 rounded-circle" style={{ opacity: 0.8, backgroundColor: '#20c997 !important' }}>
                                    <FaCalendarAlt size={24} />
                                </div>
                            </div>
                        </div>
                    </div>
                    <div className="col-md-6 col-lg-3">
                        <div className="card h-100 border-0 p-4 dashboard-stat-card" style={{ background: 'linear-gradient(135deg, rgba(245, 158, 11, 0.2) 0%, rgba(245, 158, 11, 0.05) 100%)', borderLeft: '4px solid #f59e0b !important' }}>
                            <div className="d-flex align-items-center justify-content-between">
                                <div>
                                    <h6 className="text-muted text-uppercase fw-bold mb-2">Net Salary</h6>
                                    <h2 className="fw-bold mb-0">₹{stats.netSalary.toLocaleString()}</h2>
                                </div>
                                <div className="bg-warning text-white p-3 rounded-circle" style={{ opacity: 0.8, backgroundColor: '#f59e0b !important' }}>
                                    <FaMoneyBillWave size={24} />
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    {/* Employee QR Scan */}
                    <div className="col-md-6 col-lg-3" onClick={() => navigate('/employee/qr-scan')} style={{ cursor: 'pointer' }}>
                        <div className="card h-100 border-0 p-4 dashboard-stat-card" style={{ background: 'linear-gradient(135deg, rgba(13, 202, 240, 0.2) 0%, rgba(13, 202, 240, 0.05) 100%)', borderLeft: '4px solid #0dcaf0 !important' }}>
                            <div className="d-flex align-items-center justify-content-between">
                                <div>
                                    <h6 className="text-muted text-uppercase fw-bold mb-2">Scan QR</h6>
                                    <p className="text-muted mb-0 small">Mark Attendance</p>
                                </div>
                                <div className="bg-info text-white p-3 rounded-circle" style={{ opacity: 0.8 }}>
                                    <FaQrcode size={24} />
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div className="row g-4">
                    <div className="col-lg-8">
                        <div className="card border-0 p-4 h-100">
                            <h4 className="fw-bold mb-4">Recent Activities</h4>
                            <div className="timeline-container">
                                {stats.recentActivities.map(activity => (
                                    <div key={activity.id} className="d-flex mb-3 align-items-center p-3 rounded hover-bg" style={{ border: '1px solid rgba(255,255,255,0.1)'}}>
                                        <div className="bg-primary rounded-circle me-3" style={{width: '12px', height: '12px'}}></div>
                                        <div>
                                            <h6 className="mb-1 fw-bold">{activity.action}</h6>
                                            <small className="text-muted">{activity.time}</small>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                    <div className="col-lg-4">
                        <div className="card border-0 p-4 h-100" style={{ background: 'linear-gradient(135deg, rgba(32, 201, 151, 0.1) 0%, rgba(32, 201, 151, 0.02) 100%)' }}>
                            <h4 className="fw-bold mb-4">Latest Payslip</h4>
                            <div className="text-center py-4">
                                <FaFileInvoiceDollar size={48} className="text-success mb-3" />
                                <h5>October 2023</h5>
                                <p className="text-muted small">Generated on Oct 31, 2023</p>
                                <button className="btn btn-outline-success mt-2 w-100 fw-bold">Download PDF</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </Layout>
    );
};

export default EmployeeDashboard;
