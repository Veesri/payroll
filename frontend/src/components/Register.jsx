import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const Register = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [email, setEmail] = useState('');
    const [firstName, setFirstName] = useState('');
    const [lastName, setLastName] = useState('');
    const [role, setRole] = useState('employee');
    const [success, setSuccess] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setSuccess('');
        setLoading(true);

        try {
            const res = await axios.post(`${import.meta.env.VITE_API_URL || 'http://localhost:5000'}/api/auth/register`, {
                username,
                password,
                email,
                first_name: firstName,
                last_name: lastName,
                role
            });
            setSuccess(res.data.message);
            setUsername('');
            setPassword('');
            setEmail('');
            setFirstName('');
            setLastName('');
            setTimeout(() => {
                navigate('/');
            }, 3000);
        } catch (err) {
            setError(err.response?.data?.message || 'Registration failed');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="container d-flex justify-content-center align-items-center min-vh-100 py-5">
            <div className="card shadow-lg p-4 login-card" style={{ width: '500px', borderRadius: '15px' }}>
                <div className="text-center mb-4">
                    <h2 className="fw-bold" style={{ color: 'var(--bs-primary)' }}>HRMS</h2>
                    <h5 className="text-muted">Register New Account</h5>
                    <p className="text-muted small">Submit details for admin approval</p>
                </div>
                {error && <div className="alert alert-danger">{error}</div>}
                {success && <div className="alert alert-success">{success}</div>}
                
                <form onSubmit={handleSubmit}>
                    <div className="row g-3 mb-3">
                        <div className="col-md-6">
                            <label className="form-label fw-bold">First Name</label>
                            <input type="text" className="form-control" value={firstName} 
                                   onChange={(e) => setFirstName(e.target.value)} required 
                                   placeholder="John" />
                        </div>
                        <div className="col-md-6">
                            <label className="form-label fw-bold">Last Name</label>
                            <input type="text" className="form-control" value={lastName} 
                                   onChange={(e) => setLastName(e.target.value)} required 
                                   placeholder="Doe" />
                        </div>
                    </div>

                    <div className="mb-3">
                        <label className="form-label fw-bold">Email Address</label>
                        <input type="email" className="form-control" value={email} 
                               onChange={(e) => setEmail(e.target.value)} required 
                               placeholder="john.doe@example.com" />
                    </div>

                    <div className="mb-3">
                        <label className="form-label fw-bold">Username</label>
                        <input type="text" className="form-control" value={username} 
                               onChange={(e) => setUsername(e.target.value)} required 
                               placeholder="johndoe123" />
                    </div>

                    <div className="mb-3">
                        <label className="form-label fw-bold">Password</label>
                        <input type="password" className="form-control" value={password} 
                               onChange={(e) => setPassword(e.target.value)} required 
                               placeholder="••••••••" />
                    </div>

                    <div className="mb-4">
                        <label className="form-label fw-bold">Select Role</label>
                        <select className="form-select" value={role} onChange={(e) => setRole(e.target.value)}>
                            <option value="employee">Employee</option>
                            <option value="hr_admin">HR Admin</option>
                        </select>
                    </div>

                    <button type="submit" className="btn btn-primary btn-lg w-100 shadow-sm fw-bold mb-3" disabled={loading}>
                        {loading ? 'Submitting...' : 'Register'}
                    </button>
                    
                    <div className="text-center mt-3">
                        <a href="/" className="text-decoration-none text-muted small hover-text-primary">Already have an account? Login here</a>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default Register;
