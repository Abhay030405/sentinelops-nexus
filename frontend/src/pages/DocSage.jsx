import { useState, useEffect } from 'react';
import { Upload, Download, MessageSquare, Trash2, X, FileText, Send } from 'lucide-react';
import DashboardLayout from '../components/DashboardLayout';
import AdminNavigation from '../components/AdminNavigation';
import AgentNavigation from '../components/AgentNavigation';
import { Card } from '../components/ui/Card';
import { useAuth } from '../hooks/useAuth';
import apiClient from '../services/api';

export default function DocSage() {
  const { user } = useAuth();
  const isAdmin = user?.role === 'admin';
  const [documents, setDocuments] = useState([]);
  const [missions, setMissions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showUploadForm, setShowUploadForm] = useState(false);
  const [selectedMission, setSelectedMission] = useState('');
  const [uploadFile, setUploadFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [loadingMissions, setLoadingMissions] = useState(false);
  const [chatDocument, setChatDocument] = useState(null);
  const [chatMessages, setChatMessages] = useState([]);
  const [chatInput, setChatInput] = useState('');
  const [sendingMessage, setSendingMessage] = useState(false);

  useEffect(() => {
    fetchDocuments();
    if (isAdmin) {
      fetchMissions();
    } else {
      fetchAgentMissions();
    }
  }, [user]);

  const fetchDocuments = async () => {
    try {
      setLoading(true);
      const response = await apiClient.get('/api/docsage/documents', {
        params: { user_email: user?.email }
      });
      setDocuments(response);
    } catch (error) {
      console.error('Error fetching documents:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchMissions = async () => {
    try {
      setLoadingMissions(true);
      const response = await apiClient.get('/api/ops-planner/missions');
      console.log('Missions fetched:', response);
      setMissions(response.missions || response || []);
    } catch (error) {
      console.error('Error fetching missions:', error);
      setMissions([]);
    } finally {
      setLoadingMissions(false);
    }
  };

  const fetchAgentMissions = async () => {
    try {
      setLoadingMissions(true);
      // Fetch missions where agent is assigned (current or completed)
      const response = await apiClient.get('/api/ops-planner/missions', {
        params: { assigned_agent_id: user?.id }
      });
      console.log('Agent missions fetched:', response);
      setMissions(response.missions || response || []);
    } catch (error) {
      console.error('Error fetching agent missions:', error);
      setMissions([]);
    } finally {
      setLoadingMissions(false);
    }
  };

  const handleFileChange = (e) => {
    setUploadFile(e.target.files[0]);
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!uploadFile) return;

    try {
      setUploading(true);
      const formData = new FormData();
      formData.append('file', uploadFile);
      formData.append('uploaded_by', user?.email);
      if (selectedMission) {
        formData.append('mission_id', selectedMission);
      }

      await apiClient.post('/api/docsage/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      setShowUploadForm(false);
      setUploadFile(null);
      setSelectedMission('');
      fetchDocuments();
    } catch (error) {
      console.error('Error uploading document:', error);
      alert('Error uploading document: ' + (error.response?.data?.detail || error.message));
    } finally {
      setUploading(false);
    }
  };

  const handleDownload = async (doc) => {
    try {
      const response = await apiClient.get(`/api/docsage/documents/${doc.id}/download`, {
        responseType: 'blob'
      });
      const url = window.URL.createObjectURL(new Blob([response]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', doc.name);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error('Error downloading document:', error);
      alert('Error downloading document');
    }
  };

  const handleDelete = async (docId) => {
    if (!confirm('Are you sure you want to delete this document?')) return;

    try {
      await apiClient.delete(`/api/docsage/documents/${docId}`);
      fetchDocuments();
    } catch (error) {
      console.error('Error deleting document:', error);
      alert('Error deleting document');
    }
  };

  const openChat = async (doc) => {
    setChatDocument(doc);
    try {
      const history = await apiClient.get(
        `/api/docsage/chat/history/${doc.id}?user_email=${encodeURIComponent(user?.email)}`
      );
      setChatMessages(history.messages || []);
    } catch (error) {
      console.error('Error loading chat history:', error);
      setChatMessages([]);
    }
  };

  const closeChat = () => {
    setChatDocument(null);
    setChatMessages([]);
    setChatInput('');
  };

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!chatInput.trim() || !chatDocument) return;

    const userMessage = { role: 'user', content: chatInput, timestamp: new Date() };
    setChatMessages(prev => [...prev, userMessage]);
    setChatInput('');
    setSendingMessage(true);

    try {
      const response = await apiClient.post(
        `/api/docsage/chat?user_email=${encodeURIComponent(user?.email)}`,
        {
          document_id: chatDocument.id,
          question: userMessage.content,
          include_history: true
        }
      );

      const aiMessage = {
        role: 'assistant',
        content: response.answer,
        timestamp: new Date(response.timestamp)
      };
      setChatMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = {
        role: 'assistant',
        content: 'Sorry, I encountered an error processing your question.',
        timestamp: new Date()
      };
      setChatMessages(prev => [...prev, errorMessage]);
    } finally {
      setSendingMessage(false);
    }
  };

  const getMissionName = (missionId) => {
    const mission = missions.find(m => m._id === missionId);
    return mission ? mission.title : 'Unknown Mission';
  };

  return (
    <DashboardLayout
      title="DOCSAGE"
      subtitle="Document Intelligence & Analysis"
      navigation={isAdmin ? <AdminNavigation /> : <AgentNavigation />}
    >
      {/* Upload Button (Admin Only) */}
      {isAdmin && (
        <div style={{ marginBottom: '1.5rem', display: 'flex', justifyContent: 'flex-end' }}>
          <button
            onClick={() => {
              setShowUploadForm(true);
              if (missions.length === 0) {
                fetchMissions();
              }
            }}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              padding: '0.75rem 1.5rem',
              backgroundColor: '#29a399',
              color: '#ffffff',
              border: 'none',
              borderRadius: '0.5rem',
              cursor: 'pointer',
              fontFamily: "'JetBrains Mono', monospace",
              fontSize: '0.875rem',
              fontWeight: '600',
              transition: 'all 0.3s'
            }}
            onMouseEnter={(e) => e.target.style.backgroundColor = '#238d85'}
            onMouseLeave={(e) => e.target.style.backgroundColor = '#29a399'}
          >
            <Upload size={18} />
            Upload Document
          </button>
        </div>
      )}

      {/* Upload Form Modal */}
      {showUploadForm && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0, 0, 0, 0.8)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000
        }}>
          <Card variant="glass" style={{ maxWidth: '500px', width: '90%', padding: '2rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
              <h3 style={{ color: '#ffffff', fontFamily: "'JetBrains Mono', monospace", margin: 0 }}>
                Upload Document
              </h3>
              <button
                onClick={() => setShowUploadForm(false)}
                style={{
                  background: 'none',
                  border: 'none',
                  color: 'rgba(255, 255, 255, 0.6)',
                  cursor: 'pointer',
                  padding: '0.25rem'
                }}
              >
                <X size={24} />
              </button>
            </div>

            <form onSubmit={handleUpload}>
              <div style={{ marginBottom: '1.5rem' }}>
                <label style={{
                  display: 'block',
                  color: 'rgba(255, 255, 255, 0.8)',
                  fontFamily: "'JetBrains Mono', monospace",
                  fontSize: '0.875rem',
                  marginBottom: '0.5rem'
                }}>
                  Select Mission
                </label>
                <select
                  value={selectedMission}
                  onChange={(e) => setSelectedMission(e.target.value)}
                  disabled={loadingMissions}
                  style={{
                    width: '100%',
                    padding: '0.75rem',
                    backgroundColor: '#1a1d24',
                    border: '1px solid rgba(255, 255, 255, 0.2)',
                    borderRadius: '0.375rem',
                    color: '#ffffff',
                    fontFamily: "'JetBrains Mono', monospace",
                    fontSize: '0.875rem',
                    opacity: loadingMissions ? 0.6 : 1,
                    cursor: loadingMissions ? 'not-allowed' : 'pointer',
                    outline: 'none'
                  }}
                >
                  <option value="" style={{ backgroundColor: '#1a1d24', color: '#ffffff' }}>
                    {loadingMissions ? 'Loading missions...' : 'Select Mission (Optional)'}
                  </option>
                  {missions && missions.length > 0 ? (
                    missions.map(mission => (
                      <option 
                        key={mission._id || mission.id} 
                        value={mission._id || mission.id}
                        style={{ backgroundColor: '#1a1d24', color: '#ffffff' }}
                      >
                        {mission.title} ({mission.status})
                      </option>
                    ))
                  ) : !loadingMissions ? (
                    <option value="" disabled style={{ backgroundColor: '#1a1d24', color: '#ffffff' }}>
                      No missions available
                    </option>
                  ) : null}
                </select>
              </div>

              <div style={{ marginBottom: '1.5rem' }}>
                <label style={{
                  display: 'block',
                  color: 'rgba(255, 255, 255, 0.8)',
                  fontFamily: "'JetBrains Mono', monospace",
                  fontSize: '0.875rem',
                  marginBottom: '0.5rem'
                }}>
                  Upload Document
                </label>
                <input
                  type="file"
                  onChange={handleFileChange}
                  required
                  style={{
                    width: '100%',
                    padding: '0.75rem',
                    backgroundColor: 'rgba(255, 255, 255, 0.05)',
                    border: '1px solid rgba(255, 255, 255, 0.1)',
                    borderRadius: '0.375rem',
                    color: '#ffffff',
                    fontFamily: "'JetBrains Mono', monospace",
                    fontSize: '0.875rem'
                  }}
                />
              </div>

              <div style={{ display: 'flex', gap: '1rem', justifyContent: 'flex-end' }}>
                <button
                  type="button"
                  onClick={() => setShowUploadForm(false)}
                  style={{
                    padding: '0.75rem 1.5rem',
                    backgroundColor: 'rgba(255, 255, 255, 0.1)',
                    color: '#ffffff',
                    border: 'none',
                    borderRadius: '0.375rem',
                    cursor: 'pointer',
                    fontFamily: "'JetBrains Mono', monospace",
                    fontSize: '0.875rem'
                  }}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={uploading}
                  style={{
                    padding: '0.75rem 1.5rem',
                    backgroundColor: '#29a399',
                    color: '#ffffff',
                    border: 'none',
                    borderRadius: '0.375rem',
                    cursor: uploading ? 'not-allowed' : 'pointer',
                    fontFamily: "'JetBrains Mono', monospace",
                    fontSize: '0.875rem',
                    opacity: uploading ? 0.6 : 1
                  }}
                >
                  {uploading ? 'Uploading...' : 'Upload'}
                </button>
              </div>
            </form>
          </Card>
        </div>
      )}

      {/* Chat Modal */}
      {chatDocument && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0, 0, 0, 0.8)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000,
          padding: '1rem'
        }}>
          <Card variant="glass" style={{
            maxWidth: '800px',
            width: '90%',
            height: '80vh',
            display: 'flex',
            flexDirection: 'column',
            padding: 0
          }}>
            {/* Chat Header */}
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              padding: '1.5rem',
              borderBottom: '1px solid rgba(255, 255, 255, 0.1)'
            }}>
              <div>
                <h3 style={{ color: '#ffffff', fontFamily: "'JetBrains Mono', monospace", margin: 0, marginBottom: '0.25rem' }}>
                  Chat with AI
                </h3>
                <p style={{ color: 'rgba(255, 255, 255, 0.6)', fontSize: '0.875rem', margin: 0 }}>
                  {chatDocument.name}
                </p>
              </div>
              <button
                onClick={closeChat}
                style={{
                  background: 'none',
                  border: 'none',
                  color: 'rgba(255, 255, 255, 0.6)',
                  cursor: 'pointer',
                  padding: '0.25rem'
                }}
              >
                <X size={24} />
              </button>
            </div>

            {/* Chat Messages */}
            <div style={{
              flex: 1,
              overflowY: 'auto',
              padding: '1.5rem',
              display: 'flex',
              flexDirection: 'column',
              gap: '1rem'
            }}>
              {chatMessages.length === 0 && (
                <div style={{ textAlign: 'center', color: 'rgba(255, 255, 255, 0.4)', padding: '2rem' }}>
                  Ask a question about this document
                </div>
              )}
              {chatMessages.map((msg, idx) => (
                <div
                  key={idx}
                  style={{
                    alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
                    maxWidth: '70%',
                    padding: '0.75rem 1rem',
                    backgroundColor: msg.role === 'user'
                      ? 'rgba(41, 163, 153, 0.2)'
                      : 'rgba(255, 255, 255, 0.05)',
                    borderRadius: '0.5rem',
                    border: '1px solid rgba(255, 255, 255, 0.1)'
                  }}
                >
                  <p style={{
                    margin: 0,
                    color: '#ffffff',
                    fontFamily: "'Inter', sans-serif",
                    fontSize: '0.875rem',
                    lineHeight: '1.5'
                  }}>
                    {msg.content}
                  </p>
                </div>
              ))}
              {sendingMessage && (
                <div style={{
                  alignSelf: 'flex-start',
                  maxWidth: '70%',
                  padding: '0.75rem 1rem',
                  backgroundColor: 'rgba(255, 255, 255, 0.05)',
                  borderRadius: '0.5rem',
                  border: '1px solid rgba(255, 255, 255, 0.1)'
                }}>
                  <p style={{ margin: 0, color: 'rgba(255, 255, 255, 0.6)', fontSize: '0.875rem' }}>
                    Thinking...
                  </p>
                </div>
              )}
            </div>

            {/* Chat Input */}
            <form onSubmit={sendMessage} style={{
              padding: '1.5rem',
              borderTop: '1px solid rgba(255, 255, 255, 0.1)',
              display: 'flex',
              gap: '1rem'
            }}>
              <input
                type="text"
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                placeholder="Ask a question..."
                style={{
                  flex: 1,
                  padding: '0.75rem',
                  backgroundColor: 'rgba(255, 255, 255, 0.05)',
                  border: '1px solid rgba(255, 255, 255, 0.1)',
                  borderRadius: '0.375rem',
                  color: '#ffffff',
                  fontFamily: "'Inter', sans-serif",
                  fontSize: '0.875rem'
                }}
              />
              <button
                type="submit"
                disabled={sendingMessage || !chatInput.trim()}
                style={{
                  padding: '0.75rem 1.5rem',
                  backgroundColor: '#29a399',
                  color: '#ffffff',
                  border: 'none',
                  borderRadius: '0.375rem',
                  cursor: sendingMessage ? 'not-allowed' : 'pointer',
                  fontFamily: "'JetBrains Mono', monospace",
                  fontSize: '0.875rem',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                  opacity: (sendingMessage || !chatInput.trim()) ? 0.6 : 1
                }}
              >
                <Send size={18} />
                Send
              </button>
            </form>
          </Card>
        </div>
      )}

      {/* Documents Grid */}
      {loading ? (
        <div style={{ textAlign: 'center', padding: '2rem', color: 'rgba(255, 255, 255, 0.6)' }}>
          Loading documents...
        </div>
      ) : documents.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '2rem', color: 'rgba(255, 255, 255, 0.6)' }}>
          No documents found
        </div>
      ) : (
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
          gap: '1.5rem'
        }}>
          {documents.map((doc) => (
            <Card key={doc.id} variant="glass">
              <div style={{ padding: '1.5rem' }}>
                {/* Card Header */}
                <div style={{ display: 'flex', alignItems: 'flex-start', gap: '1rem', marginBottom: '1rem' }}>
                  <div style={{
                    padding: '0.75rem',
                    backgroundColor: 'rgba(41, 163, 153, 0.2)',
                    borderRadius: '0.5rem',
                    border: '1px solid rgba(41, 163, 153, 0.3)'
                  }}>
                    <FileText size={24} color="#29a399" />
                  </div>
                  <div style={{ flex: 1 }}>
                    <h4 style={{
                      color: '#ffffff',
                      fontFamily: "'JetBrains Mono', monospace",
                      fontSize: '0.875rem',
                      fontWeight: '600',
                      margin: 0,
                      marginBottom: '0.25rem',
                      wordBreak: 'break-word'
                    }}>
                      {doc.name}
                    </h4>
                    {doc.mission_id && (
                      <p style={{
                        color: 'rgba(255, 255, 255, 0.6)',
                        fontSize: '0.75rem',
                        margin: 0,
                        fontFamily: "'Inter', sans-serif"
                      }}>
                        {getMissionName(doc.mission_id)}
                      </p>
                    )}
                  </div>
                </div>

                {/* Download Button */}
                <div style={{ marginBottom: '1rem' }}>
                  <button
                    onClick={() => handleDownload(doc)}
                    style={{
                      width: '100%',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      gap: '0.5rem',
                      padding: '0.75rem',
                      backgroundColor: 'rgba(255, 255, 255, 0.1)',
                      color: '#ffffff',
                      border: '1px solid rgba(255, 255, 255, 0.2)',
                      borderRadius: '0.375rem',
                      cursor: 'pointer',
                      fontFamily: "'JetBrains Mono', monospace",
                      fontSize: '0.875rem',
                      fontWeight: '500',
                      transition: 'all 0.3s'
                    }}
                    onMouseEnter={(e) => e.target.style.backgroundColor = 'rgba(255, 255, 255, 0.15)'}
                    onMouseLeave={(e) => e.target.style.backgroundColor = 'rgba(255, 255, 255, 0.1)'}
                  >
                    <Download size={16} />
                    Download
                  </button>
                </div>

                {/* Action Buttons */}
                <div style={{ display: 'flex', gap: '0.75rem' }}>
                  <button
                    onClick={() => openChat(doc)}
                    style={{
                      flex: 1,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      gap: '0.5rem',
                      padding: '0.75rem',
                      backgroundColor: '#29a399',
                      color: '#ffffff',
                      border: 'none',
                      borderRadius: '0.375rem',
                      cursor: 'pointer',
                      fontFamily: "'JetBrains Mono', monospace",
                      fontSize: '0.875rem',
                      fontWeight: '500',
                      transition: 'all 0.3s'
                    }}
                    onMouseEnter={(e) => e.target.style.backgroundColor = '#238d85'}
                    onMouseLeave={(e) => e.target.style.backgroundColor = '#29a399'}
                  >
                    <MessageSquare size={16} />
                    Chat with AI
                  </button>

                  {isAdmin && (
                    <button
                      onClick={() => handleDelete(doc.id)}
                      style={{
                        padding: '0.75rem',
                        backgroundColor: 'rgba(255, 68, 68, 0.2)',
                        color: '#ff4444',
                        border: '1px solid rgba(255, 68, 68, 0.3)',
                        borderRadius: '0.375rem',
                        cursor: 'pointer',
                        transition: 'all 0.3s'
                      }}
                      onMouseEnter={(e) => {
                        e.target.style.backgroundColor = 'rgba(255, 68, 68, 0.3)';
                      }}
                      onMouseLeave={(e) => {
                        e.target.style.backgroundColor = 'rgba(255, 68, 68, 0.2)';
                      }}
                    >
                      <Trash2 size={16} />
                    </button>
                  )}
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
    </DashboardLayout>
  );
}
