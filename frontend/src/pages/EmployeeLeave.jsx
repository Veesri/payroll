import React, { useEffect, useState, useContext } from 'react';
import axios from 'axios';
import { AuthContext } from '../context/AuthContext';
import { FaCalendarPlus, FaCalendarCheck } from 'react-icons/fa';
import Layout from '../components/Layout';

const EmployeeLeave = () => {
    const { user } = useContext(AuthContext);
    const [leaves, setLeaves] = useState([]);
    const [leaveTypes, setLeaveTypes] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showModal, setShowModal] = useState(false);
    
    const [formData, setFormData] = useState({
        leave_type_id: '',
        from_date: '',
        to_date: '',
        reason: ''
    });

    const [page, setPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);
    
    const token = localStorage.getItem('token');
    const headers = { Authorization: `Bearer ${token}` };

    const fetchLeaves = async () => {
        try {
            const res = await axios.get(`${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/api/leaves/?page=${page}`, { headers });
            setLeaves(res.data.leaves);
            setTotalPages(res.data.pages);
        } catch (error) {
            console.error("Failed to fetch leaves", error);
        } finally {
            setLoading(false);
        }
    };

    const fetchLeaveTypes = async () => {
        try {
            const res = await axios.get(`${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/api/leaves/types`, { headers });
            setLeaveTypes(res.data);
            if (res.data.length > 0) {
                setFormData(f => ({...f, leave_type_id: res.data[0].id}));
            }
        } catch (error) {
            console.error("Failed to fetch leave types", error);
        }
    };

    useEffect(() => {
        fetchLeaveTypes();
    }, []);

    useEffect(() => {
        fetchLeaves();
    }, [page]);

    const handleApplyLeave = async (e) => {
        e.preventDefault();
        try {
            await axios.post(`${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/api/leaves/`, formData, { headers });
            alert("Leave application submitted successfully");
            setShowModal(false);
            setFormData({...formData, reason: '', from_date: '', to_date: ''});
            fetchLeaves();
        } catch (error) {
            alert(error.response?.data?.message || "Failed to apply for leave");
        }
    };

    const getStatusBadge = (status) => {
        switch(status) {
            case 'approved': return 'bg-success';
            case 'rejected': return 'bg-danger';
            default: return 'bg-warning text-dark';
        }
    };

    if (loading && page === 1) return <Layout><div className="text-center mt-5"><div className="spinner-border text-primary" role="status"></div></div></Layout>;

    return (
        <Layout>
            <div className="slide-up-animation">
                <div className="mb-5 d-flex justify-content-between align-items-center">
                    <div>
                        <h1 className="fw-bold mb-0">Leave Management</h1>
                        <p className="text-muted">Apply for leave and view your balance</p>
                    </div>
                    <button className="btn btn-primary d-flex align-items-center gap-2" onClick={() => setShowModal(true)}>
                        <FaCalendarPlus /> Apply Leave
                    </button>
                </div>

                <div className="card border-0 p-4">
                    <h4 className="fw-bold mb-4 d-flex align-items-center gap-2"><FaCalendarCheck /> Leave History</h4>
                    <div className="table-responsive">
                        <table className="table table-borderless table-hover text-white align-middle">
                            <thead className="text-muted border-bottom border-secondary">
                                <tr>
                                    <th>Type</th>
                                    <th>From Date</th>
                                    <th>To Date</th>
                                    <th>Reason</th>
                                    <th>Applied On</th>
                                    <th>Status</th>
                                    <th>Comments</th>
                                </tr>
                            </thead>
                            <tbody>
                                {leaves.map(leave => (
                                    <tr key={leave.id}>
                                        <td className="fw-bold">{leave.leave_type}</td>
                                        <td>{leave.from_date}</td>
                                        <td>{leave.to_date}</td>
                                        <td><span className="d-inline-block text-truncate" style={{maxWidth: '150px'}} title={leave.reason}>{leave.reason}</span></td>
                                        <td>{leave.applied_at}</td>
                                        <td>
                                            <span className={`badge ${getStatusBadge(leave.status)}`}>
                                                {leave.status.toUpperCase()}
                                            </span>
                                        </td>
                                        <td><span className="text-muted fst-italic">{leave.comments || '-'}</span></td>
                                    </tr>
                                ))}
                                {leaves.length === 0 && (
                                    <tr>
                                        <td colSpan="7" className="text-center text-muted py-5">
                                            No leave records found.
                                        </td>
                                    </tr>
                                )}
                            </tbody>
                        </table>
                    </div>
                    
                    {totalPages > 1 && (
                        <div className="d-flex justify-content-center mt-4">
                            <button className="btn btn-outline-primary me-2" disabled={page === 1} onClick={() => setPage(page - 1)}>Previous</button>
                            <span className="align-self-center mx-3 text-muted">Page {page} of {totalPages}</span>
                            <button className="btn btn-outline-primary ms-2" disabled={page === totalPages} onClick={() => setPage(page + 1)}>Next</button>
                        </div>
                    )}
                </div>
            </div>

            {/* Apply Leave Modal */}
            {showModal && (
                <div className="modal d-block" style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
                    <div className="modal-dialog modal-dialog-centered">
                        <div className="modal-content border-0 shadow-lg" style={{ background: 'rgba(20, 20, 30, 0.98)', backdropFilter: 'blur(10px)' }}>
                            <div className="modal-header border-bottom border-secondary">
                                <h5 className="modal-title fw-bold text-white">Apply for Leave</h5>
                                <button type="button" className="btn-close btn-close-white" onClick={() => setShowModal(false)}></button>
                            </div>
                            <div className="modal-body p-4">
                                <form onSubmit={handleApplyLeave}>
                                    <div className="mb-3">
                                        <label className="form-label text-white">Leave Type</label>
                                        <select className="form-select form-control bg-dark text-light border-secondary" value={formData.leave_type_id} onChange={e => setFormData({...formData, leave_type_id: e.target.value})} required>
                                            {leaveTypes.map(t => (
                                                <option key={t.id} value={t.id}>{t.name} ({t.days_allowed} days/yr)</option>
                                            ))}
                                        </select>
                                    </div>
                                    <div className="row mb-3">
                                        <div className="col-md-6">
                                            <label className="form-label text-white">From Date</label>
                                            <input type="date" className="form-control bg-dark text-light border-secondary" value={formData.from_date} onChange={e => setFormData({...formData, from_date: e.target.value})} required />
                                        </div>
                                        <div className="col-md-6">
                                            <label className="form-label text-white">To Date</label>
                                            <input type="date" className="form-control bg-dark text-light border-secondary" value={formData.to_date} onChange={e => setFormData({...formData, to_date: e.target.value})} required />
                                        </div>
                                    </div>
                                    <div className="mb-4">
                                        <label className="form-label text-white">Reason</label>
                                        <textarea className="form-control bg-dark text-light border-secondary" rows="3" value={formData.reason} onChange={e => setFormData({...formData, reason: e.target.value})} required></textarea>
                                    </div>
                                    <div className="d-flex justify-content-end gap-2">
                                        <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)}>Cancel</button>
                                        <button type="submit" className="btn btn-primary">Submit Application</button>
                                    </div>
                                </form>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </Layout>
    );
};

export default EmployeeLeave;
