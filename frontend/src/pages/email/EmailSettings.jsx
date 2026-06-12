import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Layout from '../../components/Layout';

const EmailSettings = () => {
    const [settings, setSettings] = useState({
        provider_type: 'smtp',
        smtp_host: '',
        smtp_port: '',
        smtp_username: '',
        smtp_password: '',
        use_tls: true,
        use_ssl: false,
        sender_name: '',
        sender_email: '',
        reply_to: ''
    });
    const [loading, setLoading] = useState(false);
    const [testEmail, setTestEmail] = useState('');
    const [message, setMessage] = useState(null);

    const fetchSettings = async () => {
        try {
            const res = await axios.get(`${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/api/email/settings`, {
                headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
            });
            if (res.data.id) setSettings(res.data);
        } catch (error) {
            console.error("Failed to load settings", error);
        }
    };

    useEffect(() => {
        fetchSettings();
    }, []);

    const handleChange = (e) => {
        const { name, value, type, checked } = e.target;
        setSettings({ ...settings, [name]: type === 'checkbox' ? checked : value });
    };

    const handleSave = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            const res = await axios.put(`${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/api/email/settings`, settings, {
                headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
            });
            setMessage({ type: 'success', text: res.data.message });
        } catch (error) {
            setMessage({ type: 'danger', text: 'Failed to save settings' });
        }
        setLoading(false);
    };

    const handleTest = async () => {
        if (!testEmail) {
            setMessage({ type: 'warning', text: 'Please enter an email to test' });
            return;
        }
        setLoading(true);
        try {
            const res = await axios.post(`${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/api/email/test`, { email: testEmail }, {
                headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
            });
            setMessage({ type: 'success', text: res.data.message });
            setTestEmail('');
        } catch (error) {
            setMessage({ type: 'danger', text: 'Failed to send test email' });
        }
        setLoading(false);
    };

    return (
        <Layout>
            <div className="slide-up-animation container-fluid py-4">
                <h2 className="mb-4 text-primary fw-bold">Email Configuration</h2>
                
                {message && <div className={`alert alert-${message.type}`}>{message.text}</div>}
                
                <div className="row">
                    <div className="col-md-8">
                        <div className="card shadow-sm border-0">
                            <div className="card-header bg-white border-bottom-0 pt-4 pb-0">
                                <h5 className="mb-0">SMTP Settings</h5>
                            </div>
                            <div className="card-body">
                                <form onSubmit={handleSave}>
                                    <div className="row mb-3">
                                        <div className="col-md-6">
                                            <label className="form-label">Provider Type</label>
                                            <select className="form-select" name="provider_type" value={settings.provider_type} onChange={handleChange}>
                                                <option value="smtp">Custom SMTP</option>
                                                <option value="gmail">Gmail SMTP</option>
                                                <option value="amazon_ses">Amazon SES</option>
                                            </select>
                                        </div>
                                    </div>
                                    <div className="row mb-3">
                                        <div className="col-md-8">
                                            <label className="form-label">SMTP Host</label>
                                            <input type="text" className="form-control" name="smtp_host" value={settings.smtp_host} onChange={handleChange} placeholder="smtp.example.com" />
                                        </div>
                                        <div className="col-md-4">
                                            <label className="form-label">SMTP Port</label>
                                            <input type="number" className="form-control" name="smtp_port" value={settings.smtp_port} onChange={handleChange} placeholder="587" />
                                        </div>
                                    </div>
                                    <div className="row mb-3">
                                        <div className="col-md-6">
                                            <label className="form-label">SMTP Username</label>
                                            <input type="text" className="form-control" name="smtp_username" value={settings.smtp_username} onChange={handleChange} />
                                        </div>
                                        <div className="col-md-6">
                                            <label className="form-label">SMTP Password</label>
                                            <input type="password" className="form-control" name="smtp_password" value={settings.smtp_password} onChange={handleChange} />
                                        </div>
                                    </div>
                                    <div className="row mb-4">
                                        <div className="col-md-6">
                                            <label className="form-label">Sender Name</label>
                                            <input type="text" className="form-control" name="sender_name" value={settings.sender_name} onChange={handleChange} placeholder="HR Department" />
                                        </div>
                                        <div className="col-md-6">
                                            <label className="form-label">Sender Email</label>
                                            <input type="email" className="form-control" name="sender_email" value={settings.sender_email} onChange={handleChange} placeholder="noreply@company.com" />
                                        </div>
                                    </div>
                                    <div className="mb-4">
                                        <div className="form-check form-check-inline">
                                            <input className="form-check-input" type="checkbox" name="use_tls" checked={settings.use_tls} onChange={handleChange} id="tlsCheck" />
                                            <label className="form-check-label" htmlFor="tlsCheck">Enable TLS</label>
                                        </div>
                                        <div className="form-check form-check-inline">
                                            <input className="form-check-input" type="checkbox" name="use_ssl" checked={settings.use_ssl} onChange={handleChange} id="sslCheck" />
                                            <label className="form-check-label" htmlFor="sslCheck">Enable SSL</label>
                                        </div>
                                    </div>
                                    <button type="submit" className="btn btn-primary px-4 shadow-sm" disabled={loading}>
                                        {loading ? 'Saving...' : 'Save Configuration'}
                                    </button>
                                </form>
                            </div>
                        </div>
                    </div>

                    <div className="col-md-4">
                        <div className="card shadow-sm border-0 bg-light">
                            <div className="card-body">
                                <h5 className="card-title text-dark mb-3">Test Connection</h5>
                                <p className="text-muted small mb-3">Send a test email to verify your SMTP configuration before running campaigns.</p>
                                <input 
                                    type="email" 
                                    className="form-control mb-3" 
                                    placeholder="test@email.com" 
                                    value={testEmail}
                                    onChange={e => setTestEmail(e.target.value)}
                                />
                                <button className="btn btn-outline-primary w-100" onClick={handleTest} disabled={loading}>
                                    Send Test Email
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </Layout>
    );
};

export default EmailSettings;
