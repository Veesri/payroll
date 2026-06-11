import React, { useState, useEffect, useContext } from 'react';
import axios from 'axios';
import Layout from '../components/Layout';
import { AuthContext } from '../context/AuthContext';
import { FaMoneyBillWave, FaCogs, FaCheckCircle, FaRupeeSign, FaDownload } from 'react-icons/fa';

const PayrollDashboard = () => {
    const [payrolls, setPayrolls] = useState([]);
    const [stats, setStats] = useState({ total_expense: 0, processed_count: 0, pending_count: 0 });
    const [loading, setLoading] = useState(true);
    const [showModal, setShowModal] = useState(false);
    
    const [filterMonth, setFilterMonth] = useState(new Date().getMonth() + 1);
    const [filterYear, setFilterYear] = useState(new Date().getFullYear());
    
    // For generation
    const [genMonth, setGenMonth] = useState(new Date().getMonth() + 1);
    const [genYear, setGenYear] = useState(new Date().getFullYear());
    const [isGenerating, setIsGenerating] = useState(false);

    const token = localStorage.getItem('token');
    const headers = { Authorization: `Bearer ${token}` };

    const fetchDashboard = async () => {
        try {
            const statRes = await axios.get(`${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/api/payroll/dashboard?month=${filterMonth}&year=${filterYear}`, { headers });
            setStats(statRes.data);
            
            const payRes = await axios.get(`${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/api/payroll/?month=${filterMonth}&year=${filterYear}`, { headers });
            setPayrolls(payRes.data);
        } catch (error) {
            console.error("Failed to fetch payroll dashboard", error);
        } finally {
            setLoading(false);
        }
    };

    const handleExportExcel = async () => {
        try {
            const res = await axios.get(`${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/api/payroll/export/excel?month=${filterMonth}&year=${filterYear}`, {
                headers,
                responseType: 'blob'
            });
            const url = window.URL.createObjectURL(new Blob([res.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', 'Payroll_Report.xlsx');
            document.body.appendChild(link);
            link.click();
            link.parentNode.removeChild(link);
        } catch (error) {
            alert("Failed to export Excel report.");
        }
    };

    useEffect(() => {
        fetchDashboard();
    }, [filterMonth, filterYear]);

    const handleGenerate = async (e) => {
        e.preventDefault();
        setIsGenerating(true);
        try {
            const res = await axios.post(`${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/api/payroll/generate`, {
                month: parseInt(genMonth),
                year: parseInt(genYear)
            }, { headers });
            
            alert(res.data.message);
            setShowModal(false);
            setFilterMonth(genMonth);
            setFilterYear(genYear);
            fetchDashboard();
        } catch (error) {
            alert(error.response?.data?.message || "Failed to generate payroll");
        } finally {
            setIsGenerating(false);
        }
    };
    
    const handleDelete = async (id) => {
        if(!window.confirm("Are you sure you want to delete this payroll record?")) return;
        try {
            await axios.delete(`${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/api/payroll/${id}`, { headers });
            fetchDashboard();
        } catch (error) {
            alert("Failed to delete");
        }
    }

    const handleGeneratePayslip = async (payrollId) => {
        try {
            const res = await axios.post(`${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/api/payslips/generate/${payrollId}`, {}, { headers });
            alert(res.data.message);
            fetchDashboard(); // Refresh to potentially show download button if we linked it
        } catch (error) {
            alert(error.response?.data?.message || "Failed to generate PDF");
        }
    };

    const handleEmailPayslip = async (payslipId) => {
        try {
            const res = await axios.post(`${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/api/payslips/email/${payslipId}`, {}, { headers });
            alert(res.data.message);
        } catch (error) {
            alert(error.response?.data?.message || "Failed to email payslip");
        }
    };

    if (loading) return <Layout><div className="text-center mt-5"><div className="spinner-border text-primary" role="status"></div></div></Layout>;

    return (
        <Layout>
            <div className="slide-up-animation">
                <div className="d-flex justify-content-between align-items-center mb-5">
                    <div>
                        <h1 className="fw-bold mb-0">Payroll Engine</h1>
                        <p className="text-muted">Process and manage employee salaries</p>
                    </div>
                    <button className="btn btn-primary btn-lg shadow-sm" onClick={() => setShowModal(true)}>
                        <FaCogs className="me-2" /> Generate Payroll
                    </button>
                </div>

                <div className="row g-4 mb-5">
                    <div className="col-md-4">
                        <div className="card h-100 border-0 p-4 dashboard-stat-card" style={{ background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.2) 0%, rgba(99, 102, 241, 0.05) 100%)', borderLeft: '4px solid var(--bs-primary) !important' }}>
                            <div className="d-flex align-items-center justify-content-between">
                                <div>
                                    <h6 className="text-muted text-uppercase fw-bold mb-2">Total Salary Expense</h6>
                                    <h2 className="fw-bold mb-0">₹{stats.total_expense.toLocaleString()}</h2>
                                </div>
                                <div className="bg-primary text-white p-3 rounded-circle" style={{ opacity: 0.8 }}>
                                    <FaRupeeSign size={24} />
                                </div>
                            </div>
                        </div>
                    </div>
                    <div className="col-md-4">
                        <div className="card h-100 border-0 p-4 dashboard-stat-card" style={{ background: 'linear-gradient(135deg, rgba(32, 201, 151, 0.2) 0%, rgba(32, 201, 151, 0.05) 100%)', borderLeft: '4px solid #20c997 !important' }}>
                            <div className="d-flex align-items-center justify-content-between">
                                <div>
                                    <h6 className="text-muted text-uppercase fw-bold mb-2">Processed Employees</h6>
                                    <h2 className="fw-bold mb-0">{stats.processed_count}</h2>
                                </div>
                                <div className="bg-success text-white p-3 rounded-circle" style={{ opacity: 0.8, backgroundColor: '#20c997 !important' }}>
                                    <FaCheckCircle size={24} />
                                </div>
                            </div>
                        </div>
                    </div>
                    <div className="col-md-4">
                        <div className="card h-100 border-0 p-4 dashboard-stat-card" style={{ background: 'linear-gradient(135deg, rgba(245, 158, 11, 0.2) 0%, rgba(245, 158, 11, 0.05) 100%)', borderLeft: '4px solid #f59e0b !important' }}>
                            <div className="d-flex align-items-center justify-content-between">
                                <div>
                                    <h6 className="text-muted text-uppercase fw-bold mb-2">Pending Payroll</h6>
                                    <h2 className="fw-bold mb-0">{stats.pending_count}</h2>
                                </div>
                                <div className="bg-warning text-white p-3 rounded-circle" style={{ opacity: 0.8, backgroundColor: '#f59e0b !important' }}>
                                    <FaMoneyBillWave size={24} />
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div className="card border-0 p-4 shadow-sm mb-4 bg-transparent border border-secondary">
                    <div className="row g-3">
                        <div className="col-md-4">
                            <label className="text-muted mb-1">Filter Month</label>
                            <select className="form-select bg-dark text-light border-secondary" value={filterMonth} onChange={e => setFilterMonth(e.target.value)}>
                                {[...Array(12)].map((_, i) => <option key={i+1} value={i+1}>{new Date(2000, i, 1).toLocaleString('default', { month: 'long' })}</option>)}
                            </select>
                        </div>
                        <div className="col-md-4">
                            <label className="text-muted mb-1">Filter Year</label>
                            <input type="number" className="form-control bg-dark text-light border-secondary" value={filterYear} onChange={e => setFilterYear(e.target.value)} />
                        </div>
                    </div>
                </div>

                <div className="card border-0 p-4 shadow-sm">
                    <div className="card-header bg-transparent border-secondary py-3 d-flex justify-content-between align-items-center">
                        <h5 className="mb-0 fw-bold">Processed Payroll Records</h5>
                        <button className="btn btn-sm btn-outline-success border-secondary text-success" onClick={handleExportExcel}>
                            <FaDownload className="me-2" /> Export Excel
                        </button>
                    </div>
                    <div className="table-responsive">
                        <table className="table table-borderless table-hover text-white align-middle mb-0">
                            <thead className="text-muted border-bottom border-secondary">
                                <tr>
                                    <th>Employee</th>
                                    <th>Month/Year</th>
                                    <th>Gross Salary</th>
                                    <th>Deductions</th>
                                    <th>Net Salary</th>
                                    <th>Status</th>
                                    <th className="text-end">Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {payrolls.map(p => (
                                    <tr key={p.id}>
                                        <td className="fw-bold">{p.employee_name} <br/><small className="text-muted fw-normal">{p.department}</small></td>
                                        <td>{new Date(p.year, p.month - 1, 1).toLocaleString('default', { month: 'short' })} {p.year}</td>
                                        <td>₹{p.gross_salary.toLocaleString(undefined, {minimumFractionDigits: 2})}</td>
                                        <td><span className="text-danger">-₹{p.deductions.toLocaleString(undefined, {minimumFractionDigits: 2})}</span></td>
                                        <td className="fw-bold text-success">₹{p.net_salary.toLocaleString(undefined, {minimumFractionDigits: 2})}</td>
                                        <td><span className="badge bg-success">{p.status.toUpperCase()}</span></td>
                                        <td className="text-end">
                                            <div className="dropdown">
                                                <button className="btn btn-sm btn-outline-info dropdown-toggle" type="button" data-bs-toggle="dropdown">
                                                    Actions
                                                </button>
                                                <ul className="dropdown-menu dropdown-menu-dark">
                                                    <li><button className="dropdown-item" onClick={() => handleGeneratePayslip(p.id)}>Generate PDF</button></li>
                                                    <li><button className="dropdown-item text-danger" onClick={() => handleDelete(p.id)}>Delete Payroll</button></li>
                                                </ul>
                                            </div>
                                        </td>
                                    </tr>
                                ))}
                                {payrolls.length === 0 && <tr><td colSpan="7" className="text-center py-5 text-muted">No payroll records found for this period.</td></tr>}
                            </tbody>
                        </table>
                    </div>
                </div>

                {/* Generate Payroll Modal */}
                {showModal && (
                    <div className="modal d-block" style={{ backgroundColor: 'rgba(0,0,0,0.5)', backdropFilter: 'blur(5px)' }}>
                        <div className="modal-dialog modal-dialog-centered">
                            <div className="modal-content border-0 shadow-lg" style={{ background: 'rgba(20, 20, 30, 0.98)', backdropFilter: 'blur(10px)' }}>
                                <div className="modal-header border-secondary">
                                    <h5 className="modal-title fw-bold text-white">Generate Batch Payroll</h5>
                                    <button type="button" className="btn-close btn-close-white" onClick={() => setShowModal(false)}></button>
                                </div>
                                <div className="modal-body p-4">
                                    <div className="alert alert-info border-0" style={{ backgroundColor: 'rgba(13, 202, 240, 0.1)' }}>
                                        This engine will auto-calculate salaries based on Attendance, Loss of Pay leaves, Allowances, and Deductions.
                                    </div>
                                    <form onSubmit={handleGenerate}>
                                        <div className="row g-3 mb-4 mt-2">
                                            <div className="col-md-6">
                                                <label className="form-label text-white">Target Month</label>
                                                <select className="form-select bg-dark text-light border-secondary" value={genMonth} onChange={e => setGenMonth(e.target.value)}>
                                                    {[...Array(12)].map((_, i) => <option key={i+1} value={i+1}>{new Date(2000, i, 1).toLocaleString('default', { month: 'long' })}</option>)}
                                                </select>
                                            </div>
                                            <div className="col-md-6">
                                                <label className="form-label text-white">Target Year</label>
                                                <input type="number" className="form-control bg-dark text-light border-secondary" value={genYear} onChange={e => setGenYear(e.target.value)} required />
                                            </div>
                                        </div>
                                        <div className="d-flex justify-content-end gap-2">
                                            <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)} disabled={isGenerating}>Cancel</button>
                                            <button type="submit" className="btn btn-primary" disabled={isGenerating}>
                                                {isGenerating ? 'Processing Engine...' : 'Run Payroll Engine'}
                                            </button>
                                        </div>
                                    </form>
                                </div>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </Layout>
    );
};

export default PayrollDashboard;
