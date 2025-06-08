// src/pages/profile.js
import { useEffect, useState } from 'react';
import axios from 'axios';
import Sidebar from "../components/sidebar";
import "./profile.css";

export default function Profile({ logout }) {
  const [profile, setProfile] = useState({ 
    name: '', 
    email: '', 
    about: '',
    phone: '',
    location: '',
    github: '',
    linkedin: ''
  });
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState(false);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const token = localStorage.getItem('token');
        const response = await axios.get('http://localhost:5001/api/student/profile', {
          headers: { Authorization: `Bearer ${token}` }
        });
        setProfile(response.data);
      } catch (error) {
        console.error('Error fetching profile:', error);
        if (error.response?.status === 401) {
          logout();
        }
      } finally {
        setLoading(false);
      }
    };

    fetchProfile();
  }, [logout]);

  const updateProfile = async () => {
    setUpdating(true);
    try {
      const token = localStorage.getItem('token');
  
      const dataToSend = {
        ...profile,
        email: profile.email // explicitly include email
      };
  
      await axios.put('http://localhost:5001/api/student/profile', dataToSend, {
        headers: { Authorization: `Bearer ${token}` }
      });
  
      alert('Profile updated successfully!');
    } catch (error) {
      console.error('Error updating profile:', error);
      alert('Failed to update profile. Please try again.');
    } finally {
      setUpdating(false);
    }
  };
  

  const handleInputChange = (field, value) => {
    setProfile(prev => ({ ...prev, [field]: value }));
  };

  if (loading) {
    return (
      <div className="profile-container">
        <Sidebar logout={logout} />
        <div className="profile-content">
          <div className="loading">Loading profile...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="profile-container">
      <Sidebar logout={logout} />
      <div className="profile-content">
        <div className="profile-header">
          <h1 className="profile-title">My Profile</h1>
          <p className="profile-subtitle">Manage your personal information</p>
        </div>

        <div className="profile-form-container">
          <div className="form-section">
            <h2 className="section-title">Personal Information</h2>
            <div className="form-grid">
              <div className="form-group">
                <label htmlFor="name">Full Name</label>
                <input
                  id="name"
                  type="text"
                  value={profile.name}
                  onChange={(e) => handleInputChange('name', e.target.value)}
                  placeholder="Enter your full name"
                />
              </div>

              <div className="form-group">
                <label htmlFor="email">Email Address</label>
                <input
                  id="email"
                  type="email"
                  value={profile.email}
                  disabled
                  className="disabled-input"
                />
              </div>

              <div className="form-group">
                <label htmlFor="phone">Phone Number</label>
                <input
                  id="phone"
                  type="tel"
                  value={profile.phone}
                  onChange={(e) => handleInputChange('phone', e.target.value)}
                  placeholder="Enter your phone number"
                />
              </div>

              <div className="form-group">
                <label htmlFor="location">Location</label>
                <input
                  id="location"
                  type="text"
                  value={profile.location}
                  onChange={(e) => handleInputChange('location', e.target.value)}
                  placeholder="City, Country"
                />
              </div>
            </div>

            <div className="form-group full-width">
              <label htmlFor="about">About Me</label>
              <textarea
                id="about"
                value={profile.about}
                onChange={(e) => handleInputChange('about', e.target.value)}
                placeholder="Tell us about yourself..."
                rows="4"
              />
            </div>
          </div>

          <div className="form-section">
            <h2 className="section-title">Social Links</h2>
            <div className="form-grid">
              <div className="form-group">
                <label htmlFor="github">GitHub Profile</label>
                <input
                  id="github"
                  type="url"
                  value={profile.github}
                  onChange={(e) => handleInputChange('github', e.target.value)}
                  placeholder="https://github.com/username"
                />
              </div>

              <div className="form-group">
                <label htmlFor="linkedin">LinkedIn Profile</label>
                <input
                  id="linkedin"
                  type="url"
                  value={profile.linkedin}
                  onChange={(e) => handleInputChange('linkedin', e.target.value)}
                  placeholder="https://linkedin.com/in/username"
                />
              </div>
            </div>
          </div>

          <div className="form-actions">
            <button 
              onClick={updateProfile} 
              disabled={updating}
              className="save-btn"
            >
              {updating ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}