import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import axios from "axios";
import "./login.css";

export default function Login({ setAuthData }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const loginUser = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      console.log('Attempting login with:', { email, password: '***' });
      
      const res = await axios.post("http://localhost:5001/api/auth/login", {
        email,
        password,
      });
      
      console.log('Login response:', res.data);
      
      if (res.data.access_token && res.data.user) {
        const { access_token, user } = res.data;
        
        // Set authentication data using the setAuthData function from App.js
        setAuthData(access_token, user.role, user.email, user.id);
        
        alert("Login successful!");
        
        // Navigate based on user role
        if (user.role === 'admin') {
          navigate('/admin');
        } else {
          navigate('/');
        }
      } else {
        alert("Login failed: Invalid response from server");
      }
      
    } catch (err) {
      console.error('Login error:', err);
      
      if (err.response) {
        console.error('Error response:', err.response.data);
        const errorMessage = err.response.data.error || err.response.data.message || 'Login failed';
        alert(`Login failed: ${errorMessage}`);
      } else if (err.request) {
        console.error('No response received:', err.request);
        alert('Cannot connect to server. Make sure the backend is running.');
      } else {
        console.error('Error setting up request:', err.message);
        alert('An unexpected error occurred');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={loginUser} className="login-form">
      <h2 className="login-title">Login</h2>
      <input
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        className="login-input"
        placeholder="Email"
        required
        disabled={loading}
      />
      <input
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        className="login-input"
        placeholder="Password"
        required
        disabled={loading}
      />
      <button type="submit" className="login-button" disabled={loading}>
        {loading ? 'Logging in...' : 'Login'}
      </button>

      <p className="register-link">
        Not registered? <Link to="/register">Create an account</Link>
      </p>
    </form>
  );
}