import React, { useState, useEffect, useContext } from 'react';
import axios from 'axios';
import Layout from '../components/Layout';
import { AuthContext } from '../context/AuthContext';
import { FaEdit, FaTrash, FaPlus } from 'react-icons/fa';

const DepartmentManagement = () => {
    const [departments, setDepartments] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showModal, setShowModal] = useState(false);
    const [currentDept, setCurrentDept] = useState(null);
    const [formData, setFormData] = useState({ name: '', description: '' });
    const { user } = useContext(AuthContext);

    const token = localStorage.getItem('token');
    const headers = { Authorization: `Bearer ${token}` };

    const fetchDepartments = async () => {
        try {
            const res = await axios.get(`${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/api/departments/`, { headers });
            setDepartments(res.data);
        } catch (error) {
            console.error("Failed to fetch departments", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchDepartments();
    }, []);

    const handleSave = async (e) => {
        e.preventDefault();
        try {
            if (currentDept) {
                await axios.put(`${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/api/departments/${currentDept.id}`, formData, { headers });
            } else {
                await axios.post(`${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/api/departments/`, formData, { headers });
            }
            setShowModal(false);
            fetchDepartments();
        } catch (error) {
            alert(error.response?.data?.message || "An error occurred");
        }
    };

    const handleDelete = async (id) => {
        if (!window.confirm("Are you sure you want to delete this department?")) return;
        try {
            await axios.delete(`${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/api/departments/${id}`, { headers });
            fetchDepartments();
        } catch (error) {
            alert("Failed to delete department");
        }
    };

    const openModal = (dept = null) => {
        setCurrentDept(dept);
        setFormData(dept ? { name: dept.name, description: dept.description } : { name: '', description: '' });
        setShowModal(true);
    };

    if (loading) return <Layout><div className="text-center mt-5"><div className="spinner-border text-primary" role="status"></div></div></Layout>;

    return (
        <Layout>
            <div className="slide-up-animation">
                <div className="d-flex justify-content-between align-items-center mb-4">
                    <h2 className="fw-bold mb-0">Department Management</h2>
                    {user?.role === 'super_admin' && (
                        <button className="btn btn-primary" onClick={() => openModal()}>
                            <FaPlus className="me-2" /> Add Department
                        </button>
                    )}
                </div>

                <div className="card border-0 p-4 shadow-sm">
                    <div className="table-responsive">
                        <table className="table table-borderless table-hover text-white align-middle mb-0">
                            <thead className="text-muted border-bottom border-secondary">
                                <tr>
                                    <th>ID</th>
                                    <th>Name</th>
                                    <th>Description</th>
                                    <th>Head ID</th>
                                    {user?.role === 'super_admin' && <th className="text-end">Actions</th>}
                                </tr>
                            </thead>
                            <tbody>
                                {departments.map(dept => (
                                    <tr key={dept.id}>
                                        <td className="text-muted">#{dept.id}</td>
                                        <td className="fw-bold">{dept.name}</td>
                                        <td>{dept.description || '-'}</td>
                                        <td>{dept.head_id ? `#${dept.head_id}` : 'Unassigned'}</td>
                                        {user?.role === 'super_admin' && (
                                            <td className="text-end">
                                                <button className="btn btn-sm btn-outline-info me-2" onClick={() => openModal(dept)}>
                                                    <FaEdit />
                                                </button>
                                                <button className="btn btn-sm btn-outline-danger" onClick={() => handleDelete(dept.id)}>
                                                    <FaTrash />
                                                </button>
                                            </td>
                                        )}
                                    </tr>
                                ))}
                                {departments.length === 0 && <tr><td colSpan="5" className="text-center py-4 text-muted">No departments found</td></tr>}
                            </tbody>
                        </table>
                    </div>
                </div>

                {/* Modal overlay */}
                {showModal && (
                    <div className="modal d-block" style={{ backgroundColor: 'rgba(0,0,0,0.5)', backdropFilter: 'blur(5px)' }}>
                        <div className="modal-dialog modal-dialog-centered modal-lg">
                            <div className="modal-content border-0 shadow-lg" style={{ background: 'rgba(20, 20, 30, 0.98)', backdropFilter: 'blur(10px)' }}>
                                <div className="modal-header border-secondary">
                                    <h5 className="modal-title fw-bold text-white">{currentDept ? 'Edit Department' : 'Add Department'}</h5>
                                    <button type="button" className="btn-close btn-close-white" onClick={() => setShowModal(false)}></button>
                                </div>
                                <div className="modal-body">
                                    <form onSubmit={handleSave}>
                                        <div className="mb-3">
                                            <label className="form-label text-white">Department Name</label>
                                            <input type="text" className="form-control bg-dark text-light border-secondary" value={formData.name} onChange={e => setFormData({...formData, name: e.target.value})} required />
                                        </div>
                                        <div className="mb-4">
                                            <label className="form-label text-white">Description</label>
                                            <textarea className="form-control bg-dark text-light border-secondary" rows="3" value={formData.description} onChange={e => setFormData({...formData, description: e.target.value})}></textarea>
                                        </div>
                                        <div className="d-flex justify-content-end gap-2">
                                            <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)}>Cancel</button>
                                            <button type="submit" className="btn btn-primary">Save Changes</button>
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

export default DepartmentManagement;
