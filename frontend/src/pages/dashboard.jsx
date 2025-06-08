// src/pages/dashboard.js
import { useEffect, useState } from 'react';
import axios from 'axios';
import Sidebar from "../components/sidebar";
import "./dashboard.css";

export default function Dashboard({ logout }) {
  const [stats, setStats] = useState({
    totalProjects: 0,
    totalSkills: 0,
    userName: ''
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const token = localStorage.getItem('token');
        
        if (!token) {
          logout();
          window.location.href = '/login';
          return;
        }
        
        const res = await axios.get('http://localhost:5001/api/dashboard', {
          headers: { Authorization: `Bearer ${token}` }
        });
  
        console.log('Dashboard response:', res.data); // Debug log
        
        const { profile, stats } = res.data;
  
        setStats({
          userName: profile?.name || 'User',
          totalProjects: stats?.total_projects || 0,
          totalSkills: stats?.total_skills || 0
        });
  
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
        console.error('Error response:', error.response?.data); // Debug log
        
        if (error.response && error.response.status === 401) {
          logout();
          window.location.href = '/login';
        }
      } finally {
        setLoading(false);
      }
    };
  
    fetchDashboardData();
  }, [logout]);

  if (loading) {
    return (
      <div className="dashboard-container">
        <Sidebar logout={logout} />
        <div className="dashboard-content">
          <div className="loading">Loading...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      <Sidebar logout={logout} />
      <div className="dashboard-content">
        <div className="dashboard-header">
          <h1 className="dashboard-heading">
            Welcome back, {stats.userName}!
          </h1>
          <p className="dashboard-subtitle">Here's what's happening with your profile</p>
        </div>
        
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-icon">📁</div>
            <div className="stat-info">
              <h3>{stats.totalProjects}</h3>
              <p>Projects</p>
            </div>
          </div>
          
          <div className="stat-card">
            <div className="stat-icon">⚡</div>
            <div className="stat-info">
              <h3>{stats.totalSkills}</h3>
              <p>Skills</p>
            </div>
          </div>
          
          <div className="stat-card">
            <div className="stat-icon">🎯</div>
            <div className="stat-info">
              <h3>100%</h3>
              <p>Profile Complete</p>
            </div>
          </div>
        </div>

        <div className="quick-actions">
          <h2>Quick Actions</h2>
          <div className="action-buttons">
            <button className="action-btn" onClick={() => window.location.href = '/projects'}>
              <span className="btn-icon">➕</span>
              Add New Project
            </button>
            <button className="action-btn" onClick={() => window.location.href = '/skills'}>
              <span className="btn-icon">⚡</span>
              Add New Skill
            </button>
            <button className="action-btn" onClick={() => window.location.href = '/profile'}>
              <span className="btn-icon">✏️</span>
              Edit Profile
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}