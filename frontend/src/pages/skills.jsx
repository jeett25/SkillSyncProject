import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import Sidebar from "../components/sidebar";
import './skills.css';

export default function Skills({ logout }) {
  const [skills, setSkills] = useState([]);
  const [newSkill, setNewSkill] = useState('');
  const [skillLevel, setSkillLevel] = useState('beginner');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const skillLevels = [
    { value: 'beginner', label: 'Beginner', color: '#68d391' },
    { value: 'intermediate', label: 'Intermediate', color: '#4299e1' },
    { value: 'advanced', label: 'Advanced', color: '#9f7aea' },
    { value: 'expert', label: 'Expert', color: '#f56565' }
  ];

  const fetchSkills = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        logout();
        navigate('/login');
        return;
      }

      setLoading(true);
      // Using port 5001 to match your backend
      const response = await axios.get('http://localhost:5001/api/skills', {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      console.log('Skills response:', response.data); // Debug log
      setSkills(response.data);
      setError('');
    } catch (err) {
      console.error('Error fetching skills:', err);
      if (err.response?.status === 401) {
        localStorage.removeItem('token');
        logout();
        navigate('/login');
      } else {
        setError('Failed to fetch skills');
      }
    } finally {
      setLoading(false);
    }
  };

  const addSkill = async () => {
    if (!newSkill.trim()) {
      setError('Please enter a skill name');
      return;
    }

    // Check if skill already exists
    const skillExists = skills.some(
      skill => skill.name?.toLowerCase() === newSkill.toLowerCase() || 
               skill.skill?.toLowerCase() === newSkill.toLowerCase() ||
               (typeof skill === 'string' && skill.toLowerCase() === newSkill.toLowerCase())
    );

    if (skillExists) {
      setError('This skill already exists');
      return;
    }

    try {
      const token = localStorage.getItem('token');
      if (!token) {
        logout();
        navigate('/login');
        return;
      }

      setLoading(true);
      const skillData = {
        skill: newSkill.trim(),
        level: skillLevel
      };

      // Using port 5001
      await axios.post('http://localhost:5001/api/skills', skillData, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      setNewSkill('');
      setSkillLevel('beginner');
      setError('');
      await fetchSkills();
    } catch (err) {
      console.error('Error adding skill:', err);
      if (err.response?.status === 401) {
        localStorage.removeItem('token');
        logout();
        navigate('/login');
      } else {
        setError(err.response?.data?.message || 'Failed to add skill');
      }
    } finally {
      setLoading(false);
    }
  };

  const deleteSkill = async (skillId, skillName) => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        logout();
        navigate('/login');
        return;
      }

      // Handle both old format (string) and new format (object with id)
      const deleteUrl = skillId 
        ? `http://localhost:5001/api/skills/${skillId}`
        : `http://localhost:5001/api/skills`;

      const deleteData = skillId ? {} : { skill: skillName };

      await axios.delete(deleteUrl, {
        headers: { Authorization: `Bearer ${token}` },
        data: deleteData
      });
      
      await fetchSkills();
      setError('');
    } catch (err) {
      console.error('Error deleting skill:', err);
      if (err.response?.status === 401) {
        localStorage.removeItem('token');
        logout();
        navigate('/login');
      } else {
        setError('Failed to delete skill');
      }
    }
  };

  const updateSkillLevel = async (skillId, newLevel) => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        logout();
        navigate('/login');
        return;
      }

      await axios.put(`http://localhost:5001/api/skills/${skillId}`, 
        { level: newLevel },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      await fetchSkills();
      setError('');
    } catch (err) {
      console.error('Error updating skill:', err);
      if (err.response?.status === 401) {
        localStorage.removeItem('token');
        logout();
        navigate('/login');
      } else {
        setError('Failed to update skill level');
      }
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      addSkill();
    }
  };

  const getSkillLevelColor = (level) => {
    const skillLevel = skillLevels.find(sl => sl.value === level);
    return skillLevel ? skillLevel.color : '#68d391';
  };

  const groupedSkills = skillLevels.reduce((acc, level) => {
    acc[level.value] = skills.filter(skill => 
      skill.level === level.value || (!skill.level && level.value === 'beginner')
    );
    return acc;
  }, {});

  useEffect(() => {
    fetchSkills();
  }, []);

  if (loading && skills.length === 0) {
    return (
      <div className="skills-container">
        <Sidebar logout={logout} />
        <div className="skills-content">
          <div className="loading">Loading skills...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="skills-container">
      <Sidebar logout={logout} />
      <div className="skills-content">
        <div className="skills-header">
          <h2 className="skills-title">My Skills</h2>
          <p className="skills-subtitle">Track and showcase your abilities</p>
        </div>

        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        <div className="add-skill-section">
          <h3>Add New Skill</h3>
          <div className="skill-form">
            <div className="form-row">
              <input
                type="text"
                className="skill-input"
                value={newSkill}
                onChange={(e) => setNewSkill(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Enter skill name (e.g., JavaScript, Python, Design)"
                disabled={loading}
              />
              <select
                className="skill-level-select"
                value={skillLevel}
                onChange={(e) => setSkillLevel(e.target.value)}
                disabled={loading}
              >
                {skillLevels.map(level => (
                  <option key={level.value} value={level.value}>
                    {level.label}
                  </option>
                ))}
              </select>
            </div>
            <button 
              className="add-skill-btn"
              onClick={addSkill}
              disabled={loading || !newSkill.trim()}
            >
              {loading ? 'Adding...' : 'Add Skill'}
            </button>
          </div>
        </div>

        <div className="skills-list-section">
          <div className="skills-summary">
            <h3>Your Skills ({skills.length})</h3>
            <div className="skills-stats">
              {skillLevels.map(level => (
                <div key={level.value} className="skill-stat">
                  <div 
                    className="skill-stat-color" 
                    style={{ backgroundColor: level.color }}
                  ></div>
                  <span className="skill-stat-label">
                    {level.label}: {groupedSkills[level.value]?.length || 0}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {skills.length === 0 ? (
            <div className="no-skills">
              <p>No skills added yet. Start building your skill portfolio!</p>
            </div>
          ) : (
            <div className="skills-display">
              {skillLevels.map(level => {
                const levelSkills = groupedSkills[level.value];
                if (!levelSkills || levelSkills.length === 0) return null;
                
                return (
                  <div key={level.value} className="skill-level-group">
                    <h4 className="skill-level-title" style={{ color: level.color }}>
                      {level.label} ({levelSkills.length})
                    </h4>
                    <div className="skills-grid">
                      {levelSkills.map((skill, index) => {
                        // Handle different skill data formats
                        const skillName = skill.skill || skill.name || skill;
                        const skillId = skill.id || skill._id;
                        const skillLevel = skill.level || 'beginner';
                        
                        return (
                          <div key={skillId || index} className="skill-card">
                            <div className="skill-card-content">
                              <span className="skill-name">{skillName}</span>
                              <div 
                                className="skill-level-indicator"
                                style={{ backgroundColor: getSkillLevelColor(skillLevel) }}
                              ></div>
                            </div>
                            <div className="skill-actions">
                              {skillId && (
                                <select
                                  className="skill-level-update"
                                  value={skillLevel}
                                  onChange={(e) => updateSkillLevel(skillId, e.target.value)}
                                  title="Update skill level"
                                >
                                  {skillLevels.map(level => (
                                    <option key={level.value} value={level.value}>
                                      {level.label}
                                    </option>
                                  ))}
                                </select>
                              )}
                              <button
                                className="delete-skill-btn"
                                onClick={() => deleteSkill(skillId, skillName)}
                                title="Delete skill"
                              >
                                ×
                              </button>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}