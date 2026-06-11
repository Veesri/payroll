import React, { useState, useEffect, useContext } from 'react';
import axios from 'axios';
import Layout from '../components/Layout';
import { AuthContext } from '../context/AuthContext';
import { FaEdit, FaTrash, FaPlus, FaSearch, FaDownload } from 'react-icons/fa';

const EmployeeManagement = () => {
    const [employees, setEmployees] = useState([]);
    const [departments, setDepartments] = useState([]);
    const [loading, setLoading] = useState(true);
    
    // Pagination & Search
    const [page, setPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);
    const [search, setSearch] = useState('');
    const [filterDept, setFilterDept] = useState('');

    const [showModal, setShowModal] = useState(false);
    const [currentEmp, setCurrentEmp] = useState(null);
    const [formData, setFormData] = useState({
        first_name: '', last_name: '', email: '', username: '', password: '', 
        department_id: '', designation: '', basic_salary: '', phone: ''
    });
    
    const { user } = useContext(AuthContext);
    const token = localStorage.getItem('token');
    const headers = { Authorization: `Bearer ${token}` };

    const fetchEmployees = async () => {
        try {
            const res = await axios.get(`${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/api/employees/?page=${page}&search=${search}&department_id=${filterDept}`, { headers });
            setEmployees(res.data.employees);
            setTotalPages(res.data.pages);
        } catch (error) {
            console.error("Failed to fetch employees", error);
        }
    };

    const fetchDepartments = async () => {
        try {
            const res = await axios.get(`${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/api/departments/`, { headers });
            setDepartments(res.data);
        } catch (error) {
            console.error("Failed to fetch departments", error);
        }
    };

    const handleExportExcel = async () => {
        try {
            const res = await axios.get(`${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/api/employees/export/excel`, {
                headers,
                responseType: 'blob'
            });
            const url = window.URL.createObjectURL(new Blob([res.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', 'Employee_Report.xlsx');
            document.body.appendChild(link);
            link.click();
            link.parentNode.removeChild(link);
        } catch (error) {
            alert("Failed to export Excel report.");
        }
    };

    useEffect(() => {
        fetchDepartments();
    }, []);

    useEffect(() => {
        fetchEmployees();
        setLoading(false);
    }, [page, search, filterDept]);

    const handleSave = async (e) => {
        e.preventDefault();
        try {
            const fd = new FormData();
            Object.keys(formData).forEach(key => {
                if (formData[key] !== null && formData[key] !== undefined) {
                    fd.append(key, formData[key]);
                }
            });

            const config = { headers: { ...headers, 'Content-Type': 'multipart/form-data' } };

            if (currentEmp) {
                await axios.put(`${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/api/employees/${currentEmp.id}`, fd, config);
            } else {
                await axios.post(`${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/api/employees/`, fd, config);
            }
            setShowModal(false);
            fetchEmployees();
        } catch (error) {
            alert(error.response?.data?.message || "An error occurred");
        }
    };

    const handleDelete = async (id) => {
        if (!window.confirm("Are you sure you want to delete this employee?")) return;
        try {
            await axios.delete(`${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/api/employees/${id}`, { headers });
            fetchEmployees();
        } catch (error) {
            alert("Failed to delete employee");
        }
    };

    const openModal = async (emp = null) => {
        if (emp) {
            // fetch full details
            try {
                const res = await axios.get(`${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/api/employees/${emp.id}`, { headers });
                const fullEmp = res.data;
                setCurrentEmp(fullEmp);
                setFormData({
                    first_name: fullEmp.first_name, last_name: fullEmp.last_name, 
                    email: fullEmp.email, phone: fullEmp.phone || '', 
                    department_id: fullEmp.department_id || '', designation: fullEmp.designation || '', 
                    basic_salary: fullEmp.basic_salary || '', status: fullEmp.status
                });
            } catch (err) {
                console.error(err);
            }
        } else {
            setCurrentEmp(null);
            setFormData({
                first_name: '', last_name: '', email: '', username: '', password: '', 
                department_id: '', designation: '', basic_salary: '', phone: '', photo: null
            });
        }
        setShowModal(true);
    };

    if (loading) return <Layout><div className="text-center mt-5"><div className="spinner-border text-primary" role="status"></div></div></Layout>;

    return (
        <Layout>
            <div className="slide-up-animation">
                <div className="d-flex justify-content-between align-items-center mb-4">
                    <h2 className="fw-bold mb-0">Employee Management</h2>
                    <div className="d-flex gap-2">
                        <button className="btn btn-outline-success" onClick={handleExportExcel}>
                            <FaDownload className="me-2" /> Export Excel
                        </button>
                        {(user?.role === 'super_admin' || user?.role === 'hr_admin') && (
                            <button className="btn btn-primary" onClick={() => openModal()}>
                                <FaPlus className="me-2" /> Add Employee
                            </button>
                        )}
                    </div>
                </div>

                <div className="card border-0 p-4 shadow-sm mb-4 bg-transparent border border-secondary">
                    <div className="row g-3">
                        <div className="col-md-5">
                            <div className="input-group">
                                <span className="input-group-text bg-transparent border-secondary text-muted"><FaSearch /></span>
                                <input type="text" className="form-control" placeholder="Search by name or email..." value={search} onChange={e => {setSearch(e.target.value); setPage(1);}} />
                            </div>
                        </div>
                        <div className="col-md-4">
                            <select className="form-select" value={filterDept} onChange={e => {setFilterDept(e.target.value); setPage(1);}}>
                                <option value="">All Departments</option>
                                {departments.map(d => <option key={d.id} value={d.id}>{d.name}</option>)}
                            </select>
                        </div>
                    </div>
                </div>

                <div className="card border-0 p-4 shadow-sm">
                    <div className="table-responsive">
                        <table className="table table-borderless table-hover text-white align-middle mb-0">
                            <thead className="text-muted border-bottom border-secondary">
                                <tr>
                                    <th>Employee</th>
                                    <th>Department</th>
                                    <th>Designation</th>
                                    <th>Status</th>
                                    <th className="text-end">Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {employees.map(emp => (
                                    <tr key={emp.id}>
                                        <td>
                                            <div className="d-flex align-items-center">
                                                {emp.photo_url ? (
                                                    <img src={`${import.meta.env.VITE_API_URL || 'http://localhost:5000'}${emp.photo_url}`} alt="profile" className="rounded-circle me-3" style={{width: '40px', height: '40px', objectFit: 'cover'}} />
                                                ) : (
                                                    <div className="bg-primary text-white rounded-circle d-flex justify-content-center align-items-center me-3" style={{width: '40px', height: '40px'}}>
                                                        {emp.first_name[0]}{emp.last_name[0]}
                                                    </div>
                                                )}
                                                <div>
                                                    <div className="fw-bold">{emp.first_name} {emp.last_name}</div>
                                                    <small className="text-muted">{emp.email}</small>
                                                </div>
                                            </div>
                                        </td>
                                        <td>{emp.department || '-'}</td>
                                        <td>{emp.designation || '-'}</td>
                                        <td><span className={`badge ${emp.status === 'active' ? 'bg-success' : 'bg-warning'}`}>{emp.status}</span></td>
                                        <td className="text-end">
                                            <button className="btn btn-sm btn-outline-info me-2" onClick={() => openModal(emp)}>
                                                <FaEdit /> Profile
                                            </button>
                                            <button className="btn btn-sm btn-outline-danger" onClick={() => handleDelete(emp.id)}>
                                                <FaTrash />
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                                {employees.length === 0 && <tr><td colSpan="5" className="text-center py-4 text-muted">No employees found</td></tr>}
                            </tbody>
                        </table>
                    </div>

                    {/* Pagination */}
                    {totalPages > 1 && (
                        <div className="d-flex justify-content-between align-items-center mt-4">
                            <button className="btn btn-sm btn-outline-secondary" disabled={page === 1} onClick={() => setPage(p => p - 1)}>Previous</button>
                            <span className="text-muted">Page {page} of {totalPages}</span>
                            <button className="btn btn-sm btn-outline-secondary" disabled={page === totalPages} onClick={() => setPage(p => p + 1)}>Next</button>
                        </div>
                    )}
                </div>

                {/* Modal overlay */}
                {showModal && (
                    <div className="modal d-block" style={{ backgroundColor: 'rgba(0,0,0,0.5)', backdropFilter: 'blur(5px)', overflowY: 'auto' }}>
                        <div className="modal-dialog modal-dialog-centered modal-lg my-5">
                            <div className="modal-content border-0 shadow-lg" style={{ background: 'rgba(20, 20, 30, 0.98)', backdropFilter: 'blur(10px)' }}>
                                <div className="modal-header border-secondary">
                                    <h5 className="modal-title fw-bold text-white">{currentEmp ? 'Edit Employee Profile' : 'Add New Employee'}</h5>
                                    <button type="button" className="btn-close btn-close-white" onClick={() => setShowModal(false)}></button>
                                </div>
                                <div className="modal-body">
                                    <form onSubmit={handleSave}>
                                        <div className="row g-3 mb-3">
                                            <div className="col-md-6">
                                                <label className="form-label text-white">First Name</label>
                                                <input type="text" className="form-control bg-dark text-light border-secondary" value={formData.first_name} onChange={e => setFormData({...formData, first_name: e.target.value})} required />
                                            </div>
                                            <div className="col-md-6">
                                                <label className="form-label text-white">Last Name</label>
                                                <input type="text" className="form-control bg-dark text-light border-secondary" value={formData.last_name} onChange={e => setFormData({...formData, last_name: e.target.value})} required />
                                            </div>
                                        </div>
                                        <div className="row g-3 mb-3">
                                            <div className="col-md-6">
                                                <label className="form-label text-white">Email</label>
                                                <input type="email" className="form-control bg-dark text-light border-secondary" value={formData.email} onChange={e => setFormData({...formData, email: e.target.value})} required />
                                            </div>
                                            <div className="col-md-6">
                                                <label className="form-label text-white">Phone</label>
                                                <input type="text" className="form-control bg-dark text-light border-secondary" value={formData.phone} onChange={e => setFormData({...formData, phone: e.target.value})} />
                                            </div>
                                        </div>

                                        {!currentEmp && (
                                            <div className="row g-3 mb-3 border border-secondary p-3 rounded bg-transparent">
                                                <h6 className="text-primary mb-2">Account Credentials</h6>
                                                <div className="col-md-6">
                                                    <label className="form-label text-white">Username</label>
                                                    <input type="text" className="form-control bg-dark text-light border-secondary" value={formData.username} onChange={e => setFormData({...formData, username: e.target.value})} required={!currentEmp} autoComplete="new-password" />
                                                </div>
                                                <div className="col-md-6">
                                                    <label className="form-label text-white">Password</label>
                                                    <input type="password" className="form-control bg-dark text-light border-secondary" value={formData.password} onChange={e => setFormData({...formData, password: e.target.value})} required={!currentEmp} autoComplete="new-password" />
                                                </div>
                                            </div>
                                        )}

                                        <div className="row g-3 mb-3">
                                            <div className="col-md-6">
                                                <label className="form-label text-white">Department</label>
                                                <select className="form-select form-control bg-dark text-light border-secondary" value={formData.department_id} onChange={e => setFormData({...formData, department_id: e.target.value})}>
                                                    <option value="">Select Department</option>
                                                    {departments.map(d => <option key={d.id} value={d.id}>{d.name}</option>)}
                                                </select>
                                            </div>
                                            <div className="col-md-6">
                                                <label className="form-label text-white">Designation</label>
                                                <input type="text" className="form-control bg-dark text-light border-secondary" value={formData.designation} onChange={e => setFormData({...formData, designation: e.target.value})} />
                                            </div>
                                        </div>

                                        <div className="row g-3 mb-4">
                                            <div className="col-md-6">
                                                <label className="form-label text-white">Basic Salary (Annual/Monthly)</label>
                                                <input type="number" className="form-control bg-dark text-light border-secondary" value={formData.basic_salary} onChange={e => setFormData({...formData, basic_salary: e.target.value})} required />
                                            </div>
                                            <div className="col-md-6">
                                                <label className="form-label text-white">Profile Photo</label>
                                                <input type="file" className="form-control bg-dark text-light border-secondary" accept="image/*" onChange={e => setFormData({...formData, photo: e.target.files[0]})} />
                                            </div>
                                        </div>
                                        {currentEmp && (
                                            <div className="row g-3 mb-4">
                                                <div className="col-md-6">
                                                    <label className="form-label text-white">Status</label>
                                                    <select className="form-select form-control bg-dark text-light border-secondary" value={formData.status} onChange={e => setFormData({...formData, status: e.target.value})}>
                                                        <option value="active">Active</option>
                                                        <option value="inactive">Inactive</option>
                                                        <option value="on_leave">On Leave</option>
                                                    </select>
                                                </div>
                                            </div>
                                        )}
                                        
                                        <div className="d-flex justify-content-end gap-2">
                                            <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)}>Cancel</button>
                                            <button type="submit" className="btn btn-primary">Save Employee</button>
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

export default EmployeeManagement;
