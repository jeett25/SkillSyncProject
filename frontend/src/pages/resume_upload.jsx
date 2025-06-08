// src/pages/resume.js
import { useEffect, useState } from 'react';
import axios from 'axios';
import Sidebar from "../components/sidebar";
import "./resume_upload.css";

export default function Resume({ logout }) {
  const [resumeInfo, setResumeInfo] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [parsing, setParsing] = useState(false);
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState('');
  const [dragActive, setDragActive] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchResumeInfo();
  }, []);

  const fetchResumeInfo = async () => {
    try {
      const token = localStorage.getItem('token');
      
      if (!token) {
        logout();
        window.location.href = '/login';
        return;
      }

      const response = await axios.get('http://localhost:5001/api/resume/info', {
        headers: { Authorization: `Bearer ${token}` }
      });

      setResumeInfo(response.data);
    } catch (error) {
      console.error('Error fetching resume info:', error);
      if (error.response && error.response.status === 404) {
        setResumeInfo(null);
      } else if (error.response && error.response.status === 401) {
        logout();
        window.location.href = '/login';
      }
    } finally {
      setLoading(false);
    }
  };

  const showMessage = (msg, type) => {
    setMessage(msg);
    setMessageType(type);
    setTimeout(() => {
      setMessage('');
      setMessageType('');
    }, 5000);
  };

  const handleFileUpload = async (file) => {
    if (!file) return;

    // Validate file type
    const allowedTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
    if (!allowedTypes.includes(file.type)) {
      showMessage('Please upload PDF, DOC, or DOCX files only', 'error');
      return;
    }

    // Validate file size (5MB)
    if (file.size > 5 * 1024 * 1024) {
      showMessage('File size must be less than 5MB', 'error');
      return;
    }

    setUploading(true);
    const formData = new FormData();
    formData.append('resume', file);

    try {
      const token = localStorage.getItem('token');
      const response = await axios.post('http://localhost:5001/api/resume/upload', formData, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'multipart/form-data'
        }
      });

      showMessage(response.data.message, 'success');
      fetchResumeInfo();
    } catch (error) {
      console.error('Upload error:', error);
      showMessage(error.response?.data?.message || 'Upload failed', 'error');
      
      if (error.response && error.response.status === 401) {
        logout();
        window.location.href = '/login';
      }
    } finally {
      setUploading(false);
    }
  };

  const handleParseResume = async () => {
    setParsing(true);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post('http://localhost:5001/api/resume/parse', {}, {
        headers: { Authorization: `Bearer ${token}` }
      });

      showMessage(response.data.message, 'success');
      fetchResumeInfo();
    } catch (error) {
      console.error('Parse error:', error);
      showMessage(error.response?.data?.message || 'Parsing failed', 'error');
      
      if (error.response && error.response.status === 401) {
        logout();
        window.location.href = '/login';
      }
    } finally {
      setParsing(false);
    }
  };

  const handleDeleteResume = async () => {
    if (!window.confirm('Are you sure you want to delete your resume?')) {
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const response = await axios.delete('http://localhost:5001/api/resume/delete', {
        headers: { Authorization: `Bearer ${token}` }
      });

      showMessage(response.data.message, 'success');
      setResumeInfo(null);
    } catch (error) {
      console.error('Delete error:', error);
      showMessage(error.response?.data?.message || 'Deletion failed', 'error');
      
      if (error.response && error.response.status === 401) {
        logout();
        window.location.href = '/login';
      }
    }
  };

  const handleDragEnter = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      handleFileUpload(files[0]);
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

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
        <div className="resume-container">
          <div className="resume-header">
            <h1 className="dashboard-heading">Resume Manager</h1>
            <p className="dashboard-subtitle">Upload, parse, and manage your resume</p>
          </div>

          {/* Message Display */}
          {message && (
            <div className={`message-alert ${messageType}`}>
              <span className="message-icon">
                {messageType === 'error' ? '❌' : '✅'}
              </span>
              <span>{message}</span>
            </div>
          )}

          {/* No Resume - Upload Section */}
          {!resumeInfo && (
            <div className="upload-section">
              <div 
                className={`upload-dropzone ${dragActive ? 'drag-active' : ''}`}
                onDragEnter={handleDragEnter}
                onDragLeave={handleDragLeave}
                onDragOver={handleDragOver}
                onDrop={handleDrop}
              >
                <div className="upload-icon">📄</div>
                <h3>Upload Your Resume</h3>
                <p>Drag and drop your resume here, or click to browse</p>
                <p className="file-requirements">
                  Supported formats: PDF, DOC, DOCX (Max 5MB)
                </p>
                
                <input
                  type="file"
                  id="resume-input"
                  accept=".pdf,.doc,.docx"
                  onChange={(e) => handleFileUpload(e.target.files[0])}
                  className="file-input"
                  disabled={uploading}
                />
                <label htmlFor="resume-input" className="browse-btn">
                  {uploading ? 'Uploading...' : 'Browse Files'}
                </label>
              </div>
            </div>
          )}

          {/* Resume Info Section */}
          {resumeInfo && (
            <div className="resume-info-card">
              <div className="card-header">
                <div className="header-left">
                  <div className="file-icon">📁</div>
                  <div>
                    <h3 className="filename">{resumeInfo.original_filename}</h3>
                    <p className="file-meta">
                      {formatFileSize(resumeInfo.file_size)} • {resumeInfo.file_type.toUpperCase()} • 
                      Uploaded {formatDate(resumeInfo.upload_date)}
                    </p>
                  </div>
                </div>
                <div className="status-badge">
                  <span className="status-icon">
                    {resumeInfo.parsed ? '✅' : '❌'}
                  </span>
                  <span>{resumeInfo.parsed ? 'Parsed' : 'Not Parsed'}</span>
                </div>
              </div>

              {/* Skills Section */}
              {resumeInfo.parsed && resumeInfo.extracted_skills && resumeInfo.extracted_skills.length > 0 && (
                <div className="skills-section">
                  <h4>Extracted Skills ({resumeInfo.extracted_skills.length})</h4>
                  <div className="skills-grid">
                    {resumeInfo.extracted_skills.map((skill, index) => (
                      <span key={index} className="skill-tag">{skill}</span>
                    ))}
                  </div>
                </div>
              )}

              {/* Action Buttons */}
              <div className="action-buttons">
                {!resumeInfo.parsed && (
                  <button 
                    onClick={handleParseResume}
                    disabled={parsing}
                    className="action-btn btn-primary"
                  >
                    <span className="btn-icon">👁️</span>
                    {parsing ? 'Parsing...' : 'Parse Resume'}
                  </button>
                )}
                
                <input
                  type="file"
                  id="replace-input"
                  accept=".pdf,.doc,.docx"
                  onChange={(e) => handleFileUpload(e.target.files[0])}
                  className="file-input"
                  disabled={uploading}
                />
                <label htmlFor="replace-input" className="action-btn btn-secondary">
                  <span className="btn-icon">🔄</span>
                  {uploading ? 'Uploading...' : 'Replace Resume'}
                </label>

                <button 
                  onClick={handleDeleteResume}
                  className="action-btn btn-danger"
                >
                  <span className="btn-icon">🗑️</span>
                  Delete Resume
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}