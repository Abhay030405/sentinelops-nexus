import React, { useState, useEffect } from 'react';
import { AlertCircle, Shield, Users, Activity, CheckCircle, XCircle, Eye, EyeOff } from 'lucide-react';

const API_BASE = 'http://localhost:8000';

// Power Rangers color scheme
const colors = {
  red: '#E74C3C',
  blue: '#3498DB',
  yellow: '#F1C40F',
  pink: '#E91E63',
  green: '#2ECC71',
  black: '#34495E'
};

const PowerRangersLogin = () => {
  const [activeTab, setActiveTab] = useState('login');
  const [showPassword, setShowPassword] = useState(false);
  const [loginData, setLoginData] = useState({ username: '', password: '' });
  const [createUserData, setCreateUserData] = useState({
    username: '',
    password: '',
    role: 'operator',
    full_name: ''
  });
  const [authToken, setAuthToken] = useState(null);
  const [currentUser, setCurrentUser] = useState(null);
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });

  useEffect(() => {
    const token = localStorage.getItem('sentinel_token');
    if (token) {
      setAuthToken(token);
      fetchCurrentUser(token);
    }
  }, []);

  const showMessage = (type, text) => {
    setMessage({ type, text });
    setTimeout(() => setMessage({ type: '', text: '' }), 5000);
  };

  const fetchCurrentUser = async (token) => {
    try {
      const response = await fetch(`${API_BASE}/users/me`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setCurrentUser(data);
        fetchLogs(token);
      } else {
        localStorage.removeItem('sentinel_token');
        setAuthToken(null);
      }
    } catch (error) {
      console.error('Error fetching user:', error);
    }
  };

  const fetchLogs = async (token) => {
    try {
      const response = await fetch(`${API_BASE}/auth/logs`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setLogs(data);
      }
    } catch (error) {
      console.error('Error fetching logs:', error);
    }
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/auth/scan`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(loginData)
      });
      const data = await response.json();
      if (response.ok) {
        localStorage.setItem('sentinel_token', data.access_token);
        setAuthToken(data.access_token);
        setCurrentUser(data.user);
        showMessage('success', `🎯 Morphin Time! Welcome, ${data.user.role.toUpperCase()} Ranger!`);
        fetchLogs(data.access_token);
      } else {
        showMessage('error', data.detail || 'Authentication failed!');
      }
    } catch (error) {
      showMessage('error', '⚠️ Command Center unreachable! Check backend connection.');
    }
    setLoading(false);
  };

  const handleCreateUser = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/admin/create-user`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${authToken}`
        },
        body: JSON.stringify(createUserData)
      });
      const data = await response.json();
      if (response.ok) {
        showMessage('success', `✅ New Ranger recruited: ${data.username}`);
        setCreateUserData({ username: '', password: '', role: 'operator', full_name: '' });
      } else {
        showMessage('error', data.detail || 'Failed to create user');
      }
    } catch (error) {
      showMessage('error', '⚠️ Command Center unreachable!');
    }
    setLoading(false);
  };

  const handleLogout = () => {
    localStorage.removeItem('sentinel_token');
    setAuthToken(null);
    setCurrentUser(null);
    setLogs([]);
    showMessage('success', '👋 Power Down complete. Stay vigilant, Ranger!');
  };

  const getRoleColor = (role) => {
    const roleColors = {
      admin: colors.red,
      operator: colors.blue,
      viewer: colors.yellow
    };
    return roleColors[role] || colors.black;
  };

  const getRoleBadge = (role) => {
    const badges = {
      admin: '🔴 RED RANGER',
      operator: '🔵 BLUE RANGER',
      viewer: '🟡 YELLOW RANGER'
    };
    return badges[role] || role.toUpperCase();
  };

  if (!authToken) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4" style={{
        background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%)'
      }}>
        <div className="max-w-md w-full">
          {/* Power Rangers Logo Header */}
          <div className="text-center mb-8">
            <div className="inline-block p-4 rounded-full bg-gradient-to-r from-red-500 via-blue-500 to-yellow-500 mb-4">
              <Shield size={64} className="text-white" />
            </div>
            <h1 className="text-4xl font-bold text-white mb-2">SENTINEL OPS</h1>
            <p className="text-blue-300 text-lg">⚡ MORPHIN GRID ACCESS ⚡</p>
          </div>

          {/* Login Card */}
          <div className="bg-gray-800 rounded-lg shadow-2xl p-8 border-2 border-blue-500">
            <form onSubmit={handleLogin} className="space-y-6">
              <div>
                <label className="block text-sm font-bold text-blue-300 mb-2">
                  RANGER ID
                </label>
                <input
                  type="text"
                  value={loginData.username}
                  onChange={(e) => setLoginData({...loginData, username: e.target.value})}
                  className="w-full px-4 py-3 bg-gray-900 border-2 border-blue-600 rounded-lg text-white focus:outline-none focus:border-blue-400"
                  placeholder="Enter your ranger ID"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-bold text-blue-300 mb-2">
                  ACCESS CODE
                </label>
                <div className="relative">
                  <input
                    type={showPassword ? "text" : "password"}
                    value={loginData.password}
                    onChange={(e) => setLoginData({...loginData, password: e.target.value})}
                    className="w-full px-4 py-3 bg-gray-900 border-2 border-blue-600 rounded-lg text-white focus:outline-none focus:border-blue-400"
                    placeholder="Enter access code"
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-3 text-blue-400"
                  >
                    {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                  </button>
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full py-3 bg-gradient-to-r from-red-600 to-blue-600 text-white font-bold rounded-lg hover:from-red-700 hover:to-blue-700 transform hover:scale-105 transition-all duration-200 disabled:opacity-50"
              >
                {loading ? '⚡ MORPHING...' : '🔥 IT\'S MORPHIN TIME! 🔥'}
              </button>
            </form>
          </div>

          {message.text && (
            <div className={`mt-4 p-4 rounded-lg ${message.type === 'success' ? 'bg-green-900 border-green-500' : 'bg-red-900 border-red-500'} border-2`}>
              <p className="text-white text-center font-bold">{message.text}</p>
            </div>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen p-6" style={{
      background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%)'
    }}>
      {/* Header */}
      <div className="max-w-7xl mx-auto mb-8">
        <div className="bg-gradient-to-r from-red-600 via-blue-600 to-yellow-600 rounded-lg p-6 shadow-2xl">
          <div className="flex justify-between items-center">
            <div className="flex items-center gap-4">
              <Shield size={48} className="text-white" />
              <div>
                <h1 className="text-3xl font-bold text-white">SENTINEL OPS COMMAND CENTER</h1>
                <p className="text-blue-200">⚡ Phase 1: Identity Vault Online ⚡</p>
              </div>
            </div>
            <button
              onClick={handleLogout}
              className="px-6 py-3 bg-red-700 text-white font-bold rounded-lg hover:bg-red-800 transform hover:scale-105 transition-all"
            >
              🔴 POWER DOWN
            </button>
          </div>
        </div>
      </div>

      {/* User Profile Card */}
      <div className="max-w-7xl mx-auto mb-8">
        <div className="bg-gray-800 rounded-lg p-6 border-2 shadow-xl" style={{borderColor: getRoleColor(currentUser?.role)}}>
          <div className="flex items-center gap-6">
            <div className="w-24 h-24 rounded-full flex items-center justify-center text-4xl" style={{
              background: `linear-gradient(135deg, ${getRoleColor(currentUser?.role)}, ${colors.black})`
            }}>
              👤
            </div>
            <div className="flex-1">
              <h2 className="text-2xl font-bold text-white mb-2">{currentUser?.full_name}</h2>
              <p className="text-gray-300 mb-2">@{currentUser?.username}</p>
              <div className="inline-block px-4 py-2 rounded-full font-bold text-white" style={{
                backgroundColor: getRoleColor(currentUser?.role)
              }}>
                {getRoleBadge(currentUser?.role)}
              </div>
            </div>
            <div className="text-right">
              <div className="text-green-400 font-bold text-lg mb-2">🟢 ACTIVE</div>
              <div className="text-gray-400 text-sm">QR TOKEN: {currentUser?.qr_token?.substring(0, 8)}...</div>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="max-w-7xl mx-auto mb-6">
        <div className="flex gap-4">
          <button
            onClick={() => setActiveTab('logs')}
            className={`px-6 py-3 font-bold rounded-lg transition-all ${
              activeTab === 'logs' 
                ? 'bg-blue-600 text-white' 
                : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
            }`}
          >
            📊 IDENTITY LOGS
          </button>
          {currentUser?.role === 'admin' && (
            <button
              onClick={() => setActiveTab('create')}
              className={`px-6 py-3 font-bold rounded-lg transition-all ${
                activeTab === 'create' 
                  ? 'bg-red-600 text-white' 
                  : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
              }`}
            >
              👥 RECRUIT RANGER
            </button>
          )}
        </div>
      </div>

      {/* Content Area */}
      <div className="max-w-7xl mx-auto">
        {activeTab === 'logs' && (
          <div className="bg-gray-800 rounded-lg p-6 border-2 border-blue-500 shadow-xl">
            <h3 className="text-2xl font-bold text-white mb-6 flex items-center gap-3">
              <Activity className="text-blue-400" />
              RECENT MORPHIN GRID ACTIVITY
            </h3>
            <div className="space-y-3">
              {logs.length === 0 ? (
                <p className="text-gray-400 text-center py-8">No activity logs yet</p>
              ) : (
                logs.map((log, idx) => (
                  <div key={idx} className="bg-gray-900 p-4 rounded-lg border border-gray-700 flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      {log.success ? (
                        <CheckCircle className="text-green-400" size={24} />
                      ) : (
                        <XCircle className="text-red-400" size={24} />
                      )}
                      <div>
                        <p className="text-white font-bold">{log.username}</p>
                        <p className="text-gray-400 text-sm">{log.action}</p>
                      </div>
                    </div>
                    <div className="text-right text-gray-400 text-sm">
                      <p>{new Date(log.timestamp).toLocaleString()}</p>
                      <p className="text-xs">{log.ip_address}</p>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        )}

        {activeTab === 'create' && currentUser?.role === 'admin' && (
          <div className="bg-gray-800 rounded-lg p-6 border-2 border-red-500 shadow-xl">
            <h3 className="text-2xl font-bold text-white mb-6 flex items-center gap-3">
              <Users className="text-red-400" />
              RECRUIT NEW RANGER
            </h3>
            <form onSubmit={handleCreateUser} className="space-y-6">
              <div className="grid grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-bold text-blue-300 mb-2">FULL NAME</label>
                  <input
                    type="text"
                    value={createUserData.full_name}
                    onChange={(e) => setCreateUserData({...createUserData, full_name: e.target.value})}
                    className="w-full px-4 py-3 bg-gray-900 border-2 border-blue-600 rounded-lg text-white focus:outline-none focus:border-blue-400"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-bold text-blue-300 mb-2">RANGER ID</label>
                  <input
                    type="text"
                    value={createUserData.username}
                    onChange={(e) => setCreateUserData({...createUserData, username: e.target.value})}
                    className="w-full px-4 py-3 bg-gray-900 border-2 border-blue-600 rounded-lg text-white focus:outline-none focus:border-blue-400"
                    required
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-bold text-blue-300 mb-2">ACCESS CODE</label>
                <input
                  type="password"
                  value={createUserData.password}
                  onChange={(e) => setCreateUserData({...createUserData, password: e.target.value})}
                  className="w-full px-4 py-3 bg-gray-900 border-2 border-blue-600 rounded-lg text-white focus:outline-none focus:border-blue-400"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-bold text-blue-300 mb-2">RANGER ROLE</label>
                <select
                  value={createUserData.role}
                  onChange={(e) => setCreateUserData({...createUserData, role: e.target.value})}
                  className="w-full px-4 py-3 bg-gray-900 border-2 border-blue-600 rounded-lg text-white focus:outline-none focus:border-blue-400"
                >
                  <option value="operator">🔵 BLUE RANGER (Operator)</option>
                  <option value="viewer">🟡 YELLOW RANGER (Viewer)</option>
                  <option value="admin">🔴 RED RANGER (Admin)</option>
                </select>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full py-4 bg-gradient-to-r from-red-600 to-blue-600 text-white font-bold text-lg rounded-lg hover:from-red-700 hover:to-blue-700 transform hover:scale-105 transition-all duration-200 disabled:opacity-50"
              >
                {loading ? '⚡ RECRUITING...' : '✨ ACTIVATE RANGER PROTOCOL ✨'}
              </button>
            </form>
          </div>
        )}
      </div>

      {message.text && (
        <div className="fixed bottom-6 right-6 max-w-md">
          <div className={`p-4 rounded-lg shadow-2xl ${message.type === 'success' ? 'bg-green-900 border-green-500' : 'bg-red-900 border-red-500'} border-2`}>
            <p className="text-white font-bold">{message.text}</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default PowerRangersLogin;