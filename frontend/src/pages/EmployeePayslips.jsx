import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Layout from '../components/Layout';
import { FaDownload, FaFilePdf, FaEye } from 'react-icons/fa';

const EmployeePayslips = () => {
    const [payslips, setPayslips] = useState([]);
    const [loading, setLoading] = useState(true);
    
    const [filterYear, setFilterYear] = useState(new Date().getFullYear());

    const token = localStorage.getItem('token');
    const headers = { Authorization: `Bearer ${token}` };

    const fetchPayslips = async () => {
        try {
            const res = await axios.get(`${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/api/payslips/?year=${filterYear}`, { headers });
            setPayslips(res.data);
        } catch (error) {
            console.error("Failed to fetch payslips", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchPayslips();
    }, [filterYear]);

    const handleDownload = async (id, month, year) => {
        try {
            const res = await axios.get(`${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/api/payslips/download/${id}`, { 
                headers,
                responseType: 'blob' 
            });
            const url = window.URL.createObjectURL(new Blob([res.data]));
            const link = document.createElement('a');
            link.href = url;
            const monthName = new Date(year, month - 1, 1).toLocaleString('default', { month: 'short' });
            link.setAttribute('download', `Payslip_${monthName}_${year}.pdf`);
            document.body.appendChild(link);
            link.click();
            link.parentNode.removeChild(link);
        } catch (error) {
            alert("Failed to download PDF. It may not exist.");
        }
    };

    const handleView = async (id) => {
        try {
            const res = await axios.get(`${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/api/payslips/view/${id}`, { 
                headers,
                responseType: 'blob' 
            });
            const file = new Blob([res.data], { type: 'application/pdf' });
            const fileURL = URL.createObjectURL(file);
            window.open(fileURL, '_blank');
        } catch (error) {
            alert("Failed to view PDF. It may not exist.");
        }
    };

    if (loading) return <Layout><div className="text-center mt-5"><div className="spinner-border text-primary" role="status"></div></div></Layout>;

    return (
        <Layout>
            <div className="slide-up-animation">
                <div className="mb-5">
                    <h1 className="fw-bold mb-0">My Payslips</h1>
                    <p className="text-muted">View and download your monthly salary slips</p>
                </div>

                <div className="card border-0 p-4 shadow-sm mb-4 bg-transparent border border-secondary">
                    <div className="row g-3">
                        <div className="col-md-4">
                            <label className="text-muted mb-1">Filter by Year</label>
                            <input type="number" className="form-control bg-dark text-light border-secondary" value={filterYear} onChange={e => setFilterYear(e.target.value)} />
                        </div>
                    </div>
                </div>

                <div className="card border-0 p-4 shadow-sm">
                    <div className="table-responsive">
                        <table className="table table-borderless table-hover text-white align-middle mb-0">
                            <thead className="text-muted border-bottom border-secondary">
                                <tr>
                                    <th>Period</th>
                                    <th>Generated Date</th>
                                    <th>Status</th>
                                    <th className="text-end">Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {payslips.map(p => {
                                    const monthName = new Date(p.year, p.month - 1, 1).toLocaleString('default', { month: 'long' });
                                    return (
                                    <tr key={p.id}>
                                        <td className="fw-bold"><FaFilePdf className="text-danger me-2"/> {monthName} {p.year}</td>
                                        <td>{p.generated_date}</td>
                                        <td><span className="badge bg-success">Available</span></td>
                                        <td className="text-end">
                                            <button className="btn btn-sm btn-outline-info me-2" onClick={() => handleView(p.id)}>
                                                <FaEye className="me-1" /> View PDF
                                            </button>
                                            <button className="btn btn-sm btn-primary" onClick={() => handleDownload(p.id, p.month, p.year)}>
                                                <FaDownload className="me-1" /> Download PDF
                                            </button>
                                        </td>
                                    </tr>
                                )})}
                                {payslips.length === 0 && <tr><td colSpan="4" className="text-center py-5 text-muted">No payslips found for this year.</td></tr>}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </Layout>
    );
};

export default EmployeePayslips;
