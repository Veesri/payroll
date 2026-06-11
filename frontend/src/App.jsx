import React, { useContext } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, AuthContext } from './context/AuthContext';
import Login from './components/Login';
import Register from './components/Register';
import SuperAdminDashboard from './pages/SuperAdminDashboard';
import UserManagement from './pages/UserManagement';
import HRDashboard from './pages/HRDashboard';
import DepartmentManagement from './pages/DepartmentManagement';
import EmployeeManagement from './pages/EmployeeManagement';
import EmployeeDashboard from './pages/EmployeeDashboard';
import EmployeeProfile from './pages/EmployeeProfile';
import EmployeeAttendance from './pages/EmployeeAttendance';
import EmployeeLeave from './pages/EmployeeLeave';
import EmployeeSalary from './pages/EmployeeSalary';
import EmployeePayslips from './pages/EmployeePayslips';
import SalaryStructures from './pages/SalaryStructures';
import PayrollDashboard from './pages/PayrollDashboard';
import HRLeaveManagement from './pages/HRLeaveManagement';
import HRAttendance from './pages/HRAttendance';
import HRApplyLeave from './pages/HRApplyLeave';
import SuperAdminLeaveApprovals from './pages/SuperAdminLeaveApprovals';

const ProtectedRoute = ({ children, allowedRoles }) => {
    const { user, loading } = useContext(AuthContext);
    
    if (loading) return <div>Loading...</div>;
    
    if (!user) {
        if (allowedRoles.includes('super_admin')) return <Navigate to="/super-admin/login" />;
        if (allowedRoles.includes('hr_admin')) return <Navigate to="/hr/login" />;
        return <Navigate to="/employee/login" />;
    }
    
    if (!allowedRoles.includes(user.role)) {
        return <Navigate to="/" />;
    }
    
    return children;
};

const App = () => {
    return (
        <AuthProvider>
            <Router>
                <Routes>
                    {/* Redirect root to employee login */}
                    <Route path="/" element={<Navigate to="/employee/login" />} />
                    
                    {/* Login & Register Routes */}
                    <Route path="/super-admin/login" element={<Login role="super_admin" title="Super Admin" />} />
                    <Route path="/hr/login" element={<Login role="hr_admin" title="HR Admin" />} />
                    <Route path="/employee/login" element={<Login role="employee" title="Employee" />} />
                    <Route path="/register" element={<Register />} />

                    {/* Protected Dashboard Routes */}
                    <Route path="/super-admin/dashboard" element={
                        <ProtectedRoute allowedRoles={['super_admin']}>
                            <SuperAdminDashboard />
                        </ProtectedRoute>
                    } />
                    <Route path="/super-admin/users" element={
                        <ProtectedRoute allowedRoles={['super_admin']}>
                            <UserManagement />
                        </ProtectedRoute>
                    } />
                    <Route path="/hr/dashboard" element={
                        <ProtectedRoute allowedRoles={['hr_admin']}>
                            <HRDashboard />
                        </ProtectedRoute>
                    } />
                    <Route path="/hr-admin/dashboard" element={
                        <ProtectedRoute allowedRoles={['hr_admin']}>
                            <HRDashboard />
                        </ProtectedRoute>
                    } />
                    <Route path="/hr/attendance" element={
                        <ProtectedRoute allowedRoles={['hr_admin', 'super_admin']}>
                            <HRAttendance />
                        </ProtectedRoute>
                    } />
                    <Route path="/hr/leave" element={
                        <ProtectedRoute allowedRoles={['hr_admin', 'super_admin']}>
                            <HRLeaveManagement />
                        </ProtectedRoute>
                    } />
                    <Route path="/hr/apply-leave" element={
                        <ProtectedRoute allowedRoles={['hr_admin']}>
                            <HRApplyLeave />
                        </ProtectedRoute>
                    } />
                    <Route path="/admin/leave-approvals" element={
                        <ProtectedRoute allowedRoles={['super_admin']}>
                            <SuperAdminLeaveApprovals />
                        </ProtectedRoute>
                    } />
                    <Route path="/hr/salary" element={
                        <ProtectedRoute allowedRoles={['hr_admin', 'super_admin']}>
                            <SalaryStructures />
                        </ProtectedRoute>
                    } />
                    <Route path="/hr/payroll" element={
                        <ProtectedRoute allowedRoles={['hr_admin', 'super_admin']}>
                            <PayrollDashboard />
                        </ProtectedRoute>
                    } />
                    <Route path="/employee/dashboard" element={
                        <ProtectedRoute allowedRoles={['employee']}>
                            <EmployeeDashboard />
                        </ProtectedRoute>
                    } />
                    <Route path="/employee/profile" element={
                        <ProtectedRoute allowedRoles={['employee']}>
                            <EmployeeProfile />
                        </ProtectedRoute>
                    } />
                    <Route path="/employee/attendance" element={
                        <ProtectedRoute allowedRoles={['employee']}>
                            <EmployeeAttendance />
                        </ProtectedRoute>
                    } />
                    <Route path="/employee/leave" element={
                        <ProtectedRoute allowedRoles={['employee']}>
                            <EmployeeLeave />
                        </ProtectedRoute>
                    } />
                    <Route path="/employee/salary" element={
                        <ProtectedRoute allowedRoles={['employee']}>
                            <EmployeeSalary />
                        </ProtectedRoute>
                    } />
                    <Route path="/employee/payslips" element={
                        <ProtectedRoute allowedRoles={['employee']}>
                            <EmployeePayslips />
                        </ProtectedRoute>
                    } />

                    {/* Shared Management Routes */}
                    <Route path="/departments" element={
                        <ProtectedRoute allowedRoles={['super_admin']}>
                            <DepartmentManagement />
                        </ProtectedRoute>
                    } />
                    <Route path="/employees" element={
                        <ProtectedRoute allowedRoles={['super_admin', 'hr_admin']}>
                            <EmployeeManagement />
                        </ProtectedRoute>
                    } />

                    {/* Catch all unmatched routes */}
                    <Route path="*" element={<Navigate to="/" />} />
                </Routes>
            </Router>
        </AuthProvider>
    );
};

export default App;
