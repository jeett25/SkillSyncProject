import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import Sidebar from "../components/sidebar";
import './projects.css';

export default function Projects({logout}) {
  const [projects, setProjects] = useState([]);
  const [newProject, setNewProject] = useState({ title: '', description: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const fetchProjects = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        navigate('/login');
        return;
      }

      setLoading(true);
      const response = await axios.get('http://localhost:5001/api/projects', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setProjects(response.data);
      setError('');
    } catch (err) {
      if (err.response?.status === 401) {
        localStorage.removeItem('token');
        navigate('/login');
      } else {
        setError('Failed to fetch projects');
      }
      console.error('Error fetching projects:', err);
    } finally {
      setLoading(false);
    }
  };

  const addProject = async () => {
    if (!newProject.title.trim() || !newProject.description.trim()) {
      setError('Please fill in both title and description');
      return;
    }

    try {
      const token = localStorage.getItem('token');
      if (!token) {
        navigate('/login');
        return;
      }

      setLoading(true);
      await axios.post('http://localhost:5001/api/projects', newProject, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      setNewProject({ title: '', description: '' });
      setError('');
      await fetchProjects();
    } catch (err) {
      if (err.response?.status === 401) {
        localStorage.removeItem('token');
        navigate('/login');
      } else {
        setError('Failed to add project');
      }
      console.error('Error adding project:', err);
    } finally {
      setLoading(false);
    }
  };

  const deleteProject = async (projectId) => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        navigate('/login');
        return;
      }

      await axios.delete(`http://localhost:5001/api/projects/${projectId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      await fetchProjects();
    } catch (err) {
      if (err.response?.status === 401) {
        localStorage.removeItem('token');
        navigate('/login');
      } else {
        setError('Failed to delete project');
      }
      console.error('Error deleting project:', err);
    }
  };

  const handleInputChange = (field, value) => {
    setNewProject(prev => ({
      ...prev,
      [field]: value
    }));
  };

  useEffect(() => {
    fetchProjects();
  }, []);

  if (loading && projects.length === 0) {
    return (
      <div className="projects-container">
        <Sidebar logout={logout} />
        <div className="projects-content">
          <div className="loading">Loading skills...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="projects-container">
       <Sidebar logout={logout} />
      <div className='projects-main'>
      <div className="projects-header">
        <h2 className="projects-title">My Projects</h2>
        <p className="projects-subtitle">Manage and showcase your work</p>
      </div>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      <div className="add-project-section">
        <h3>Add New Project</h3>
        <div className="project-form">
          <input
            type="text"
            className="project-input"
            value={newProject.title}
            onChange={(e) => handleInputChange('title', e.target.value)}
            placeholder="Project Title"
            disabled={loading}
          />
          <textarea
            className="project-textarea"
            value={newProject.description}
            onChange={(e) => handleInputChange('description', e.target.value)}
            placeholder="Project Description"
            rows="4"
            disabled={loading}
          />
          <button 
            className="add-project-btn"
            onClick={addProject}
            disabled={loading || !newProject.title.trim() || !newProject.description.trim()}
          >
            {loading ? 'Adding...' : 'Add Project'}
          </button>
        </div>
      </div>

      <div className="projects-list-section">
        <h3>Your Projects</h3>
        {loading && projects.length === 0 ? (
          <div className="loading">Loading projects...</div>
        ) : projects.length === 0 ? (
          <div className="no-projects">
            <p>No projects yet. Add your first project above!</p>
          </div>
        ) : (
          <div className="projects-grid">
            {projects.map((project, index) => (
              <div key={project.id || index} className="project-card">
                <div className="project-card-header">
                  <h4 className="project-card-title">{project.title}</h4>
                  {project.id && (
                    <button
                      className="delete-btn"
                      onClick={() => deleteProject(project.id)}
                      title="Delete project"
                    >
                      ×
                    </button>
                  )}
                </div>
                <p className="project-card-description">{project.description}</p>
                {project.createdAt && (
                  <div className="project-card-date">
                    Created: {new Date(project.createdAt).toLocaleDateString()}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
      </div>
    </div>
  );
}