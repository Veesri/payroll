import React, { useContext } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import { FaHome, FaBuilding, FaUsers, FaSignOutAlt, FaCalendarCheck, FaUserCheck, FaRupeeSign, FaMoneyBillWave } from 'react-icons/fa';

const Layout = ({ children }) => {
    const { user, logout } = useContext(AuthContext);
    const location = useLocation();

    const getDashboardPath = (role) => {
        if (role === 'super_admin') return '/super-admin/dashboard';
        if (role === 'hr_admin') return '/hr/dashboard';
        return '/employee/dashboard';
    };

    const menuItems = [
        { path: getDashboardPath(user?.role), name: 'Dashboard', icon: <FaHome /> },
        { path: '/super-admin/users', name: 'User Accounts', icon: <FaUsers />, roles: ['super_admin'] },
        { path: '/departments', name: 'Departments', icon: <FaBuilding />, roles: ['super_admin'] },
        { path: '/employees', name: 'Employees', icon: <FaUsers />, roles: ['super_admin', 'hr_admin'] },
        { path: '/hr/attendance', name: 'Co. Attendance', icon: <FaCalendarCheck />, roles: ['super_admin', 'hr_admin'] },
        { path: '/hr/leave', name: 'Employee Leave Approvals', icon: <FaUserCheck />, roles: ['super_admin', 'hr_admin'] },
        { path: '/hr/apply-leave', name: 'My Leave', icon: <FaCalendarCheck />, roles: ['hr_admin'] },
        { path: '/admin/leave-approvals', name: 'HR Leave Approvals', icon: <FaUserCheck />, roles: ['super_admin'] },
        { path: '/hr/salary', name: 'Salary Config', icon: <FaRupeeSign />, roles: ['super_admin', 'hr_admin'] },
        { path: '/hr/payroll', name: 'Payroll Engine', icon: <FaMoneyBillWave />, roles: ['super_admin', 'hr_admin'] },
        // Employee Portal routes
        { path: '/employee/profile', name: 'Profile', icon: <FaUsers />, roles: ['employee'] },
        { path: '/employee/attendance', name: 'Attendance', icon: <FaBuilding />, roles: ['employee'] },
        { path: '/employee/leave', name: 'Leave', icon: <FaBuilding />, roles: ['employee'] },
        { path: '/employee/salary', name: 'Salary', icon: <FaRupeeSign />, roles: ['employee'] },
        { path: '/employee/payslips', name: 'My Payslips', icon: <FaMoneyBillWave />, roles: ['employee'] },
    ];

    return (
        <div className="d-flex" style={{ minHeight: '100vh' }}>
            {/* Sidebar */}
            <div className="glass-panel text-white p-4 d-flex flex-column" style={{ width: '280px' }}>
                <div className="mb-5">
                    <h3 className="fw-bold text-primary mb-0">HRMS</h3>
                    <small className="text-muted text-uppercase">{user?.role.replace('_', ' ')}</small>
                </div>
                
                <ul className="nav nav-pills flex-column mb-auto gap-2">
                    {menuItems.filter(item => !item.roles || item.roles.includes(user?.role)).map(item => (
                        <li className="nav-item" key={item.path}>
                            <Link to={item.path} className={`nav-link text-white d-flex align-items-center ${location.pathname === item.path ? 'active bg-primary' : 'hover-bg'}`} style={{ borderRadius: '10px' }}>
                                <span className="me-3">{item.icon}</span>
                                {item.name}
                            </Link>
                        </li>
                    ))}
                </ul>
                <hr className="border-secondary" />
                <div className="d-flex align-items-center">
                    <div className="bg-primary rounded-circle d-flex justify-content-center align-items-center me-3 fw-bold" style={{width: '40px', height: '40px'}}>
                        {user?.username?.[0].toUpperCase()}
                    </div>
                    <div>
                        <h6 className="mb-0 fw-bold">{user?.username}</h6>
                        <button className="btn btn-link text-danger p-0 text-decoration-none" onClick={logout}>
                            <FaSignOutAlt className="me-1" /> Logout
                        </button>
                    </div>
                </div>
            </div>

            {/* Main Content */}
            <div className="flex-grow-1 p-4 overflow-auto">
                {children}
            </div>
        </div>
    );
};

export default Layout;
