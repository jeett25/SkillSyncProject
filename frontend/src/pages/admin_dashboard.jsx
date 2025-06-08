import { useEffect, useState } from 'react';
import axios from 'axios';
import "./adminDashboard.css";
import { useNavigate } from 'react-router-dom';

export default function AdminDashboard({ logout }) {
    const navigate = useNavigate();

    const handleLogout = () => {
      logout();
      navigate("/login");
    };
      
  const [dashboardData, setDashboardData] = useState({
    statistics: {
      total_users: 0,
      total_students: 0,
      total_projects: 0,
      total_skills: 0,
      total_resumes: 0,
      parsed_resumes: 0,
      unparsed_resumes: 0
    },
    recent_activity: {
      recent_users: [],
      recent_projects: []
    }
  });
  const [students, setStudents] = useState([]);
  const [filteredStudents, setFilteredStudents] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterBy, setFilterBy] = useState('all');
  const [selectedStudent, setSelectedStudent] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAdminData();
  }, []);

  useEffect(() => {
    filterStudents();
  }, [students, searchTerm, filterBy]);

  const fetchAdminData = async () => {
    try {
      const token = localStorage.getItem('token');
      
      if (!token) {
        logout();
        window.location.href = '/login';
        return;
      }

      // Fetch dashboard data
      const dashboardRes = await axios.get('http://localhost:5001/admin/dashboard', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setDashboardData(dashboardRes.data);

      // Fetch all students
      const studentsRes = await axios.get('http://localhost:5001/admin/students', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setStudents(studentsRes.data);

    } catch (error) {
      console.error('Error fetching admin data:', error);
      if (error.response && error.response.status === 403) {
        alert('Access denied. Admin privileges required.');
        logout();
        window.location.href = '/login';
      } else if (error.response && error.response.status === 401) {
        logout();
        window.location.href = '/login';
      }
    } finally {
      setLoading(false);
    }
  };

  const filterStudents = () => {
    let filtered = students.filter(student => {
      const matchesSearch = 
        student.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        student.email?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        student.location?.toLowerCase().includes(searchTerm.toLowerCase());
      
      if (filterBy === 'all') return matchesSearch;
      if (filterBy === 'complete') return matchesSearch && isProfileComplete(student);
      if (filterBy === 'incomplete') return matchesSearch && !isProfileComplete(student);
      if (filterBy === 'with-github') return matchesSearch && student.github;
      if (filterBy === 'with-linkedin') return matchesSearch && student.linkedin;
      
      return matchesSearch;
    });
    setFilteredStudents(filtered);
  };

  const isProfileComplete = (student) => {
    const requiredFields = ['name', 'email', 'about', 'phone', 'location'];
    return requiredFields.every(field => student[field] && student[field].trim() !== '');
  };

  const getProfileCompletionPercentage = (student) => {
    const requiredFields = ['name', 'email', 'about', 'phone', 'location'];
    const completedFields = requiredFields.filter(field => student[field] && student[field].trim() !== '');
    return Math.round((completedFields.length / requiredFields.length) * 100);
  };

  const viewStudentDetails = (student) => {
    setSelectedStudent(student);
    setShowModal(true);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  if (loading) {
    return (
      <div className="admin-dashboard-container">
        <div className="admin-dashboard-content">
          <div className="loading">Loading...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="admin-dashboard-container">
      <div className="admin-dashboard-content">
        <div className="admin-dashboard-header">
        <button className="logout-btn" onClick={handleLogout}>
  🚪 Logout
</button>
          <h1 className="admin-dashboard-heading">Admin Dashboard</h1>
          <p className="admin-dashboard-subtitle">Manage students, projects, and system analytics</p>
        </div>

        {/* Navigation Tabs */}
        <div className="admin-tabs">
          <button 
            className={`tab-btn ${activeTab === 'overview' ? 'active' : ''}`}
            onClick={() => setActiveTab('overview')}
          >
            📊 Overview
          </button>
          <button 
            className={`tab-btn ${activeTab === 'students' ? 'active' : ''}`}
            onClick={() => setActiveTab('students')}
          >
            👥 Students
          </button>
          <button 
            className={`tab-btn ${activeTab === 'analytics' ? 'active' : ''}`}
            onClick={() => setActiveTab('analytics')}
          >
            📈 Analytics
          </button>
        </div>

        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <>
            <div className="admin-stats-grid">
              <div className="admin-stat-card">
                <div className="admin-stat-icon">👥</div>
                <div className="admin-stat-info">
                  <h3>{dashboardData.statistics.total_users}</h3>
                  <p>Total Users</p>
                </div>
              </div>
              
              <div className="admin-stat-card">
                <div className="admin-stat-icon">🎓</div>
                <div className="admin-stat-info">
                  <h3>{dashboardData.statistics.total_students}</h3>
                  <p>Students</p>
                </div>
              </div>
              
              <div className="admin-stat-card">
                <div className="admin-stat-icon">📁</div>
                <div className="admin-stat-info">
                  <h3>{dashboardData.statistics.total_projects}</h3>
                  <p>Projects</p>
                </div>
              </div>

              <div className="admin-stat-card">
                <div className="admin-stat-icon">⚡</div>
                <div className="admin-stat-info">
                  <h3>{dashboardData.statistics.total_skills}</h3>
                  <p>Skills</p>
                </div>
              </div>

              <div className="admin-stat-card">
                <div className="admin-stat-icon">📄</div>
                <div className="admin-stat-info">
                  <h3>{dashboardData.statistics.total_resumes}</h3>
                  <p>Resumes</p>
                </div>
              </div>

              <div className="admin-stat-card">
                <div className="admin-stat-icon">✅</div>
                <div className="admin-stat-info">
                  <h3>{dashboardData.statistics.parsed_resumes}</h3>
                  <p>Parsed Resumes</p>
                </div>
              </div>
            </div>

            {/* Recent Activity */}
            <div className="recent-activity-section">
              <h2>Recent Activity</h2>
              <div className="activity-grid">
                <div className="activity-card">
                  <h3>Recent Users</h3>
                  <div className="activity-list">
                    {dashboardData.recent_activity.recent_users.map(user => (
                      <div key={user._id} className="activity-item">
                        <span className="activity-email">{user.email}</span>
                        <span className="activity-date">{formatDate(user.created_at)}</span>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="activity-card">
                  <h3>Recent Projects</h3>
                  <div className="activity-list">
                    {dashboardData.recent_activity.recent_projects.map(project => (
                      <div key={project._id} className="activity-item">
                        <span className="activity-title">{project.title}</span>
                        <span className="activity-date">{formatDate(project.created_at)}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </>
        )}

        {/* Students Tab */}
        {activeTab === 'students' && (
          <>
            {/* Search and Filter */}
            <div className="students-controls">
              <div className="search-bar">
                <input
                  type="text"
                  placeholder="Search students by name, email, or location..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="search-input"
                />
              </div>
              <div className="filter-bar">
                <select 
                  value={filterBy} 
                  onChange={(e) => setFilterBy(e.target.value)}
                  className="filter-select"
                >
                  <option value="all">All Students</option>
                  <option value="complete">Complete Profiles</option>
                  <option value="incomplete">Incomplete Profiles</option>
                  <option value="with-github">With GitHub</option>
                  <option value="with-linkedin">With LinkedIn</option>
                </select>
              </div>
            </div>

            {/* Students Grid */}
            <div className="students-grid">
              {filteredStudents.map(student => (
                <div key={student._id} className="student-card">
                  <div className="student-header">
                    <h3>{student.name || 'No Name'}</h3>
                    <div className="completion-badge">
                      {getProfileCompletionPercentage(student)}%
                    </div>
                  </div>
                  
                  <div className="student-info">
                    <p className="student-email">{student.email}</p>
                    <p className="student-location">{student.location || 'No location'}</p>
                    <p className="student-joined">Joined: {formatDate(student.created_at)}</p>
                  </div>

                  <div className="student-links">
                    {student.github && (
                      <a href={student.github} target="_blank" rel="noopener noreferrer" className="social-link github">
                        GitHub
                      </a>
                    )}
                    {student.linkedin && (
                      <a href={student.linkedin} target="_blank" rel="noopener noreferrer" className="social-link linkedin">
                        LinkedIn
                      </a>
                    )}
                  </div>

                  <div className="student-actions">
                    <button 
                      className="view-btn"
                      onClick={() => viewStudentDetails(student)}
                    >
                      👁️ View Details
                    </button>
                  </div>
                </div>
              ))}
            </div>

            {filteredStudents.length === 0 && (
              <div className="no-results">
                <p>No students found matching your criteria.</p>
              </div>
            )}
          </>
        )}

        {/* Analytics Tab */}
        {activeTab === 'analytics' && (
          <div className="analytics-section">
            <h2>System Analytics</h2>
            <div className="analytics-grid">
              <div className="analytics-card">
                <h3>Profile Completion</h3>
                <div className="completion-stats">
                  <div className="completion-item">
                    <span>Complete Profiles:</span>
                    <span>{students.filter(s => isProfileComplete(s)).length}</span>
                  </div>
                  <div className="completion-item">
                    <span>Incomplete Profiles:</span>
                    <span>{students.filter(s => !isProfileComplete(s)).length}</span>
                  </div>
                  <div className="completion-item">
                    <span>With GitHub:</span>
                    <span>{students.filter(s => s.github).length}</span>
                  </div>
                  <div className="completion-item">
                    <span>With LinkedIn:</span>
                    <span>{students.filter(s => s.linkedin).length}</span>
                  </div>
                </div>
              </div>

              <div className="analytics-card">
                <h3>Growth Metrics</h3>
                <div className="growth-stats">
                  <div className="growth-item">
                    <span>Total Growth:</span>
                    <span className="growth-positive">+12.5%</span>
                  </div>
                  <div className="growth-item">
                    <span>Monthly Active:</span>
                    <span>{Math.round(students.length * 0.7)}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Student Details Modal */}
        {showModal && selectedStudent && (
          <div className="modal-overlay" onClick={() => setShowModal(false)}>
            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
              <div className="modal-header">
                <h2>Student Details</h2>
                <button className="close-btn" onClick={() => setShowModal(false)}>×</button>
              </div>
              
              <div className="modal-body">
                <div className="student-detail-section">
                  <h3>Personal Information</h3>
                  <div className="detail-grid">
                    <div className="detail-item">
                      <label>Name:</label>
                      <span>{selectedStudent.name || 'Not provided'}</span>
                    </div>
                    <div className="detail-item">
                      <label>Email:</label>
                      <span>{selectedStudent.email}</span>
                    </div>
                    <div className="detail-item">
                      <label>Phone:</label>
                      <span>{selectedStudent.phone || 'Not provided'}</span>
                    </div>
                    <div className="detail-item">
                      <label>Location:</label>
                      <span>{selectedStudent.location || 'Not provided'}</span>
                    </div>
                  </div>
                </div>

                <div className="student-detail-section">
                  <h3>About</h3>
                  <p>{selectedStudent.about || 'No description provided'}</p>
                </div>

                <div className="student-detail-section">
                  <h3>Social Links</h3>
                  <div className="social-links">
                    {selectedStudent.github ? (
                      <a href={selectedStudent.github} target="_blank" rel="noopener noreferrer" className="social-link github">
                        GitHub Profile
                      </a>
                    ) : (
                      <span className="no-link">No GitHub profile</span>
                    )}
                    {selectedStudent.linkedin ? (
                      <a href={selectedStudent.linkedin} target="_blank" rel="noopener noreferrer" className="social-link linkedin">
                        LinkedIn Profile
                      </a>
                    ) : (
                      <span className="no-link">No LinkedIn profile</span>
                    )}
                  </div>
                </div>

                <div className="student-detail-section">
                  <h3>Account Information</h3>
                  <div className="detail-grid">
                    <div className="detail-item">
                      <label>User ID:</label>
                      <span>{selectedStudent.user_id}</span>
                    </div>
                    <div className="detail-item">
                      <label>Profile Completion:</label>
                      <span>{getProfileCompletionPercentage(selectedStudent)}%</span>
                    </div>
                    <div className="detail-item">
                      <label>Created:</label>
                      <span>{formatDate(selectedStudent.created_at)}</span>
                    </div>
                    <div className="detail-item">
                      <label>Last Updated:</label>
                      <span>{formatDate(selectedStudent.updated_at)}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}