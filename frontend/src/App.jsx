import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './AuthContext';
import Dashboard from './Dashboard';
import Login from './Login';
import Register from './Register';
import Home from './Home';

const LoadingScreen = () => (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <span className="spinner" style={{ width: 24, height: 24 }} />
    </div>
);

// Redirects authenticated users away from login/register to dashboard
const PublicRoute = ({ children }) => {
    const { token, loading } = useAuth();
    if (loading) return <LoadingScreen />;
    return token ? <Navigate to="/dashboard" replace /> : children;
};

// Redirects unauthenticated users to login
const PrivateRoute = ({ children }) => {
    const { token, loading } = useAuth();
    if (loading) return <LoadingScreen />;
    return token ? children : <Navigate to="/login" replace />;
};

function AppRoutes() {
    return (
        <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/login" element={<PublicRoute><Login /></PublicRoute>} />
            <Route path="/register" element={<PublicRoute><Register /></PublicRoute>} />
            <Route
                path="/dashboard"
                element={
                    <PrivateRoute>
                        <Dashboard />
                    </PrivateRoute>
                }
            />
        </Routes>
    );
}

function App() {
    return (
        <Router>
            <AuthProvider>
                <AppRoutes />
            </AuthProvider>
        </Router>
    );
}

export default App;
