import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Layout from '../../components/Layout';

const EmailComposer = () => {
    const [departments, setDepartments] = useState([]);
    const [employees, setEmployees] = useState([]);
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState(null);
    
    const [form, setForm] = useState({
        audience: 'all', // all, department, specific
        department_id: '',
        employee_ids: [],
        subject: '',
        body: ''
    });

    useEffect(() => {
        const fetchData = async () => {
            const token = localStorage.getItem('token');
            const headers = { Authorization: `Bearer ${token}` };
            try {
                const deptRes = await axios.get(`${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/api/departments/`, { headers });
                setDepartments(deptRes.data);
                
                const empRes = await axios.get(`${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/api/employees/?per_page=1000`, { headers });
                setEmployees(empRes.data.employees || []);
            } catch (err) {
                console.error(err);
            }
        };
        fetchData();
    }, []);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setForm({ ...form, [name]: value });
    };

    const handleEmployeeSelect = (e) => {
        const value = Array.from(e.target.selectedOptions, option => option.value);
        setForm({ ...form, employee_ids: value });
    };

    const handleSend = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            const token = localStorage.getItem('token');
            const res = await axios.post(`${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/api/email/compose`, form, {
                headers: { Authorization: `Bearer ${token}` }
            });
            setMessage({ type: 'success', text: res.data.message });
            setForm({ ...form, subject: '', body: '' }); // reset only body
        } catch (error) {
            setMessage({ type: 'danger', text: 'Failed to queue emails.' });
        }
        setLoading(false);
    };

    return (
        <Layout>
            <div className="slide-up-animation container-fluid py-4">
                <h2 className="mb-4 text-primary fw-bold">Compose Campaign</h2>
                
                {message && <div className={`alert alert-${message.type}`}>{message.text}</div>}
                
                <div className="card shadow-sm border-0">
                    <div className="card-body">
                        <form onSubmit={handleSend}>
                            <div className="row mb-4">
                                <div className="col-md-4">
                                    <label className="form-label fw-bold">Target Audience</label>
                                    <select className="form-select" name="audience" value={form.audience} onChange={handleChange}>
                                        <option value="all">All Active Employees</option>
                                        <option value="department">Specific Department</option>
                                        <option value="specific">Specific Employees</option>
                                    </select>
                                </div>
                                
                                {form.audience === 'department' && (
                                    <div className="col-md-4">
                                        <label className="form-label fw-bold">Select Department</label>
                                        <select className="form-select" name="department_id" value={form.department_id} onChange={handleChange} required>
                                            <option value="">-- Choose --</option>
                                            {departments.map(d => <option key={d.id} value={d.id}>{d.name}</option>)}
                                        </select>
                                    </div>
                                )}
                                
                                {form.audience === 'specific' && (
                                    <div className="col-md-8">
                                        <label className="form-label fw-bold">Select Employees (Hold Ctrl to multi-select)</label>
                                        <select className="form-select" multiple name="employee_ids" value={form.employee_ids} onChange={handleEmployeeSelect} required style={{height: '100px'}}>
                                            {employees.map(e => <option key={e.id} value={e.id}>{e.first_name} {e.last_name} ({e.email})</option>)}
                                        </select>
                                    </div>
                                )}
                            </div>

                            <div className="mb-3">
                                <label className="form-label fw-bold">Email Subject</label>
                                <input type="text" className="form-control" name="subject" value={form.subject} onChange={handleChange} placeholder="Company Announcement: ..." required />
                            </div>

                            <div className="mb-4">
                                <label className="form-label fw-bold">Message Body (HTML Supported)</label>
                                <textarea className="form-control" rows="12" name="body" value={form.body} onChange={handleChange} placeholder="<p>Dear {{employee_name}},</p>" required></textarea>
                                <div className="form-text mt-2 text-muted">You can use <code>{'{{employee_name}}'}</code> and <code>{'{{employee_id}}'}</code> to personalize each email.</div>
                            </div>

                            <div className="d-flex justify-content-end">
                                <button type="submit" className="btn btn-primary btn-lg shadow-sm px-5" disabled={loading}>
                                    {loading ? 'Queuing...' : 'Send Bulk Email Queue'}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </Layout>
    );
};

export default EmailComposer;
