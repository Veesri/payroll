import React, { useEffect, useState, useContext } from 'react';
import axios from 'axios';
import { AuthContext } from '../context/AuthContext';
import { FaDownload, FaHistory } from 'react-icons/fa';
import Layout from '../components/Layout';

const HRAttendance = () => {
    const { user } = useContext(AuthContext);
    const [attendanceData, setAttendanceData] = useState([]);
    const [loading, setLoading] = useState(true);
    const [page, setPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);
    const [filterEmployeeId, setFilterEmployeeId] = useState('');
    
    const token = localStorage.getItem('token');
    const headers = { Authorization: `Bearer ${token}` };

    const fetchAttendance = async () => {
        try {
            const url = `${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/api/attendance/?page=${page}${filterEmployeeId ? `&employee_id=${filterEmployeeId}` : ''}`;
            const res = await axios.get(url, { headers });
            setAttendanceData(res.data.attendance);
            setTotalPages(res.data.pages);
        } catch (error) {
            console.error("Failed to fetch attendance", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchAttendance();
    }, [page, filterEmployeeId]);

    const handleExportExcel = async () => {
        try {
            const res = await axios.get(`${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/api/attendance/export/excel`, {
                headers,
                responseType: 'blob'
            });
            const url = window.URL.createObjectURL(new Blob([res.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', 'Attendance_Report.xlsx');
            document.body.appendChild(link);
            link.click();
            link.parentNode.removeChild(link);
        } catch (error) {
            alert("Failed to export Excel report.");
        }
    };

    if (loading && page === 1) return <Layout><div className="text-center mt-5"><div className="spinner-border text-primary" role="status"></div></div></Layout>;

    return (
        <Layout>
            <div className="slide-up-animation">
                <div className="mb-5 d-flex justify-content-between align-items-center">
                    <div>
                        <h1 className="fw-bold mb-0">Company Attendance</h1>
                        <p className="text-muted">Monitor and export daily attendance logs</p>
                    </div>
                    <button className="btn btn-outline-success border-secondary text-success" onClick={handleExportExcel}>
                        <FaDownload className="me-2" /> Export to Excel
                    </button>
                </div>

                <div className="card border-0 p-4">
                    <div className="d-flex justify-content-between align-items-center mb-4">
                        <h4 className="fw-bold mb-0 d-flex align-items-center gap-2"><FaHistory /> Daily Logs</h4>
                        <div style={{ maxWidth: '300px' }}>
                            <input type="number" className="form-control" placeholder="Filter by Employee ID..." value={filterEmployeeId} onChange={(e) => { setFilterEmployeeId(e.target.value); setPage(1); }} />
                        </div>
                    </div>

                    <div className="table-responsive">
                        <table className="table table-borderless table-hover text-white align-middle">
                            <thead className="text-muted border-bottom border-secondary">
                                <tr>
                                    <th>Employee</th>
                                    <th>Department</th>
                                    <th>Date</th>
                                    <th>Check In</th>
                                    <th>Check Out</th>
                                    <th>Working Hours</th>
                                    <th>Status</th>
                                    <th>Source</th>
                                </tr>
                            </thead>
                            <tbody>
                                {attendanceData.map(record => (
                                    <tr key={record.id}>
                                        <td className="fw-bold">{record.employee_name}</td>
                                        <td>{record.department || '-'}</td>
                                        <td>{record.date}</td>
                                        <td>{record.check_in}</td>
                                        <td>{record.check_out}</td>
                                        <td>{record.working_hours ? `${record.working_hours} hrs` : '-'}</td>
                                        <td>
                                            <span className={`badge ${record.status === 'present' ? 'bg-success' : record.status === 'absent' ? 'bg-danger' : 'bg-warning text-dark'}`}>
                                                {record.status.toUpperCase()}
                                            </span>
                                        </td>
                                        <td><small className="text-muted">{record.source.toUpperCase()}</small></td>
                                    </tr>
                                ))}
                                {attendanceData.length === 0 && (
                                    <tr>
                                        <td colSpan="8" className="text-center text-muted py-5">
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

export default HRAttendance;
