import React, { useEffect, useState, useContext } from 'react';
import axios from 'axios';
import { AuthContext } from '../context/AuthContext';
import { FaUsers, FaBuilding, FaQrcode, FaEnvelope } from 'react-icons/fa';
import { useNavigate } from 'react-router-dom';
import Layout from '../components/Layout';

const SuperAdminDashboard = () => {
    const { user } = useContext(AuthContext);
    const [departments, setDepartments] = useState([]);
    const [employees, setEmployees] = useState([]);
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();

    useEffect(() => {
        const fetchData = async () => {
            try {
                const token = localStorage.getItem('token');
                const headers = { Authorization: `Bearer ${token}` };
                
                const [deptRes, empRes] = await Promise.all([
                    axios.get(`${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/api/departments/`, { headers }),
                    axios.get(`${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/api/employees/`, { headers })
                ]);
                
                setDepartments(deptRes.data);
                setEmployees(empRes.data.employees || []);
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
                    <h1 className="fw-bold mb-0">Super Admin Portal</h1>
                    <p className="text-muted">Welcome back, {user?.username}</p>
                </div>

            <div className="row g-4 mb-5">
                <div className="col-md-6 col-lg-3">
                    <div className="card h-100 border-0 p-4 dashboard-stat-card" style={{ background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.2) 0%, rgba(99, 102, 241, 0.05) 100%)', borderLeft: '4px solid var(--bs-primary) !important' }}>
                        <div className="d-flex align-items-center justify-content-between">
                            <div>
                                <h6 className="text-muted text-uppercase fw-bold mb-2">Total Employees</h6>
                                <h2 className="fw-bold mb-0">{employees.length}</h2>
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
                                <h6 className="text-muted text-uppercase fw-bold mb-2">Total Departments</h6>
                                <h2 className="fw-bold mb-0">{departments.length}</h2>
                            </div>
                            <div className="bg-success text-white p-3 rounded-circle" style={{ opacity: 0.8, backgroundColor: '#20c997 !important' }}>
                                <FaBuilding size={24} />
                            </div>
                        </div>
                    </div>
                </div>
                
                {/* QR Access */}
                <div className="col-md-6 col-lg-3" onClick={() => navigate('/admin/qr-dashboard')} style={{ cursor: 'pointer' }}>
                    <div className="card h-100 border-0 p-4 dashboard-stat-card" style={{ background: 'linear-gradient(135deg, rgba(255, 193, 7, 0.2) 0%, rgba(255, 193, 7, 0.05) 100%)', borderLeft: '4px solid #ffc107 !important' }}>
                        <div className="d-flex align-items-center justify-content-between">
                            <div>
                                <h6 className="text-muted text-uppercase fw-bold mb-2">Display QR</h6>
                                <p className="text-muted mb-0 small">Open QR for Scans</p>
                            </div>
                            <div className="bg-warning text-dark p-3 rounded-circle" style={{ opacity: 0.8 }}>
                                <FaQrcode size={24} />
                            </div>
                        </div>
                    </div>
                </div>

                {/* Email Dashboard Access */}
                <div className="col-md-6 col-lg-3" onClick={() => navigate('/admin/email-dashboard')} style={{ cursor: 'pointer' }}>
                    <div className="card h-100 border-0 p-4 dashboard-stat-card" style={{ background: 'linear-gradient(135deg, rgba(220, 53, 69, 0.2) 0%, rgba(220, 53, 69, 0.05) 100%)', borderLeft: '4px solid #dc3545 !important' }}>
                        <div className="d-flex align-items-center justify-content-between">
                            <div>
                                <h6 className="text-muted text-uppercase fw-bold mb-2">Email Tools</h6>
                                <p className="text-muted mb-0 small">Manage Payslips</p>
                            </div>
                            <div className="bg-danger text-white p-3 rounded-circle" style={{ opacity: 0.8 }}>
                                <FaEnvelope size={24} />
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div className="row g-4">
                <div className="col-lg-6">
                    <div className="card border-0 p-4 h-100">
                        <h4 className="fw-bold mb-4">Departments</h4>
                        <div className="table-responsive">
                            <table className="table table-borderless table-hover text-white align-middle">
                                <thead className="text-muted border-bottom border-secondary">
                                    <tr>
                                        <th>Name</th>
                                        <th>Description</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {departments.map(dept => (
                                        <tr key={dept.id}>
                                            <td className="fw-bold">{dept.name}</td>
                                            <td>{dept.description || '-'}</td>
                                        </tr>
                                    ))}
                                    {departments.length === 0 && <tr><td colSpan="2" className="text-center text-muted py-3">No departments found</td></tr>}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
                <div className="col-lg-6">
                    <div className="card border-0 p-4 h-100">
                        <h4 className="fw-bold mb-4">Recent Employees</h4>
                        <div className="table-responsive">
                            <table className="table table-borderless table-hover text-white align-middle">
                                <thead className="text-muted border-bottom border-secondary">
                                    <tr>
                                        <th>Name</th>
                                        <th>Department</th>
                                        <th>Role</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {employees.slice(0,5).map(emp => (
                                        <tr key={emp.id}>
                                            <td className="fw-bold">
                                                <div className="d-flex align-items-center">
                                                    <div className="bg-primary text-white rounded-circle d-flex justify-content-center align-items-center me-3" style={{width: '35px', height: '35px', fontSize: '14px'}}>
                                                        {emp.first_name[0]}{emp.last_name[0]}
                                                    </div>
                                                    {emp.first_name} {emp.last_name}
                                                </div>
                                            </td>
                                            <td>{emp.department || '-'}</td>
                                            <td><span className="badge bg-secondary">{emp.designation || 'Employee'}</span></td>
                                        </tr>
                                    ))}
                                    {employees.length === 0 && <tr><td colSpan="3" className="text-center text-muted py-3">No employees found</td></tr>}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
            </div>
        </Layout>
    );
};

export default SuperAdminDashboard;
