import React, { useState, useEffect, useContext } from 'react';
import axios from 'axios';
import Layout from '../components/Layout';
import { AuthContext } from '../context/AuthContext';
import { FaEdit, FaRupeeSign } from 'react-icons/fa';

const SalaryStructures = () => {
    const [structures, setStructures] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showModal, setShowModal] = useState(false);
    const [currentEmp, setCurrentEmp] = useState(null);
    const [formData, setFormData] = useState({
        basic_salary: 0, hra: 0, travel_allowance: 0, medical_allowance: 0, 
        bonus: 0, pf: 0, professional_tax: 0, other_deductions: 0, overtime_rate: 0
    });
    const { user } = useContext(AuthContext);

    const token = localStorage.getItem('token');
    const headers = { Authorization: `Bearer ${token}` };

    const fetchStructures = async () => {
        try {
            const res = await axios.get(`${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/api/salary/`, { headers });
            setStructures(res.data);
        } catch (error) {
            console.error("Failed to fetch salary structures", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchStructures();
    }, []);

    const handleSave = async (e) => {
        e.preventDefault();
        try {
            await axios.put(`${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/api/salary/${currentEmp.employee_id}`, formData, { headers });
            setShowModal(false);
            fetchStructures();
        } catch (error) {
            alert(error.response?.data?.message || "Failed to update salary structure");
        }
    };

    const openModal = (emp) => {
        setCurrentEmp(emp);
        setFormData({
            basic_salary: emp.basic_salary,
            hra: emp.hra,
            travel_allowance: emp.travel_allowance,
            medical_allowance: emp.medical_allowance,
            bonus: emp.bonus,
            pf: emp.pf,
            professional_tax: emp.professional_tax,
            other_deductions: emp.other_deductions,
            overtime_rate: emp.overtime_rate
        });
        setShowModal(true);
    };

    if (loading) return <Layout><div className="text-center mt-5"><div className="spinner-border text-primary" role="status"></div></div></Layout>;

    return (
        <Layout>
            <div className="slide-up-animation">
                <div className="mb-4">
                    <h2 className="fw-bold mb-0">Salary Structures</h2>
                    <p className="text-muted">Manage fixed salary components and deductions for employees</p>
                </div>

                <div className="card border-0 p-4 shadow-sm">
                    <div className="table-responsive">
                        <table className="table table-borderless table-hover text-white align-middle mb-0">
                            <thead className="text-muted border-bottom border-secondary">
                                <tr>
                                    <th>Employee</th>
                                    <th>Department</th>
                                    <th>Basic Salary</th>
                                    <th>Allowances (HRA+TA+MA)</th>
                                    <th>Deductions (PF+PT)</th>
                                    <th className="text-end">Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {structures.map(emp => (
                                    <tr key={emp.employee_id}>
                                        <td className="fw-bold">{emp.employee_name}</td>
                                        <td>{emp.department}</td>
                                        <td>₹{emp.basic_salary.toLocaleString()}</td>
                                        <td><span className="text-success">+₹{(emp.hra + emp.travel_allowance + emp.medical_allowance).toLocaleString()}</span></td>
                                        <td><span className="text-danger">-₹{(emp.pf + emp.professional_tax + emp.other_deductions).toLocaleString()}</span></td>
                                        <td className="text-end">
                                            <button className="btn btn-sm btn-outline-info" onClick={() => openModal(emp)}>
                                                <FaEdit /> Configure
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                                {structures.length === 0 && <tr><td colSpan="6" className="text-center py-4 text-muted">No employees found</td></tr>}
                            </tbody>
                        </table>
                    </div>
                </div>

                {/* Edit Modal */}
                {showModal && (
                    <div className="modal d-block" style={{ backgroundColor: 'rgba(0,0,0,0.5)', backdropFilter: 'blur(5px)', overflowY: 'auto' }}>
                        <div className="modal-dialog modal-dialog-centered modal-lg my-5">
                            <div className="modal-content border-0 shadow-lg" style={{ background: 'rgba(20, 20, 30, 0.98)', backdropFilter: 'blur(10px)' }}>
                                <div className="modal-header border-secondary">
                                    <h5 className="modal-title fw-bold text-white">Configure Salary Structure: {currentEmp.employee_name}</h5>
                                    <button type="button" className="btn-close btn-close-white" onClick={() => setShowModal(false)}></button>
                                </div>
                                <div className="modal-body">
                                    <form onSubmit={handleSave}>
                                        <h6 className="text-primary mb-3">Earnings</h6>
                                        <div className="row g-3 mb-3">
                                            <div className="col-md-4">
                                                <label className="form-label text-white">Basic Salary</label>
                                                <div className="input-group">
                                                    <span className="input-group-text bg-dark text-muted border-secondary"><FaRupeeSign /></span>
                                                    <input type="number" className="form-control bg-dark text-light border-secondary" value={formData.basic_salary} onChange={e => setFormData({...formData, basic_salary: e.target.value})} required />
                                                </div>
                                            </div>
                                            <div className="col-md-4">
                                                <label className="form-label text-white">HRA</label>
                                                <input type="number" className="form-control bg-dark text-light border-secondary" value={formData.hra} onChange={e => setFormData({...formData, hra: e.target.value})} />
                                            </div>
                                            <div className="col-md-4">
                                                <label className="form-label text-white">Travel Allowance</label>
                                                <input type="number" className="form-control bg-dark text-light border-secondary" value={formData.travel_allowance} onChange={e => setFormData({...formData, travel_allowance: e.target.value})} />
                                            </div>
                                            <div className="col-md-4">
                                                <label className="form-label text-white">Medical Allowance</label>
                                                <input type="number" className="form-control bg-dark text-light border-secondary" value={formData.medical_allowance} onChange={e => setFormData({...formData, medical_allowance: e.target.value})} />
                                            </div>
                                            <div className="col-md-4">
                                                <label className="form-label text-white">Fixed Bonus</label>
                                                <input type="number" className="form-control bg-dark text-light border-secondary" value={formData.bonus} onChange={e => setFormData({...formData, bonus: e.target.value})} />
                                            </div>
                                        </div>

                                        <h6 className="text-danger mb-3 mt-4">Deductions</h6>
                                        <div className="row g-3 mb-3">
                                            <div className="col-md-4">
                                                <label className="form-label text-white">Provident Fund (PF)</label>
                                                <input type="number" className="form-control bg-dark text-light border-secondary" value={formData.pf} onChange={e => setFormData({...formData, pf: e.target.value})} />
                                            </div>
                                            <div className="col-md-4">
                                                <label className="form-label text-white">Professional Tax</label>
                                                <input type="number" className="form-control bg-dark text-light border-secondary" value={formData.professional_tax} onChange={e => setFormData({...formData, professional_tax: e.target.value})} />
                                            </div>
                                            <div className="col-md-4">
                                                <label className="form-label text-white">Other Deductions</label>
                                                <input type="number" className="form-control bg-dark text-light border-secondary" value={formData.other_deductions} onChange={e => setFormData({...formData, other_deductions: e.target.value})} />
                                            </div>
                                        </div>
                                        
                                        <h6 className="text-warning mb-3 mt-4">Other Variables</h6>
                                        <div className="row g-3 mb-4">
                                            <div className="col-md-4">
                                                <label className="form-label text-white">Overtime Rate (Per Hour)</label>
                                                <div className="input-group">
                                                    <span className="input-group-text bg-dark text-muted border-secondary"><FaRupeeSign /></span>
                                                    <input type="number" className="form-control bg-dark text-light border-secondary" value={formData.overtime_rate} onChange={e => setFormData({...formData, overtime_rate: e.target.value})} />
                                                </div>
                                            </div>
                                        </div>

                                        <div className="d-flex justify-content-end gap-2">
                                            <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)}>Cancel</button>
                                            <button type="submit" className="btn btn-primary">Save Structure</button>
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

export default SalaryStructures;
