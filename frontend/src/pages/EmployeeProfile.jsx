import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Layout from '../components/Layout';
import { FaUserAlt, FaPhoneAlt, FaEnvelope, FaIdCard, FaBuilding, FaUserCheck } from 'react-icons/fa';

const EmployeeProfile = () => {
    const [profile, setProfile] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    const token = localStorage.getItem('token');
    const headers = { Authorization: `Bearer ${token}` };

    useEffect(() => {
        const fetchProfile = async () => {
            try {
                // Get general user info (specifically the employee id)
                const meRes = await axios.get(`${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/api/auth/me`, { headers });
                const employeeId = meRes.data.employee?.id;

                if (employeeId) {
                    // Fetch full employee details
                    const empRes = await axios.get(`${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/api/employees/${employeeId}`, { headers });
                    setProfile(empRes.data);
                } else {
                    setError('No employee profile associated with this account.');
                }
            } catch (err) {
                setError('Failed to fetch profile details.');
            } finally {
                setLoading(false);
            }
        };

        fetchProfile();
    }, []);

    if (loading) return <Layout><div className="text-center mt-5"><div className="spinner-border text-primary" role="status"></div></div></Layout>;

    return (
        <Layout>
            <div className="slide-up-animation">
                <div className="mb-4">
                    <h2 className="fw-bold mb-0">My Profile</h2>
                </div>

                {error ? (
                    <div className="alert alert-danger">{error}</div>
                ) : (
                    <div className="row g-4">
                        <div className="col-md-4">
                            <div className="card text-center p-4 h-100 shadow-sm border-0">
                                <div className="card-body">
                                    {profile?.photo_url ? (
                                        <img src={`${import.meta.env.VITE_API_URL || 'http://localhost:5000'}${profile.photo_url}`} alt="Profile" className="rounded-circle img-thumbnail mb-3" style={{width: '150px', height: '150px', objectFit: 'cover'}} />
                                    ) : (
                                        <div className="bg-primary text-white rounded-circle d-flex justify-content-center align-items-center mx-auto mb-3 fw-bold" style={{width: '150px', height: '150px', fontSize: '48px'}}>
                                            {profile?.first_name?.[0]}{profile?.last_name?.[0]}
                                        </div>
                                    )}
                                    <h4 className="fw-bold mb-1">{profile?.first_name} {profile?.last_name}</h4>
                                    <span className="badge bg-primary px-3 py-2 rounded-pill">{profile?.designation || 'Employee'}</span>
                                    
                                    <hr className="my-4 border-secondary" />
                                    
                                    <div className="d-flex align-items-center justify-content-center mb-2">
                                        <FaIdCard className="text-muted me-2" />
                                        <span className="text-muted small">Employee ID: EMP-{profile?.id?.toString().padStart(4, '0')}</span>
                                    </div>
                                    <div className="d-flex align-items-center justify-content-center">
                                        <FaBuilding className="text-muted me-2" />
                                        <span className="text-muted small">Dept: {profile?.department || 'Unassigned'}</span>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div className="col-md-8">
                            <div className="card p-4 h-100 shadow-sm border-0">
                                <h4 className="fw-bold mb-4 border-bottom pb-2 border-secondary">Profile Details</h4>
                                
                                <div className="row g-3">
                                    <div className="col-sm-6">
                                        <label className="text-muted small mb-1">First Name</label>
                                        <div className="p-3 bg-dark bg-opacity-20 rounded border border-secondary text-white fw-bold">
                                            {profile?.first_name}
                                        </div>
                                    </div>
                                    <div className="col-sm-6">
                                        <label className="text-muted small mb-1">Last Name</label>
                                        <div className="p-3 bg-dark bg-opacity-20 rounded border border-secondary text-white fw-bold">
                                            {profile?.last_name}
                                        </div>
                                    </div>

                                    <div className="col-sm-6">
                                        <label className="text-muted small mb-1">Email Address</label>
                                        <div className="p-3 bg-dark bg-opacity-20 rounded border border-secondary text-white d-flex align-items-center">
                                            <FaEnvelope className="text-primary me-2" />
                                            <span>{profile?.email}</span>
                                        </div>
                                    </div>
                                    <div className="col-sm-6">
                                        <label className="text-muted small mb-1">Phone Number</label>
                                        <div className="p-3 bg-dark bg-opacity-20 rounded border border-secondary text-white d-flex align-items-center">
                                            <FaPhoneAlt className="text-primary me-2" />
                                            <span>{profile?.phone || 'Not Configured'}</span>
                                        </div>
                                    </div>

                                    <div className="col-sm-6">
                                        <label className="text-muted small mb-1">Designation</label>
                                        <div className="p-3 bg-dark bg-opacity-20 rounded border border-secondary text-white">
                                            {profile?.designation || 'Employee'}
                                        </div>
                                    </div>
                                    <div className="col-sm-6">
                                        <label className="text-muted small mb-1">Employment Status</label>
                                        <div className="p-3 bg-dark bg-opacity-20 rounded border border-secondary text-white d-flex align-items-center">
                                            <FaUserCheck className="text-success me-2" />
                                            <span className="text-capitalize">{profile?.status}</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </Layout>
    );
};

export default EmployeeProfile;
