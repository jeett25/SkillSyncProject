// src/components/sidebar.js
import { Link, useNavigate } from "react-router-dom";
import "./sidebar.css";


export default function Sidebar({ logout }) {
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <h3>SkillSync</h3>
      </div>
      <nav className="sidebar-nav">
        <Link to="/" className="sidebar-link">
          <span className="sidebar-icon">🏠</span>
          Dashboard
        </Link>
        <Link to="/profile" className="sidebar-link">
          <span className="sidebar-icon">👤</span>
          Profile
        </Link>
        <Link to="/projects" className="sidebar-link">
          <span className="sidebar-icon">📁</span>
          Projects
        </Link>
        <Link to="/skills" className="sidebar-link">
          <span className="sidebar-icon">⚡</span>
          Skills
        </Link>
        <Link to="/resume" className="sidebar-link">
          <span className="sidebar-icon">📄</span>
          Resume
        </Link>
      </nav>
      <div className="sidebar-footer">
        <button onClick={handleLogout} className="logout-btn">
          <span className="sidebar-icon">🚪</span>
          Logout
        </button>
      </div>
    </div>
  );
}