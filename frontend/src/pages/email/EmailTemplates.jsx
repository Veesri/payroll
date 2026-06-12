import React, { useState, useEffect } from 'react';
import axios from 'axios';

const EmailTemplates = () => {
    const [templates, setTemplates] = useState([]);
    const [loading, setLoading] = useState(false);
    const [showModal, setShowModal] = useState(false);
    const [currentTemplate, setCurrentTemplate] = useState({ id: null, name: '', subject: '', body: '' });

    const fetchTemplates = async () => {
        try {
            const token = localStorage.getItem('token');
            const res = await axios.get(`${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/api/email/templates`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            setTemplates(res.data);
        } catch (error) {
            console.error("Failed to fetch templates", error);
        }
    };

    useEffect(() => {
        fetchTemplates();
    }, []);

    const handleSave = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            const token = localStorage.getItem('token');
            if (currentTemplate.id) {
                await axios.put(`${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/api/email/templates/${currentTemplate.id}`, currentTemplate, {
                    headers: { Authorization: `Bearer ${token}` }
                });
            } else {
                await axios.post(`${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/api/email/templates`, currentTemplate, {
                    headers: { Authorization: `Bearer ${token}` }
                });
            }
            setShowModal(false);
            fetchTemplates();
        } catch (error) {
            alert('Failed to save template');
        }
        setLoading(false);
    };

    const handleDelete = async (id) => {
        if (!window.confirm("Are you sure you want to delete this template?")) return;
        try {
            const token = localStorage.getItem('token');
            await axios.delete(`${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/api/email/templates/${id}`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            fetchTemplates();
        } catch (error) {
            alert('Failed to delete template');
        }
    };

    const openEdit = (t) => {
        setCurrentTemplate(t);
        setShowModal(true);
    };

    const openNew = () => {
        setCurrentTemplate({ id: null, name: '', subject: '', body: '' });
        setShowModal(true);
    };

    return (
        <div className="container-fluid py-4">
            <div className="d-flex justify-content-between align-items-center mb-4">
                <h2 className="text-primary fw-bold mb-0">Email Templates</h2>
                <button className="btn btn-primary shadow-sm" onClick={openNew}>
                    + Create Template
                </button>
            </div>

            <div className="card shadow-sm border-0">
                <div className="card-body p-0">
                    <div className="table-responsive">
                        <table className="table table-hover align-middle mb-0">
                            <thead className="table-light">
                                <tr>
                                    <th>Template Name</th>
                                    <th>Subject Line</th>
                                    <th>Last Updated</th>
                                    <th className="text-end">Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {templates.length === 0 ? (
                                    <tr><td colSpan="4" className="text-center text-muted py-4">No templates found</td></tr>
                                ) : templates.map(t => (
                                    <tr key={t.id}>
                                        <td className="fw-bold">{t.name}</td>
                                        <td>{t.subject}</td>
                                        <td className="text-muted small">{t.updated_at}</td>
                                        <td className="text-end">
                                            <button className="btn btn-sm btn-outline-secondary me-2" onClick={() => openEdit(t)}>Edit</button>
                                            <button className="btn btn-sm btn-outline-danger" onClick={() => handleDelete(t.id)}>Delete</button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            {showModal && (
                <div className="modal d-block" style={{backgroundColor: 'rgba(0,0,0,0.5)'}}>
                    <div className="modal-dialog modal-lg">
                        <div className="modal-content">
                            <form onSubmit={handleSave}>
                                <div className="modal-header">
                                    <h5 className="modal-title">{currentTemplate.id ? 'Edit Template' : 'New Template'}</h5>
                                    <button type="button" className="btn-close" onClick={() => setShowModal(false)}></button>
                                </div>
                                <div className="modal-body">
                                    <div className="mb-3">
                                        <label className="form-label">Template Identifier (e.g. PASSWORD_RESET)</label>
                                        <input type="text" className="form-control" value={currentTemplate.name} onChange={e => setCurrentTemplate({...currentTemplate, name: e.target.value})} required />
                                    </div>
                                    <div className="mb-3">
                                        <label className="form-label">Email Subject</label>
                                        <input type="text" className="form-control" value={currentTemplate.subject} onChange={e => setCurrentTemplate({...currentTemplate, subject: e.target.value})} required />
                                    </div>
                                    <div className="mb-3">
                                        <label className="form-label">Email Body (HTML allowed)</label>
                                        <textarea className="form-control" rows="8" value={currentTemplate.body} onChange={e => setCurrentTemplate({...currentTemplate, body: e.target.value})} required></textarea>
                                        <div className="form-text">Variables: {'{{employee_name}}'}, {'{{employee_id}}'}, {'{{month}}'}, {'{{year}}'}</div>
                                    </div>
                                </div>
                                <div className="modal-footer">
                                    <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)}>Cancel</button>
                                    <button type="submit" className="btn btn-primary" disabled={loading}>Save Template</button>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default EmailTemplates;
