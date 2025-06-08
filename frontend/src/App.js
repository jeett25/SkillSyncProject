// src/App.js
import { BrowserRouter as Router, Route, Routes, Navigate } from "react-router-dom";
import { useState, useEffect } from "react";
import Login from "./pages/login";
import Register from "./pages/register";
import Dashboard from "./pages/dashboard";
import Profile from "./pages/profile";
import Projects from "./pages/projects";
import Skills from "./pages/skills";
import Resume from "./pages/resume_upload";
import AdminDashboard from "./pages/admin_dashboard";
function App() {
  const [token, setToken] = useState(localStorage.getItem("token"));
  const [userRole, setUserRole] = useState(localStorage.getItem("userRole"));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const storedToken = localStorage.getItem("token");
    const storedRole = localStorage.getItem("userRole");
    
    if (storedToken) {
      setToken(storedToken);
      setUserRole(storedRole);
    }
    setLoading(false);
  }, []);

  const isAuthenticated = () => !!token;
  const isAdmin = () => userRole === 'admin';
  const isUser = () => userRole === 'user' || userRole === null;

  const logout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("userRole");
    localStorage.removeItem("userEmail");
    localStorage.removeItem("userId");
    setToken(null);
    setUserRole(null);
  };

  const setAuthData = (token, role, email, userId) => {
    localStorage.setItem("token", token);
    localStorage.setItem("userRole", role);
    localStorage.setItem("userEmail", email);
    localStorage.setItem("userId", userId);
    setToken(token);
    setUserRole(role);
  };

  // Protected Route Components
  const ProtectedRoute = ({ children, adminOnly = false }) => {
    if (!isAuthenticated()) {
      return <Navigate to="/login" replace />;
    }
    
    if (adminOnly && !isAdmin()) {
      return <Navigate to="/unauthorized" replace />;
    }
    
    return children;
  };

  const PublicRoute = ({ children }) => {
    if (isAuthenticated()) {
      return isAdmin() ? <Navigate to="/admin" replace /> : <Navigate to="/" replace />;
    }
    return children;
  };

  if (loading) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh',
        fontSize: '1.2rem',
        color: '#666'
      }}>
        Loading...
      </div>
    );
  }

  return (
    <Router>
      <Routes>
        {/* Public Routes */}
        <Route
          path="/login"
          element={
            <PublicRoute>
              <Login setAuthData={setAuthData} />
            </PublicRoute>
          }
        />
        <Route
          path="/register"
          element={
            <PublicRoute>
              <Register />
            </PublicRoute>
          }
        />

        {/* User Routes */}
        <Route
          path="/"
          element={
            <ProtectedRoute>
              {isAdmin() ? <Navigate to="/admin" replace /> : <Dashboard logout={logout} />}
            </ProtectedRoute>
          }
        />
        <Route
          path="/profile"
          element={
            <ProtectedRoute>
              {isAdmin() ? <Navigate to="/admin" replace /> : <Profile logout={logout} />}
            </ProtectedRoute>
          }
        />
        <Route
          path="/projects"
          element={
            <ProtectedRoute>
              {isAdmin() ? <Navigate to="/admin" replace /> : <Projects logout={logout} />}
            </ProtectedRoute>
          }
        />
        <Route
          path="/skills"
          element={
            <ProtectedRoute>
              {isAdmin() ? <Navigate to="/admin" replace /> : <Skills logout={logout} />}
            </ProtectedRoute>
          }
        />
        <Route
          path="/resume"
          element={
            <ProtectedRoute>
              {isAdmin() ? <Navigate to="/admin" replace /> : <Resume logout={logout} />}
            </ProtectedRoute>
          }
        />

        {/* Admin Routes */}
        <Route
          path="/admin"
          element={
            <ProtectedRoute adminOnly={true}>
              <AdminDashboard logout={logout} />
            </ProtectedRoute>
          }
        />

        {/* Error Routes */}
        <Route
          path="/unauthorized"
          element={
            <div style={{
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'center',
              alignItems: 'center',
              height: '100vh',
              textAlign: 'center',
              padding: '2rem'
            }}>
              <h1 style={{ color: '#dc3545', marginBottom: '1rem' }}>Access Denied</h1>
              <p style={{ color: '#666', marginBottom: '2rem' }}>
                You don't have permission to access this page.
              </p>
              <button
                onClick={() => window.history.back()}
                style={{
                  padding: '0.75rem 1.5rem',
                  background: '#4CAF50',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  fontSize: '1rem'
                }}
              >
                Go Back
              </button>
            </div>
          }
        />

        {/* 404 Route */}
        <Route
          path="*"
          element={
            <div style={{
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'center',
              alignItems: 'center',
              height: '100vh',
              textAlign: 'center',
              padding: '2rem'
            }}>
              <h1 style={{ color: '#dc3545', marginBottom: '1rem' }}>404 - Page Not Found</h1>
              <p style={{ color: '#666', marginBottom: '2rem' }}>
                The page you're looking for doesn't exist.
              </p>
              <button
                onClick={() => window.location.href = isAdmin() ? '/admin' : '/'}
                style={{
                  padding: '0.75rem 1.5rem',
                  background: '#4CAF50',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  fontSize: '1rem'
                }}
              >
                Go Home
              </button>
            </div>
          }
        />
      </Routes>
    </Router>
  );
}

export default App;