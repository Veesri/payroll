import React, { useState, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';

const Login = ({ role, title }) => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const { login } = useContext(AuthContext);
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        try {
            await login(username, password, role);
            if (role === 'super_admin') navigate('/super-admin/dashboard');
            else if (role === 'hr_admin') navigate('/hr/dashboard');
            else navigate('/employee/dashboard');
        } catch (err) {
            setError(err.response?.data?.message || 'Login failed');
        }
    };

    return (
        <div className="container d-flex justify-content-center align-items-center vh-100">
            <div className="card shadow-lg p-4 login-card" style={{ width: '400px', borderRadius: '15px' }}>
                <div className="text-center mb-4">
                    <h2 className="fw-bold" style={{ color: 'var(--bs-primary)' }}>HRMS</h2>
                    <h5 className="text-muted">{title} Login</h5>
                </div>
                {error && <div className="alert alert-danger">{error}</div>}
                <form onSubmit={handleSubmit}>
                    <div className="mb-3">
                        <label className="form-label fw-bold">Username</label>
                        <input type="text" className="form-control form-control-lg" value={username} 
                               onChange={(e) => setUsername(e.target.value)} required 
                               placeholder="Enter your username" />
                    </div>
                    <div className="mb-4">
                        <label className="form-label fw-bold">Password</label>
                        <input type="password" className="form-control form-control-lg" value={password} 
                               onChange={(e) => setPassword(e.target.value)} required 
                               placeholder="••••••••" />
                    </div>
                    <button type="submit" className="btn btn-primary btn-lg w-100 shadow-sm fw-bold mb-3">Login</button>
                    
                    <div className="text-center mt-3">
                        {role !== 'employee' && <a href="/employee/login" className="text-decoration-none text-muted small me-3 hover-text-primary">Employee Portal</a>}
                        {role !== 'hr_admin' && <a href="/hr/login" className="text-decoration-none text-muted small me-3 hover-text-primary">HR Portal</a>}
                        {role !== 'super_admin' && <a href="/super-admin/login" className="text-decoration-none text-muted small hover-text-primary">Super Admin Portal</a>}
                    </div>
                    <div className="text-center mt-3 border-top pt-2 border-secondary">
                        <span className="text-muted small">Don't have an account? </span>
                        <a href="/register" className="text-decoration-none text-primary small fw-bold">Register here</a>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default Login;
