import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Layout from '../components/Layout';
import { FaMoneyBillWave, FaRupeeSign, FaBuilding, FaIdCard } from 'react-icons/fa';

const EmployeeSalary = () => {
    const [profile, setProfile] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    const token = localStorage.getItem('token');
    const headers = { Authorization: `Bearer ${token}` };

    useEffect(() => {
        const fetchSalaryDetails = async () => {
            try {
                // Get general user info (specifically the employee id)
                const meRes = await axios.get(`${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/api/auth/me`, { headers });
                const employeeId = meRes.data.employee?.id;

                if (employeeId) {
                    // Fetch full employee details (includes basic_salary)
                    const empRes = await axios.get(`${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/api/employees/${employeeId}`, { headers });
                    setProfile(empRes.data);
                } else {
                    setError('No profile details found for salary configuration.');
                }
            } catch (err) {
                console.error("Salary fetch error:", err);
                setError(`Failed to fetch salary profile: ${err.message || err}`);
            } finally {
                setLoading(false);
            }
        };

        fetchSalaryDetails();
    }, []);

    if (loading) return <Layout><div className="text-center mt-5"><div className="spinner-border text-primary" role="status"></div></div></Layout>;

    // Let's assume standard breakdown as typical in Indian payroll if basic_salary represents annual or monthly.
    const basic = profile?.basic_salary || 0;
    
    // Simulate typical HRA (40%), Medical (10%), Travel (10%)
    const hra = basic * 0.40;
    const travel = basic * 0.10;
    const medical = basic * 0.05;
    const gross = basic + hra + travel + medical;
    
    // Deductions
    const pf = basic * 0.12;
    const pt = basic > 15000 ? 200 : 0;
    const totalDeductions = pf + pt;
    const netPay = gross - totalDeductions;

    return (
        <Layout>
            <div className="slide-up-animation">
                <div className="mb-4">
                    <h2 className="fw-bold mb-0">My Salary & Compensation</h2>
                </div>

                {error ? (
                    <div className="alert alert-danger">{error}</div>
                ) : (
                    <div className="row g-4">
                        <div className="col-md-5">
                            <div className="card border-0 p-4 shadow-sm bg-gradient" style={{ background: 'linear-gradient(135deg, rgba(32, 201, 151, 0.15) 0%, rgba(32, 201, 151, 0.03) 100%)', borderLeft: '4px solid #20c997' }}>
                                <div className="card-body">
                                    <FaMoneyBillWave size={40} className="text-success mb-3" />
                                    <h5 className="text-muted text-uppercase fw-bold mb-2">Net Monthly Estimation</h5>
                                    <h1 className="fw-bold mb-0 text-success">
                                        <FaRupeeSign />{netPay.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}
                                    </h1>
                                    <p className="text-muted small mt-2">
                                        Estimated based on basic configuration of ₹{basic.toLocaleString()}
                                    </p>
                                    
                                    <hr className="my-4 border-secondary" />
                                    
                                    <div className="d-flex align-items-center mb-2">
                                        <FaIdCard className="text-muted me-2" />
                                        <span className="text-muted small">Employee: {profile?.first_name} {profile?.last_name}</span>
                                    </div>
                                    <div className="d-flex align-items-center">
                                        <FaBuilding className="text-muted me-2" />
                                        <span className="text-muted small">Department: {profile?.department || 'N/A'}</span>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div className="col-md-7">
                            <div className="card p-4 border-0 shadow-sm">
                                <h4 className="fw-bold mb-4 border-bottom pb-2 border-secondary">Salary Structure Breakdown</h4>
                                
                                <div className="table-responsive">
                                    <table className="table table-borderless align-middle mb-0">
                                        <thead>
                                            <tr className="border-bottom border-secondary text-dark">
                                                <th className="fw-bold">Component</th>
                                                <th className="text-end fw-bold">Amount</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            <tr>
                                                <td className="text-dark">Basic Salary</td>
                                                <td className="text-end fw-semibold text-dark">₹{basic.toLocaleString(undefined, {minimumFractionDigits: 2})}</td>
                                            </tr>
                                            <tr>
                                                <td className="text-dark">House Rent Allowance (HRA)</td>
                                                <td className="text-end fw-medium text-dark">₹{hra.toLocaleString(undefined, {minimumFractionDigits: 2})}</td>
                                            </tr>
                                            <tr>
                                                <td className="text-dark">Travel Allowance</td>
                                                <td className="text-end fw-medium text-dark">₹{travel.toLocaleString(undefined, {minimumFractionDigits: 2})}</td>
                                            </tr>
                                            <tr>
                                                <td className="text-dark">Medical Allowance</td>
                                                <td className="text-end fw-medium text-dark">₹{medical.toLocaleString(undefined, {minimumFractionDigits: 2})}</td>
                                            </tr>
                                            <tr className="border-top border-secondary font-weight-bold">
                                                <td className="fw-bold text-success">Gross Salary</td>
                                                <td className="text-end fw-bold text-success">₹{gross.toLocaleString(undefined, {minimumFractionDigits: 2})}</td>
                                            </tr>
                                            <tr className="border-top border-secondary text-dark">
                                                <td colSpan="2" className="pt-3 pb-1 small text-uppercase fw-bold">Deductions</td>
                                            </tr>
                                            <tr>
                                                <td className="text-dark">Provident Fund (PF)</td>
                                                <td className="text-end fw-medium text-dark">₹{pf.toLocaleString(undefined, {minimumFractionDigits: 2})}</td>
                                            </tr>
                                            <tr>
                                                <td className="text-dark">Professional Tax (PT)</td>
                                                <td className="text-end fw-medium text-dark">₹{pt.toLocaleString(undefined, {minimumFractionDigits: 2})}</td>
                                            </tr>
                                            <tr className="border-top border-secondary font-weight-bold">
                                                <td className="fw-bold text-danger">Total Deductions</td>
                                                <td className="text-end fw-bold text-danger">₹{totalDeductions.toLocaleString(undefined, {minimumFractionDigits: 2})}</td>
                                            </tr>
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </Layout>
    );
};

export default EmployeeSalary;
