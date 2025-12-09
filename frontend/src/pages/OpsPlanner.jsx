import { useState, useEffect } from 'react';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Upload, Trash2, User, X, CheckCircle, XCircle } from 'lucide-react';
import DashboardLayout from '../components/DashboardLayout';
import AgentNavigation from '../components/AgentNavigation';
import AdminNavigation from '../components/AdminNavigation';
import apiClient from '../services/api';

export default function OpsPlanner() {
  const [missions, setMissions] = useState([]);
  const [failedMissionsData, setFailedMissionsData] = useState([]);
  const [availableAgents, setAvailableAgents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showCompletedView, setShowCompletedView] = useState(false);
  const [showFailedView, setShowFailedView] = useState(false);
  const [showAssignModal, setShowAssignModal] = useState(false);
  const [showSubmitModal, setShowSubmitModal] = useState(false);
  const [selectedMission, setSelectedMission] = useState(null);
  const [currentUser, setCurrentUser] = useState(null);
  const [createForm, setCreateForm] = useState({ 
    title: '', 
    description: '', 
    difficulty: 'search',
    due_date: '',
    tags: ''
  });
  const [submitForm, setSubmitForm] = useState({
    status: 'completed',
    notes: ''
  });

  useEffect(() => {
    fetchCurrentUser();
  }, []);

  useEffect(() => {
    if (currentUser) {
      fetchMissions();
    }
  }, [currentUser]);

  const fetchCurrentUser = async () => {
    try {
      const response = await apiClient.get('/auth/me');
      setCurrentUser(response);
    } catch (err) {
      console.error('Error fetching current user:', err);
    }
  };

  const fetchMissions = async () => {
    try {
      setLoading(true);
      setError(null);
      
      if (currentUser?.role === 'agent') {
        // Agent: fetch "My Work"
        const response = await apiClient.get('/api/ops-planner/my-work');
        const allMissions = [
          ...response.assigned_missions.map(m => ({ ...m, id: m._id || m.id })),
          ...response.completed_missions.map(m => ({ ...m, id: m._id || m.id }))
        ];
        setMissions(allMissions);
        // Store failed missions separately (they have status 'pending' but were failed by this agent)
        setFailedMissionsData(response.failed_missions.map(m => ({ ...m, id: m._id || m.id })));
      } else {
        // Admin: fetch kanban board
        const response = await apiClient.get('/api/ops-planner/board');
        const allMissions = [];
        response.columns.forEach(column => {
          // Map _id to id for consistency
          const mappedMissions = column.missions.map(m => ({
            ...m,
            id: m._id || m.id
          }));
          allMissions.push(...mappedMissions);
        });
        setMissions(allMissions);
      }
    } catch (err) {
      console.error('Error fetching missions:', err);
      setError(err.message);
      setMissions([]);
    } finally {
      setLoading(false);
    }
  };

  const openMissions = missions.filter(m => m.status === 'pending');
  const inProgressMissions = missions.filter(m => m.status === 'in_progress');
  const completedMissions = missions.filter(m => m.status === 'completed');
  const failedMissions = failedMissionsData; // Use the separate failed missions data from API

  const handleCreateMission = async (e) => {
    e.preventDefault();
    try {
      const tagsArray = createForm.tags.split(',').map(tag => tag.trim()).filter(tag => tag.length > 0);
      const missionData = {
        title: createForm.title,
        description: createForm.description,
        difficulty: createForm.difficulty,
        due_date: createForm.due_date ? new Date(createForm.due_date).toISOString() : undefined,
        tags: tagsArray,
      };
      await apiClient.post('/api/ops-planner/missions', missionData);
      await fetchMissions();
      setShowCreateModal(false);
      setCreateForm({ title: '', description: '', difficulty: 'search', due_date: '', tags: '' });
    } catch (err) {
      console.error('Error creating mission:', err);
      alert('Failed to create mission: ' + (err.message || 'Unknown error'));
    }
  };

  const handleDeleteMission = async (missionId) => {
    if (window.confirm('Are you sure you want to abort this mission?')) {
      try {
        await apiClient.delete(`/api/ops-planner/missions/${missionId}`);
        await fetchMissions();
      } catch (err) {
        console.error('Error deleting mission:', err);
        alert('Failed to delete mission: ' + (err.message || 'Unknown error'));
      }
    }
  };

  const handleOpenAssignModal = async (mission) => {
    setSelectedMission(mission);
    try {
      const agents = await apiClient.get('/api/ops-planner/agents/available');
      // Map _id to id for consistency
      const mappedAgents = agents.map(agent => ({
        ...agent,
        id: agent._id || agent.id
      }));
      // Filter out previously failed agent if exists
      const filteredAgents = mission.previous_assigned_agent_id 
        ? mappedAgents.filter(agent => agent.id !== mission.previous_assigned_agent_id)
        : mappedAgents;
      setAvailableAgents(filteredAgents);
      setShowAssignModal(true);
    } catch (err) {
      console.error('Error fetching agents:', err);
      alert('Failed to fetch available agents');
    }
  };

  const handleAssignAgent = async (agentId) => {
    try {
      await apiClient.post(`/api/ops-planner/missions/${selectedMission.id}/assign`, { agent_id: agentId });
      await fetchMissions();
      setShowAssignModal(false);
      setSelectedMission(null);
    } catch (err) {
      console.error('Error assigning mission:', err);
      alert('Failed to assign mission: ' + (err.message || 'Unknown error'));
    }
  };

  const handleOpenSubmitModal = (mission) => {
    setSelectedMission(mission);
    setSubmitForm({ status: 'completed', notes: '' });
    setShowSubmitModal(true);
  };

  const handleSubmitMission = async (e) => {
    e.preventDefault();
    try {
      await apiClient.patch(`/api/ops-planner/missions/${selectedMission.id}/status`, {
        status: submitForm.status,
        completion_notes: submitForm.notes
      });
      await fetchMissions();
      setShowSubmitModal(false);
      setSelectedMission(null);
    } catch (err) {
      console.error('Error submitting mission:', err);
      alert('Failed to submit mission: ' + (err.message || 'Unknown error'));
    }
  };

  const getMissionNumber = (missionId) => {
    // Get all missions sorted by creation date
    const sortedMissions = [...missions].sort((a, b) => 
      new Date(a.created_at) - new Date(b.created_at)
    );
    const index = sortedMissions.findIndex(m => m.id === missionId);
    return index >= 0 ? index + 1 : missions.length + 1;
  };

  const MissionCard = ({ mission, isAgent = false }) => {
    const getDifficultyColor = (difficulty) => {
      switch(difficulty?.toLowerCase()) {
        case 'insane': return { bg: 'rgba(255, 68, 68, 0.2)', color: '#ff4444' };
        case 'hard': return { bg: 'rgba(255, 200, 68, 0.2)', color: '#ffc844' };
        default: return { bg: 'rgba(68, 200, 68, 0.2)', color: '#44c844' };
      }
    };

    const difficultyStyle = getDifficultyColor(mission.difficulty);
    const missionNumber = getMissionNumber(mission.id);
    
    return (
      <Card variant="default" style={{ minWidth: '340px', backgroundColor: '#0a0a0f', border: '1px solid #1a1a2e', position: 'relative', display: 'flex', flexDirection: 'column', backdropFilter: 'blur(10px)', boxShadow: '0 8px 32px rgba(0, 0, 0, 0.5)' }}>
        <div style={{ padding: '0.875rem', display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          {/* Mission Number Badge */}
          <div style={{ position: 'absolute', top: '0.5rem', left: '0.5rem', padding: '0.2rem 0.5rem', backgroundColor: 'rgba(41, 163, 153, 0.2)', border: '1px solid #29a399', borderRadius: '0.2rem', fontSize: '0.65rem', fontWeight: '600', color: '#29a399' }}>
            #Mission {missionNumber}
          </div>
          
          {/* Title and Difficulty */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', gap: '0.75rem', paddingRight: '70px', paddingTop: '1.5rem' }}>
            <h4 style={{ margin: 0, color: '#29a399', fontSize: '0.95rem', fontWeight: '600', lineHeight: '1.3' }}>{mission.title}</h4>
            <span style={{ padding: '0.25rem 0.6rem', backgroundColor: difficultyStyle.bg, color: difficultyStyle.color, borderRadius: '0.2rem', fontSize: '0.65rem', fontWeight: '600', whiteSpace: 'nowrap' }}>
              {mission.difficulty?.toUpperCase() || 'SEARCH'}
            </span>
          </div>
          
          {/* Description */}
          <p style={{ margin: 0, color: 'rgba(255, 255, 255, 0.7)', fontSize: '0.8rem', lineHeight: '1.3' }}>
            {mission.description?.length > 100 ? mission.description.substring(0, 100) + '...' : mission.description}
          </p>
          
          {/* Tags */}
          {mission.tags && mission.tags.length > 0 && (
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.3rem' }}>
              {mission.tags.map((tag, index) => (
                <span key={index} style={{ padding: '0.15rem 0.5rem', backgroundColor: 'rgba(41, 163, 153, 0.15)', color: '#29a399', borderRadius: '0.2rem', fontSize: '0.65rem', border: '1px solid rgba(41, 163, 153, 0.3)' }}>
                  #{tag}
                </span>
              ))}
            </div>
          )}
          
          {/* Dates */}
          <div style={{ fontSize: '0.75rem', color: 'rgba(255, 255, 255, 0.5)' }}>
            {mission.due_date && (
              <p style={{ margin: '0.3rem 0', color: '#e59019' }}>
                <span style={{ color: 'rgba(255, 255, 255, 0.3)' }}>Due:</span> {new Date(mission.due_date).toLocaleDateString()} {new Date(mission.due_date).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </p>
            )}
            <p style={{ margin: '0.3rem 0', color: 'rgba(255, 255, 255, 0.5)' }}>
              <span style={{ color: 'rgba(255, 255, 255, 0.3)' }}>Created:</span> {new Date(mission.created_at).toLocaleDateString()}
            </p>
          </div>
          
          {/* Admin View - Pending Status Buttons */}
          {!isAgent && mission.status === 'pending' && (
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <button onClick={() => handleOpenAssignModal(mission)} style={{ flex: 1, padding: '0.5rem', backgroundColor: '#29a399', border: 'none', color: '#ffffff', borderRadius: '0.25rem', cursor: 'pointer', fontSize: '0.7rem', fontWeight: '600', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.3rem', transition: 'all 0.2s ease' }} onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#3ab8a8'} onMouseLeave={(e) => e.currentTarget.style.backgroundColor = '#29a399'}>
                <User size={12} /> ASSIGN AGENT
              </button>
              <button onClick={() => handleDeleteMission(mission.id)} style={{ flex: 0.6, padding: '0.5rem', backgroundColor: 'transparent', border: '1px solid #ff4444', color: '#ff4444', borderRadius: '0.25rem', cursor: 'pointer', fontSize: '0.7rem', fontWeight: '600', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.2rem', transition: 'all 0.2s ease' }} onMouseEnter={(e) => e.currentTarget.style.backgroundColor = 'rgba(255, 68, 68, 0.1)'} onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}>
                <Trash2 size={12} /> DELETE
              </button>
            </div>
          )}
          
          {/* Admin View - In Progress Status */}
          {!isAgent && mission.status === 'in_progress' && mission.assigned_agent_name && (
            <div style={{ padding: '0.5rem 0.75rem', backgroundColor: 'rgba(41, 163, 153, 0.1)', borderRadius: '0.25rem', color: '#29a399', fontSize: '0.75rem', fontWeight: '600', border: '1px solid rgba(41, 163, 153, 0.3)' }}>
              Assigned to: {mission.assigned_agent_name}
            </div>
          )}
          
          {/* Agent View - Submit Button */}
          {isAgent && mission.status === 'in_progress' && (
            <button onClick={() => handleOpenSubmitModal(mission)} style={{ width: '100%', padding: '0.5rem', backgroundColor: '#29a399', border: 'none', color: '#ffffff', borderRadius: '0.25rem', cursor: 'pointer', fontSize: '0.7rem', fontWeight: '600', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.3rem', transition: 'all 0.2s ease' }} onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#3ab8a8'} onMouseLeave={(e) => e.currentTarget.style.backgroundColor = '#29a399'}>
              SUBMIT MISSION
            </button>
          )}
        </div>
      </Card>
    );
  };

  const CompletedMissionCard = ({ mission, isFailed = false }) => {
    const [showDetails, setShowDetails] = useState(false);
    const missionNumber = getMissionNumber(mission.id);
    
    return (
      <div onMouseEnter={() => setShowDetails(true)} onMouseLeave={() => setShowDetails(false)} style={{ position: 'relative', padding: '1rem', backgroundColor: '#1a1f2e', border: `1px solid ${isFailed ? '#ff6b6b' : '#4caf50'}`, borderRadius: '0.375rem', cursor: 'pointer', minHeight: '60px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ flex: 1 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
            <span style={{ padding: '0.15rem 0.4rem', backgroundColor: 'rgba(41, 163, 153, 0.2)', border: '1px solid #29a399', borderRadius: '0.2rem', fontSize: '0.6rem', fontWeight: '600', color: '#29a399' }}>
              #M{missionNumber}
            </span>
            <h4 style={{ margin: 0, color: isFailed ? '#ff6b6b' : '#4caf50', fontSize: '0.95rem', fontWeight: '600' }}>{mission.title}</h4>
          </div>
          <p style={{ margin: '0.25rem 0 0 0', color: 'rgba(255, 255, 255, 0.5)', fontSize: '0.8rem' }}>
            {mission.completed_at ? new Date(mission.completed_at).toLocaleDateString() : 'N/A'}
          </p>
        </div>
        {showDetails && (
          <div style={{ position: 'absolute', bottom: '100%', left: 0, right: 0, backgroundColor: '#0f0f1e', border: '1px solid #29a399', borderRadius: '0.375rem', padding: '0.75rem', marginBottom: '0.5rem', zIndex: 10 }}>
            <p style={{ margin: '0 0 0.5rem 0', color: 'rgba(255, 255, 255, 0.7)', fontSize: '0.8rem' }}>{mission.description}</p>
            {mission.completion_notes && (
              <p style={{ margin: '0.25rem 0 0 0', color: 'rgba(255, 255, 255, 0.5)', fontSize: '0.75rem' }}>Notes: {mission.completion_notes}</p>
            )}
          </div>
        )}
      </div>
    );
  };

  // AGENT VIEW
  if (currentUser?.role === 'agent') {
    return (
      <DashboardLayout
        title="OPS PLANNER"
        subtitle="Mission Operations"
        navigation={<AgentNavigation />}
      >
        <div style={{ maxWidth: '1600px', margin: '0 auto', padding: '0 1rem 1rem 1rem', position: 'relative' }}>
        {loading ? (
          <div style={{ textAlign: 'center', padding: '2rem', color: 'rgba(255, 255, 255, 0.6)' }}>Loading missions...</div>
        ) : showCompletedView ? (
          <>
            <div style={{ opacity: 0.3, pointerEvents: 'none' }}>
              <h2 style={{ margin: '0 0 1rem 0', color: '#29a399', fontSize: '1.5rem', fontWeight: '400', letterSpacing: '1px' }}>ACTIVE MISSIONS</h2>
            </div>
            <div style={{ position: 'fixed', inset: 0, backgroundColor: 'rgba(0, 0, 0, 0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 50 }} onClick={() => setShowCompletedView(false)}>
              <Card variant="default" style={{ maxWidth: '600px', width: '90%', maxHeight: '80vh', overflowY: 'auto' }} onClick={(e) => e.stopPropagation()}>
                <div style={{ padding: '2rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                    <h2 style={{ margin: 0, color: '#4caf50', fontSize: '1.5rem', fontWeight: '400', letterSpacing: '1px' }}>COMPLETED ({completedMissions.length})</h2>
                    <button onClick={() => setShowCompletedView(false)} style={{ background: 'none', border: 'none', color: '#ffffff', cursor: 'pointer', fontSize: '1.5rem' }}><X size={24} /></button>
                  </div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                    {completedMissions.length > 0 ? completedMissions.map(mission => <CompletedMissionCard key={mission.id} mission={mission} />) : <div style={{ color: 'rgba(255, 255, 255, 0.5)', padding: '2rem', textAlign: 'center' }}>No completed missions</div>}
                  </div>
                </div>
              </Card>
            </div>
          </>
        ) : showFailedView ? (
          <>
            <div style={{ opacity: 0.3, pointerEvents: 'none' }}>
              <h2 style={{ margin: '0 0 1rem 0', color: '#29a399', fontSize: '1.5rem', fontWeight: '400', letterSpacing: '1px' }}>ACTIVE MISSIONS</h2>
            </div>
            <div style={{ position: 'fixed', inset: 0, backgroundColor: 'rgba(0, 0, 0, 0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 50 }} onClick={() => setShowFailedView(false)}>
              <Card variant="default" style={{ maxWidth: '600px', width: '90%', maxHeight: '80vh', overflowY: 'auto' }} onClick={(e) => e.stopPropagation()}>
                <div style={{ padding: '2rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                    <h2 style={{ margin: 0, color: '#ff6b6b', fontSize: '1.5rem', fontWeight: '400', letterSpacing: '1px' }}>FAILED ({failedMissions.length})</h2>
                    <button onClick={() => setShowFailedView(false)} style={{ background: 'none', border: 'none', color: '#ffffff', cursor: 'pointer', fontSize: '1.5rem' }}><X size={24} /></button>
                  </div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                    {failedMissions.length > 0 ? failedMissions.map(mission => <CompletedMissionCard key={mission.id} mission={mission} isFailed />) : <div style={{ color: 'rgba(255, 255, 255, 0.5)', padding: '2rem', textAlign: 'center' }}>No failed missions</div>}
                  </div>
                </div>
              </Card>
            </div>
          </>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                <h2 style={{ margin: 0, color: '#29a399', fontSize: '1.5rem', fontWeight: '400', letterSpacing: '1px' }}>ACTIVE MISSIONS ({inProgressMissions.length})</h2>
                <div style={{ display: 'flex', gap: '0.75rem' }}>
                  <button onClick={() => setShowCompletedView(true)} style={{ padding: '0.75rem 1.5rem', backgroundColor: 'transparent', border: '1px solid #4caf50', color: '#ffffff', borderRadius: '0.5rem', cursor: 'pointer', fontSize: '0.9rem', fontWeight: '400', transition: 'all 0.2s ease' }} onMouseEnter={(e) => e.currentTarget.style.backgroundColor = 'rgba(76, 175, 80, 0.1)'} onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}>
                    View Completed
                  </button>
                  <button onClick={() => setShowFailedView(true)} style={{ padding: '0.75rem 1.5rem', backgroundColor: 'transparent', border: '1px solid #ff6b6b', color: '#ffffff', borderRadius: '0.5rem', cursor: 'pointer', fontSize: '0.9rem', fontWeight: '400', transition: 'all 0.2s ease' }} onMouseEnter={(e) => e.currentTarget.style.backgroundColor = 'rgba(255, 107, 107, 0.1)'} onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}>
                    View Failed
                  </button>
                </div>
              </div>
              <div style={{ display: 'flex', gap: '0.875rem', overflowX: 'auto', overflowY: 'hidden', paddingBottom: '0.5rem' }}>
                {inProgressMissions.length > 0 ? (
                  inProgressMissions.map(mission => <MissionCard key={mission.id} mission={mission} isAgent={true} />)
                ) : (
                  <div style={{ color: 'rgba(255, 255, 255, 0.5)', padding: '1.5rem', fontSize: '0.85rem' }}>No active missions assigned to you</div>
                )}
              </div>
            </div>
          </div>
        )}
        
        {/* Agent Submit Mission Modal */}
        {showSubmitModal && selectedMission && (
          <div style={{ position: 'fixed', inset: 0, backgroundColor: 'rgba(0, 0, 0, 0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 40 }} onClick={() => { setShowSubmitModal(false); setSelectedMission(null); }}>
            <Card variant="default" style={{ maxWidth: '500px', width: '90%' }} onClick={(e) => e.stopPropagation()}>
              <div style={{ padding: '1.5rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                  <h3 style={{ fontSize: '1.25rem', fontWeight: '600', margin: 0, color: '#ffffff' }}>Submit Mission</h3>
                  <button onClick={() => { setShowSubmitModal(false); setSelectedMission(null); }} style={{ background: 'none', border: 'none', color: '#ffffff', cursor: 'pointer', fontSize: '1.5rem' }}>
                    <X size={24} />
                  </button>
                </div>
                <form onSubmit={handleSubmitMission} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                  <div>
                    <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: '400', color: 'rgba(255, 255, 255, 0.65)', marginBottom: '0.5rem' }}>
                      Mission Status <span style={{ color: '#e59019' }}>*</span>
                    </label>
                    <select value={submitForm.status} onChange={(e) => setSubmitForm({ ...submitForm, status: e.target.value })} required style={{ width: '100%', padding: '0.75rem', backgroundColor: '#1a1f2e', border: '1px solid #3a4050', borderRadius: '0.375rem', color: '#ffffff', fontSize: '0.9rem', boxSizing: 'border-box', cursor: 'pointer' }}>
                      <option value="completed">✓ Completed</option>
                      <option value="failed">✗ Failed</option>
                    </select>
                  </div>
                  <div>
                    <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: '400', color: 'rgba(255, 255, 255, 0.65)', marginBottom: '0.5rem' }}>
                      Notes (Optional)
                    </label>
                    <textarea value={submitForm.notes} onChange={(e) => setSubmitForm({ ...submitForm, notes: e.target.value })} placeholder="Add any additional notes..." style={{ width: '100%', padding: '0.75rem', backgroundColor: '#1a1f2e', border: '1px solid #3a4050', borderRadius: '0.375rem', color: '#ffffff', fontSize: '0.9rem', minHeight: '100px', fontFamily: 'inherit', boxSizing: 'border-box' }} />
                  </div>
                  <div style={{ display: 'flex', gap: '1rem' }}>
                    <button type="submit" style={{ flex: 1, padding: '0.75rem', backgroundColor: '#29a399', border: 'none', color: '#ffffff', borderRadius: '0.375rem', cursor: 'pointer', fontWeight: '500', transition: 'all 0.2s ease' }} onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#3ab8a8'} onMouseLeave={(e) => e.currentTarget.style.backgroundColor = '#29a399'}>
                      SUBMIT
                    </button>
                    <button type="button" onClick={() => { setShowSubmitModal(false); setSelectedMission(null); }} style={{ flex: 1, padding: '0.75rem', backgroundColor: 'transparent', border: '1px solid #3a4050', color: '#ffffff', borderRadius: '0.375rem', cursor: 'pointer', fontWeight: '500', transition: 'all 0.2s ease' }} onMouseEnter={(e) => e.currentTarget.style.borderColor = '#29a399'} onMouseLeave={(e) => e.currentTarget.style.borderColor = '#3a4050'}>
                      CANCEL
                    </button>
                  </div>
                </form>
              </div>
            </Card>
          </div>
        )}
        </div>
      </DashboardLayout>
    );
  }

  // ADMIN VIEW
  return (
    <div style={{ maxWidth: '1600px', margin: '0 auto', padding: '0 1rem 1rem 1rem', position: 'relative' }}>
      {/* Create Mission Button */}
      <button onClick={() => setShowCreateModal(true)} style={{ position: 'fixed', bottom: '2rem', right: '2rem', padding: '1rem 1.75rem', backgroundColor: '#29a399', border: 'none', color: '#ffffff', borderRadius: '0.5rem', cursor: 'pointer', fontSize: '0.9rem', fontWeight: '600', transition: 'all 0.2s ease', zIndex: 30, boxShadow: '0 4px 12px rgba(41, 163, 153, 0.3)' }} onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#3ab8a8'} onMouseLeave={(e) => e.currentTarget.style.backgroundColor = '#29a399'}>
        + CREATE MISSION
      </button>
      
      {loading ? (
        <div style={{ textAlign: 'center', padding: '2rem', color: 'rgba(255, 255, 255, 0.6)' }}>Loading missions...</div>
      ) : showCompletedView ? (
        <>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', opacity: 0.3, pointerEvents: 'none' }}>
            <div><h2 style={{ margin: 0, color: '#29a399', fontSize: '1.5rem', fontWeight: '400', letterSpacing: '1px' }}>OPEN MISSIONS</h2></div>
          </div>
          <div style={{ position: 'fixed', inset: 0, backgroundColor: 'rgba(0, 0, 0, 0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 50 }} onClick={() => setShowCompletedView(false)}>
            <Card variant="default" style={{ maxWidth: '600px', width: '90%', maxHeight: '80vh', overflowY: 'auto' }} onClick={(e) => e.stopPropagation()}>
              <div style={{ padding: '2rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                  <h2 style={{ margin: 0, color: '#4caf50', fontSize: '1.5rem', fontWeight: '400', letterSpacing: '1px' }}>COMPLETED ({completedMissions.length})</h2>
                  <button onClick={() => setShowCompletedView(false)} style={{ background: 'none', border: 'none', color: '#ffffff', cursor: 'pointer', fontSize: '1.5rem' }}><X size={24} /></button>
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                  {completedMissions.length > 0 ? completedMissions.map(mission => <CompletedMissionCard key={mission.id} mission={mission} />) : <div style={{ color: 'rgba(255, 255, 255, 0.5)', padding: '2rem', textAlign: 'center' }}>No completed missions</div>}
                </div>
              </div>
            </Card>
          </div>
        </>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          {/* OPEN MISSIONS Section */}
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
              <h2 style={{ margin: 0, color: '#29a399', fontSize: '1.5rem', fontWeight: '400', letterSpacing: '1px' }}>
                OPEN MISSIONS ({openMissions.length})
              </h2>
              <button onClick={() => setShowCompletedView(true)} style={{ padding: '0.75rem 1.5rem', backgroundColor: 'transparent', border: '1px solid #4caf50', color: '#ffffff', borderRadius: '0.5rem', cursor: 'pointer', fontSize: '0.9rem', fontWeight: '400', transition: 'all 0.2s ease' }} onMouseEnter={(e) => e.currentTarget.style.backgroundColor = 'rgba(76, 175, 80, 0.1)'} onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}>
                View Completed
              </button>
            </div>
            <div style={{ display: 'flex', gap: '0.875rem', overflowX: 'auto', overflowY: 'hidden', paddingBottom: '0.5rem' }}>
              {openMissions.length > 0 ? (
                openMissions.map(mission => <MissionCard key={mission.id} mission={mission} isAgent={false} />)
              ) : (
                <div style={{ color: 'rgba(255, 255, 255, 0.5)', padding: '1.5rem', fontSize: '0.85rem' }}>No open missions</div>
              )}
            </div>
          </div>
          
          {/* IN PROGRESS Section */}
          <div>
            <h2 style={{ margin: '0 0 1rem 0', color: '#29a399', fontSize: '1.5rem', fontWeight: '400', letterSpacing: '1px' }}>
              IN PROGRESS ({inProgressMissions.length})
            </h2>
            <div style={{ display: 'flex', gap: '0.875rem', overflowX: 'auto', overflowY: 'hidden', paddingBottom: '0.5rem' }}>
              {inProgressMissions.length > 0 ? (
                inProgressMissions.map(mission => <MissionCard key={mission.id} mission={mission} isAgent={false} />)
              ) : (
                <div style={{ color: 'rgba(255, 255, 255, 0.5)', padding: '1.5rem', fontSize: '0.85rem' }}>No missions in progress</div>
              )}
            </div>
          </div>
        </div>
      )}
      
      {/* Assign Agent Modal */}
      {showAssignModal && selectedMission && (
        <div style={{ position: 'fixed', inset: 0, backgroundColor: 'rgba(0, 0, 0, 0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 40 }} onClick={() => { setShowAssignModal(false); setSelectedMission(null); }}>
          <Card variant="default" style={{ maxWidth: '500px', width: '90%' }} onClick={(e) => e.stopPropagation()}>
            <div style={{ padding: '1.5rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                <h3 style={{ fontSize: '1.25rem', fontWeight: '600', margin: 0, color: '#ffffff' }}>Assign Agent to Mission</h3>
                <button onClick={() => { setShowAssignModal(false); setSelectedMission(null); }} style={{ background: 'none', border: 'none', color: '#ffffff', cursor: 'pointer', fontSize: '1.5rem' }}>
                  <X size={24} />
                </button>
              </div>
              <p style={{ color: 'rgba(255, 255, 255, 0.6)', fontSize: '0.85rem', marginBottom: '1rem' }}>
                Agents sorted by score (highest first) • Only FREE agents shown
              </p>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', maxHeight: '400px', overflowY: 'auto' }}>
                {availableAgents.length > 0 ? (
                  availableAgents.map(agent => (
                    <button key={agent.id} onClick={() => handleAssignAgent(agent.id)} style={{ padding: '1rem', backgroundColor: '#1a1f2e', border: '1px solid #3a4050', color: '#ffffff', borderRadius: '0.375rem', cursor: 'pointer', fontSize: '0.9rem', textAlign: 'left', transition: 'all 0.2s ease', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }} onMouseEnter={(e) => { e.currentTarget.style.backgroundColor = '#29a399'; e.currentTarget.style.borderColor = '#29a399'; }} onMouseLeave={(e) => { e.currentTarget.style.backgroundColor = '#1a1f2e'; e.currentTarget.style.borderColor = '#3a4050'; }}>
                      <div>
                        <div style={{ fontWeight: '600', marginBottom: '0.25rem' }}>{agent.full_name}</div>
                        <div style={{ fontSize: '0.75rem', color: 'rgba(255, 255, 255, 0.5)' }}>{agent.email}</div>
                        <div style={{ fontSize: '0.7rem', color: 'rgba(255, 255, 255, 0.4)', marginTop: '0.25rem' }}>
                          Completed: {agent.completed_missions} • Failed: {agent.failed_missions}
                        </div>
                      </div>
                      <div style={{ padding: '0.25rem 0.75rem', backgroundColor: 'rgba(41, 163, 153, 0.2)', border: '1px solid #29a399', borderRadius: '0.25rem', fontSize: '0.85rem', fontWeight: '600', color: '#29a399' }}>
                        Score: {agent.score}
                      </div>
                    </button>
                  ))
                ) : (
                  <div style={{ color: 'rgba(255, 255, 255, 0.5)', padding: '2rem', textAlign: 'center' }}>
                    No available agents. All agents are currently busy or unavailable.
                  </div>
                )}
              </div>
            </div>
          </Card>
        </div>
      )}
      
      {/* Create Mission Modal */}
      {showCreateModal && (
        <div style={{ position: 'fixed', inset: 0, backgroundColor: 'rgba(0, 0, 0, 0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 40 }} onClick={() => setShowCreateModal(false)}>
          <Card variant="default" style={{ maxWidth: '500px', width: '90%' }} onClick={(e) => e.stopPropagation()}>
            <div style={{ padding: '1.5rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                <h3 style={{ fontSize: '1.25rem', fontWeight: '600', margin: 0, color: '#ffffff' }}>Create New Mission</h3>
                <button onClick={() => setShowCreateModal(false)} style={{ background: 'none', border: 'none', color: '#ffffff', cursor: 'pointer', fontSize: '1.5rem' }}>
                  <X size={24} />
                </button>
              </div>
              <form onSubmit={handleCreateMission} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: '400', color: 'rgba(255, 255, 255, 0.65)', marginBottom: '0.5rem' }}>
                    Mission Title <span style={{ color: '#e59019' }}>*</span>
                  </label>
                  <input type="text" value={createForm.title} onChange={(e) => setCreateForm({ ...createForm, title: e.target.value })} required placeholder="e.g., Secure Facility Alpha" style={{ width: '100%', padding: '0.75rem', backgroundColor: '#1a1f2e', border: '1px solid #3a4050', borderRadius: '0.375rem', color: '#ffffff', fontSize: '0.9rem', boxSizing: 'border-box' }} />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: '400', color: 'rgba(255, 255, 255, 0.65)', marginBottom: '0.5rem' }}>
                    Description <span style={{ color: '#e59019' }}>*</span>
                  </label>
                  <textarea value={createForm.description} onChange={(e) => setCreateForm({ ...createForm, description: e.target.value })} required placeholder="Complete security sweep of Facility Alpha" style={{ width: '100%', padding: '0.75rem', backgroundColor: '#1a1f2e', border: '1px solid #3a4050', borderRadius: '0.375rem', color: '#ffffff', fontSize: '0.9rem', minHeight: '100px', fontFamily: 'inherit', boxSizing: 'border-box' }} />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: '400', color: 'rgba(255, 255, 255, 0.65)', marginBottom: '0.5rem' }}>
                    Difficulty <span style={{ color: '#e59019' }}>*</span>
                  </label>
                  <select value={createForm.difficulty} onChange={(e) => setCreateForm({ ...createForm, difficulty: e.target.value })} required style={{ width: '100%', padding: '0.75rem', backgroundColor: '#1a1f2e', border: '1px solid #3a4050', borderRadius: '0.375rem', color: '#ffffff', fontSize: '0.9rem', boxSizing: 'border-box', cursor: 'pointer' }}>
                    <option value="search">Search</option>
                    <option value="hard">Hard</option>
                    <option value="insane">Insane</option>
                  </select>
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: '400', color: 'rgba(255, 255, 255, 0.65)', marginBottom: '0.5rem' }}>
                    Due Date <span style={{ color: '#e59019' }}>*</span>
                  </label>
                  <input type="datetime-local" value={createForm.due_date} onChange={(e) => setCreateForm({ ...createForm, due_date: e.target.value })} required min={new Date().toISOString().slice(0, 16)} style={{ width: '100%', padding: '0.75rem', backgroundColor: '#1a1f2e', border: '1px solid #3a4050', borderRadius: '0.375rem', color: '#ffffff', fontSize: '0.9rem', boxSizing: 'border-box', cursor: 'pointer' }} />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: '400', color: 'rgba(255, 255, 255, 0.65)', marginBottom: '0.5rem' }}>
                    Tags <span style={{ fontSize: '0.75rem', color: 'rgba(255, 255, 255, 0.45)' }}>(comma-separated)</span>
                  </label>
                  <input type="text" value={createForm.tags} onChange={(e) => setCreateForm({ ...createForm, tags: e.target.value })} placeholder="security, facility, urgent" style={{ width: '100%', padding: '0.75rem', backgroundColor: '#1a1f2e', border: '1px solid #3a4050', borderRadius: '0.375rem', color: '#ffffff', fontSize: '0.9rem', boxSizing: 'border-box' }} />
                </div>
                <div style={{ display: 'flex', gap: '1rem' }}>
                  <button type="submit" style={{ flex: 1, padding: '0.75rem', backgroundColor: '#29a399', border: 'none', color: '#ffffff', borderRadius: '0.375rem', cursor: 'pointer', fontWeight: '500', transition: 'all 0.2s ease' }} onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#3ab8a8'} onMouseLeave={(e) => e.currentTarget.style.backgroundColor = '#29a399'}>
                    CREATE
                  </button>
                  <button type="button" onClick={() => setShowCreateModal(false)} style={{ flex: 1, padding: '0.75rem', backgroundColor: 'transparent', border: '1px solid #3a4050', color: '#ffffff', borderRadius: '0.375rem', cursor: 'pointer', fontWeight: '500', transition: 'all 0.2s ease' }} onMouseEnter={(e) => e.currentTarget.style.borderColor = '#29a399'} onMouseLeave={(e) => e.currentTarget.style.borderColor = '#3a4050'}>
                    CANCEL
                  </button>
                </div>
              </form>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
}
