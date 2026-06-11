import React, { useEffect, useState, useContext } from 'react';
import axios from 'axios';
import { AuthContext } from '../context/AuthContext';
import { FaClock, FaSignOutAlt, FaHistory } from 'react-icons/fa';
import Layout from '../components/Layout';

const EmployeeAttendance = () => {
    const { user } = useContext(AuthContext);
    const [attendanceHistory, setAttendanceHistory] = useState([]);
    const [loading, setLoading] = useState(true);
    const [page, setPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);
    
    const token = localStorage.getItem('token');
    const headers = { Authorization: `Bearer ${token}` };

    const fetchAttendance = async () => {
        try {
            const res = await axios.get(`${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/api/attendance/?page=${page}`, { headers });
            setAttendanceHistory(res.data.attendance);
            setTotalPages(res.data.pages);
        } catch (error) {
            console.error("Failed to fetch attendance", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchAttendance();
    }, [page]);

    const handleCheckIn = async () => {
        try {
            const res = await axios.post(`${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/api/attendance/checkin`, { source: 'web' }, { headers });
            alert(`Check-in successful at ${res.data.time}`);
            fetchAttendance();
        } catch (error) {
            alert(error.response?.data?.message || "Check-in failed");
        }
    };

    const handleCheckOut = async () => {
        try {
            const res = await axios.post(`${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/api/attendance/checkout`, {}, { headers });
            alert(`Check-out successful at ${res.data.time}. Working hours: ${res.data.working_hours}`);
            fetchAttendance();
        } catch (error) {
            alert(error.response?.data?.message || "Check-out failed");
        }
    };

    if (loading && page === 1) return <Layout><div className="text-center mt-5"><div className="spinner-border text-primary" role="status"></div></div></Layout>;

    return (
        <Layout>
            <div className="slide-up-animation">
                <div className="mb-5 d-flex justify-content-between align-items-center">
                    <div>
                        <h1 className="fw-bold mb-0">Attendance</h1>
                        <p className="text-muted">Manage your daily check-ins and check-outs</p>
                    </div>
                    <div className="d-flex gap-3">
                        <button className="btn btn-primary d-flex align-items-center gap-2" onClick={handleCheckIn}>
                            <FaClock /> Check In
                        </button>
                        <button className="btn btn-outline-danger d-flex align-items-center gap-2" onClick={handleCheckOut}>
                            <FaSignOutAlt /> Check Out
                        </button>
                    </div>
                </div>

                <div className="card border-0 p-4">
                    <h4 className="fw-bold mb-4 d-flex align-items-center gap-2"><FaHistory /> Attendance History</h4>
                    <div className="table-responsive">
                        <table className="table table-borderless table-hover text-white align-middle">
                            <thead className="text-muted border-bottom border-secondary">
                                <tr>
                                    <th>Date</th>
                                    <th>Check In</th>
                                    <th>Check Out</th>
                                    <th>Working Hours</th>
                                    <th>Status</th>
                                    <th>Source</th>
                                </tr>
                            </thead>
                            <tbody>
                                {attendanceHistory.map(record => (
                                    <tr key={record.id}>
                                        <td className="fw-bold">{record.date}</td>
                                        <td>{record.check_in}</td>
                                        <td>{record.check_out}</td>
                                        <td>{record.working_hours ? `${record.working_hours} hrs` : '-'}</td>
                                        <td>
                                            <span className={`badge ${record.status === 'present' ? 'bg-success' : 'bg-danger'}`}>
                                                {record.status.toUpperCase()}
                                            </span>
                                        </td>
                                        <td><small className="text-muted">{record.source.toUpperCase()}</small></td>
                                    </tr>
                                ))}
                                {attendanceHistory.length === 0 && (
                                    <tr>
                                        <td colSpan="6" className="text-center text-muted py-5">
                                            No attendance records found.
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
        </Layout>
    );
};

export default EmployeeAttendance;
