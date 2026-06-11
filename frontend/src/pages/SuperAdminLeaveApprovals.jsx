import React, { useEffect, useState, useContext } from 'react';
import axios from 'axios';
import { AuthContext } from '../context/AuthContext';
import { FaCheckCircle, FaTimesCircle, FaDownload } from 'react-icons/fa';
import Layout from '../components/Layout';

const SuperAdminLeaveApprovals = () => {
    const { user } = useContext(AuthContext);
    const [leaves, setLeaves] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showModal, setShowModal] = useState(false);
    const [currentLeave, setCurrentLeave] = useState(null);
    const [action, setAction] = useState('approve');
    const [comments, setComments] = useState('');
    
    const [page, setPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);
    const [filterStatus, setFilterStatus] = useState('');
    
    const token = localStorage.getItem('token');
    const headers = { Authorization: `Bearer ${token}` };

    const fetchLeaves = async () => {
        try {
            // Because user.role is super_admin, backend will only return approval_level='super_admin'
            const res = await axios.get(`${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/api/leaves/?page=${page}&per_page=15&status=${filterStatus}`, { headers });
            setLeaves(res.data.leaves);
            setTotalPages(res.data.pages);
        } catch (error) {
            console.error("Failed to fetch leaves", error);
        } finally {
            setLoading(false);
        }
    };

    const handleExportExcel = async () => {
        try {
            const res = await axios.get(`${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/api/leaves/export/excel?status=${filterStatus}`, {
                headers,
                responseType: 'blob'
            });
            const url = window.URL.createObjectURL(new Blob([res.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', 'HR_Leave_Report.xlsx');
            document.body.appendChild(link);
            link.click();
            link.parentNode.removeChild(link);
        } catch (error) {
            alert("Failed to export Excel report.");
        }
    };

    useEffect(() => {
        fetchLeaves();
    }, [page, filterStatus]);

    const handleProcessLeave = async (e) => {
        e.preventDefault();
        try {
            await axios.put(`${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/api/leaves/${currentLeave.id}/${action}`, { comments }, { headers });
            alert(`Leave ${action}d successfully`);
            setShowModal(false);
            setCurrentLeave(null);
            setComments('');
            fetchLeaves();
        } catch (error) {
            alert(error.response?.data?.message || "Failed to process leave");
        }
    };

    const openProcessModal = (leave, type) => {
        setCurrentLeave(leave);
        setAction(type);
        setComments('');
        setShowModal(true);
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
                <div className="d-flex justify-content-between align-items-center mb-5">
                    <div>
                        <h1 className="fw-bold mb-0 text-warning">HR Leave Escalarions</h1>
                        <p className="text-muted">Review and process leave requests submitted by HR Administrators</p>
                    </div>
                    <button className="btn btn-outline-success border-secondary text-success" onClick={handleExportExcel}>
                        <FaDownload className="me-2" /> Export Excel
                    </button>
                </div>

                <div className="card border-0 p-4">
                    <div className="row mb-4">
                        <div className="col-md-3">
                            <select className="form-select bg-dark text-light border-secondary" value={filterStatus} onChange={e => {setFilterStatus(e.target.value); setPage(1);}}>
                                <option value="">All Statuses</option>
                                <option value="pending">Pending</option>
                                <option value="approved">Approved</option>
                                <option value="rejected">Rejected</option>
                            </select>
                        </div>
                    </div>
                    <div className="table-responsive">
                        <table className="table table-borderless table-hover text-white align-middle">
                            <thead className="text-muted border-bottom border-secondary">
                                <tr>
                                    <th>HR Admin</th>
                                    <th>Leave Type</th>
                                    <th>Date Range</th>
                                    <th>Reason</th>
                                    <th>Applied On</th>
                                    <th>Status</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {leaves.map(leave => (
                                    <tr key={leave.id}>
                                        <td className="fw-bold text-warning">{leave.employee_name}</td>
                                        <td>{leave.leave_type}</td>
                                        <td>{leave.from_date} to {leave.to_date}</td>
                                        <td><span className="d-inline-block text-truncate" style={{maxWidth: '150px'}} title={leave.reason}>{leave.reason}</span></td>
                                        <td>{leave.applied_at}</td>
                                        <td>
                                            <span className={`badge ${getStatusBadge(leave.status)}`}>
                                                {leave.status.toUpperCase()}
                                            </span>
                                        </td>
                                        <td>
                                            {leave.status === 'pending' ? (
                                                <div className="d-flex gap-2">
                                                    <button className="btn btn-sm btn-success" onClick={() => openProcessModal(leave, 'approve')} title="Approve">
                                                        <FaCheckCircle />
                                                    </button>
                                                    <button className="btn btn-sm btn-danger" onClick={() => openProcessModal(leave, 'reject')} title="Reject">
                                                        <FaTimesCircle />
                                                    </button>
                                                </div>
                                            ) : (
                                                <span className="text-muted small fst-italic">{leave.comments ? 'Commented' : 'Processed'}</span>
                                            )}
                                        </td>
                                    </tr>
                                ))}
                                {leaves.length === 0 && (
                                    <tr>
                                        <td colSpan="7" className="text-center text-muted py-5">
                                            No escalated HR leave requests found.
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

            {/* Process Leave Modal */}
            {showModal && currentLeave && (
                <div className="modal d-block" style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
                    <div className="modal-dialog modal-dialog-centered">
                        <div className="modal-content border-0 shadow-lg" style={{ background: 'rgba(20, 20, 30, 0.98)', backdropFilter: 'blur(10px)' }}>
                            <div className="modal-header border-bottom border-secondary">
                                <h5 className="modal-title fw-bold text-capitalize text-white">{action} HR Leave Request</h5>
                                <button type="button" className="btn-close btn-close-white" onClick={() => setShowModal(false)}></button>
                            </div>
                            <div className="modal-body p-4">
                                <div className="mb-4">
                                    <h6 className="text-white">HR Admin: <span className="text-warning fw-bold">{currentLeave.employee_name}</span></h6>
                                    <h6 className="text-white">Date: <span className="text-light fw-normal">{currentLeave.from_date} to {currentLeave.to_date} ({currentLeave.leave_type})</span></h6>
                                    <h6 className="text-white mt-3">Reason:</h6>
                                    <p className="text-light bg-dark p-2 rounded border border-secondary">{currentLeave.reason}</p>
                                </div>
                                <form onSubmit={handleProcessLeave}>
                                    <div className="mb-4">
                                        <label className="form-label text-white">Add Comment (Optional)</label>
                                        <textarea className="form-control bg-dark text-light border-secondary" rows="3" value={comments} onChange={e => setComments(e.target.value)} placeholder="Reason for approval/rejection..."></textarea>
                                    </div>
                                    <div className="d-flex justify-content-end gap-2">
                                        <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)}>Cancel</button>
                                        <button type="submit" className={`btn btn-${action === 'approve' ? 'success' : 'danger'}`}>
                                            Confirm {action.charAt(0).toUpperCase() + action.slice(1)}
                                        </button>
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

export default SuperAdminLeaveApprovals;
