import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Layout from '../components/Layout';
import { FaUserCheck, FaUserSlash, FaUserAlt } from 'react-icons/fa';

const UserManagement = () => {
    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    const token = localStorage.getItem('token');
    const headers = { Authorization: `Bearer ${token}` };

    const fetchUsers = async () => {
        try {
            const res = await axios.get(`${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/api/auth/users`, { headers });
            setUsers(res.data);
        } catch (err) {
            setError('Failed to fetch user accounts.');
        } finally {
            setLoading(false);
        }
    };

    const handleApprove = async (id) => {
        try {
            await axios.post(`${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/api/auth/users/${id}/approve`, {}, { headers });
            fetchUsers();
        } catch (err) {
            alert('Failed to approve user.');
        }
    };

    const handleToggleActive = async (id) => {
        try {
            await axios.post(`${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/api/auth/users/${id}/toggle-active`, {}, { headers });
            fetchUsers();
        } catch (err) {
            alert('Failed to toggle active status.');
        }
    };

    useEffect(() => {
        fetchUsers();
    }, []);

    if (loading) return <Layout><div className="text-center mt-5"><div className="spinner-border text-primary" role="status"></div></div></Layout>;

    return (
        <Layout>
            <div className="slide-up-animation">
                <div className="d-flex justify-content-between align-items-center mb-4">
                    <h2 className="fw-bold mb-0">User Account Approvals</h2>
                </div>

                {error && <div className="alert alert-danger">{error}</div>}

                <div className="card border-0 p-4 shadow-sm">
                    <div className="table-responsive">
                        <table className="table table-borderless table-hover text-white align-middle mb-0">
                            <thead className="text-muted border-bottom border-secondary">
                                <tr>
                                    <th>Full Name</th>
                                    <th>Username</th>
                                    <th>Email</th>
                                    <th>Requested Role</th>
                                    <th>Approval Status</th>
                                    <th>Active Status</th>
                                    <th className="text-end">Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {users.map(u => (
                                    <tr key={u.id}>
                                        <td>
                                            <div className="d-flex align-items-center">
                                                <div className="bg-primary text-white rounded-circle d-flex justify-content-center align-items-center me-3" style={{width: '35px', height: '35px'}}>
                                                    <FaUserAlt />
                                                </div>
                                                <div className="fw-bold">{u.first_name} {u.last_name}</div>
                                            </div>
                                        </td>
                                        <td><code>{u.username}</code></td>
                                        <td>{u.email}</td>
                                        <td>
                                            <span className={`badge ${u.role === 'hr_admin' ? 'bg-info' : 'bg-secondary'}`}>
                                                {u.role === 'hr_admin' ? 'HR Admin' : 'Employee'}
                                            </span>
                                        </td>
                                        <td>
                                            {u.is_approved ? (
                                                <span className="badge bg-success">Approved</span>
                                            ) : (
                                                <span className="badge bg-warning text-dark">Pending Approval</span>
                                            )}
                                        </td>
                                        <td>
                                            {u.is_active ? (
                                                <span className="badge bg-success">Enabled</span>
                                            ) : (
                                                <span className="badge bg-danger">Disabled</span>
                                            )}
                                        </td>
                                        <td className="text-end">
                                            {!u.is_approved && (
                                                <button className="btn btn-sm btn-success me-2" onClick={() => handleApprove(u.id)}>
                                                    <FaUserCheck className="me-1" /> Approve
                                                </button>
                                            )}
                                            <button className={`btn btn-sm ${u.is_active ? 'btn-outline-danger' : 'btn-outline-success'}`} onClick={() => handleToggleActive(u.id)}>
                                                {u.is_active ? (
                                                    <><FaUserSlash className="me-1" /> Disable</>
                                                ) : (
                                                    <><FaUserCheck className="me-1" /> Enable</>
                                                )}
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                                {users.length === 0 && (
                                    <tr>
                                        <td colSpan="7" className="text-center py-4 text-muted">
                                            No user accounts registered.
                                        </td>
                                    </tr>
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </Layout>
    );
};

export default UserManagement;
