import React, { useState, useEffect } from 'react';
import { useDocuments } from '../hooks/useDocuments';
import { useAuth } from '../contexts/AuthContext';
import './WritingAnalytics.css';

interface WritingAnalyticsProps {
  onClose: () => void;
}

const WritingAnalytics: React.FC<WritingAnalyticsProps> = ({ onClose }) => {
  const { user } = useAuth();
  const {
    documents,
    series,
    writingStats,
    writingSessions,
    writingGoals,
    loadWritingStats,
    loadWritingSessions,
    createWritingGoal,
    getTotalWordCount,
    getRecentDocuments
  } = useDocuments();

  const [selectedPeriod, setSelectedPeriod] = useState<'week' | 'month' | 'year'>('month');
  const [showGoalModal, setShowGoalModal] = useState(false);
  const [newGoal, setNewGoal] = useState({
    goal_type: 'daily' as 'daily' | 'weekly' | 'monthly' | 'project',
    target_words: 500,
    document_id: '',
    series_id: ''
  });

  useEffect(() => {
    if (user) {
      loadWritingStats(selectedPeriod);
      loadWritingSessions();
    }
  }, [user, selectedPeriod, loadWritingStats, loadWritingSessions]);

  if (!user) {
    return (
      <div className="analytics-overlay">
        <div className="analytics-container">
          <div className="analytics-header">
            <h2>📊 Writing Analytics</h2>
            <button onClick={onClose} className="close-button">✕</button>
          </div>
          <div className="auth-prompt">
            <h3>🔐 Sign In Required</h3>
            <p>Please sign in to view your writing analytics and progress.</p>
          </div>
        </div>
      </div>
    );
  }

  const handleCreateGoal = async () => {
    try {
      await createWritingGoal({
        goal_type: newGoal.goal_type,
        target_words: newGoal.target_words,
        start_date: new Date().toISOString(),
        document_id: newGoal.document_id || undefined,
        series_id: newGoal.series_id || undefined
      });
      setShowGoalModal(false);
      setNewGoal({
        goal_type: 'daily',
        target_words: 500,
        document_id: '',
        series_id: ''
      });
    } catch (error) {
      console.error('Failed to create goal:', error);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  const formatTime = (minutes: number) => {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return hours > 0 ? `${hours}h ${mins}m` : `${mins}m`;
  };

  const getStreakDays = () => {
    if (!writingSessions.length) return 0;
    
    const today = new Date();
    let streak = 0;
    let currentDate = new Date(today);
    
    while (streak < 365) { // Max 365 day check
      const dayHasSessions = writingSessions.some(session => {
        const sessionDate = new Date(session.start_time);
        return sessionDate.toDateString() === currentDate.toDateString();
      });
      
      if (!dayHasSessions) break;
      
      streak++;
      currentDate.setDate(currentDate.getDate() - 1);
    }
    
    return streak;
  };

  const getProductivityTrend = () => {
    const last7Days = writingSessions
      .filter(session => {
        const sessionDate = new Date(session.start_time);
        const weekAgo = new Date();
        weekAgo.setDate(weekAgo.getDate() - 7);
        return sessionDate >= weekAgo;
      })
      .reduce((total, session) => total + session.words_written, 0);

    const previous7Days = writingSessions
      .filter(session => {
        const sessionDate = new Date(session.start_time);
        const twoWeeksAgo = new Date();
        twoWeeksAgo.setDate(twoWeeksAgo.getDate() - 14);
        const weekAgo = new Date();
        weekAgo.setDate(weekAgo.getDate() - 7);
        return sessionDate >= twoWeeksAgo && sessionDate < weekAgo;
      })
      .reduce((total, session) => total + session.words_written, 0);

    if (previous7Days === 0) return last7Days > 0 ? 100 : 0;
    return Math.round(((last7Days - previous7Days) / previous7Days) * 100);
  };

  const getGoalProgress = (goal: any) => {
    const progress = goal.current_words / goal.target_words;
    return Math.min(progress * 100, 100);
  };

  return (
    <div className="analytics-overlay">
      <div className="analytics-container">
        {/* Header */}
        <div className="analytics-header">
          <h2>📊 Writing Analytics</h2>
          <div className="header-controls">
            <select 
              value={selectedPeriod} 
              onChange={(e) => setSelectedPeriod(e.target.value as 'week' | 'month' | 'year')}
              className="period-selector"
            >
              <option value="week">This Week</option>
              <option value="month">This Month</option>
              <option value="year">This Year</option>
            </select>
            <button onClick={onClose} className="close-button">✕</button>
          </div>
        </div>

        <div className="analytics-content">
          {/* Quick Stats */}
          <div className="quick-stats">
            <div className="stat-card primary">
              <div className="stat-icon">📈</div>
              <div className="stat-info">
                <div className="stat-value">{getTotalWordCount().toLocaleString()}</div>
                <div className="stat-label">Total Words</div>
              </div>
            </div>
            
            <div className="stat-card">
              <div className="stat-icon">🔥</div>
              <div className="stat-info">
                <div className="stat-value">{getStreakDays()}</div>
                <div className="stat-label">Day Streak</div>
              </div>
            </div>
            
            <div className="stat-card">
              <div className="stat-icon">📄</div>
              <div className="stat-info">
                <div className="stat-value">{documents.length}</div>
                <div className="stat-label">Documents</div>
              </div>
            </div>
            
            <div className="stat-card">
              <div className="stat-icon">📚</div>
              <div className="stat-info">
                <div className="stat-value">{series.length}</div>
                <div className="stat-label">Series</div>
              </div>
            </div>
          </div>

          {/* Writing Goals */}
          <div className="section">
            <div className="section-header">
              <h3>🎯 Writing Goals</h3>
              <button onClick={() => setShowGoalModal(true)} className="add-goal-button">
                ➕ Add Goal
              </button>
            </div>
            
            <div className="goals-grid">
              {writingGoals.map(goal => (
                <div key={goal.id} className="goal-card">
                  <div className="goal-header">
                    <div className="goal-type">{goal.goal_type.charAt(0).toUpperCase() + goal.goal_type.slice(1)} Goal</div>
                    <div className="goal-progress-text">
                      {goal.current_words.toLocaleString()} / {goal.target_words.toLocaleString()} words
                    </div>
                  </div>
                  <div className="goal-progress">
                    <div 
                      className="goal-progress-bar" 
                      style={{ width: `${getGoalProgress(goal)}%` }}
                    ></div>
                  </div>
                  <div className="goal-percentage">{Math.round(getGoalProgress(goal))}% complete</div>
                </div>
              ))}
              
              {writingGoals.length === 0 && (
                <div className="empty-goals">
                  <p>No writing goals set yet. Create your first goal to track your progress!</p>
                </div>
              )}
            </div>
          </div>

          {/* Productivity Insights */}
          <div className="section">
            <h3>📊 Productivity Insights</h3>
            
            <div className="insights-grid">
              <div className="insight-card">
                <div className="insight-title">Weekly Trend</div>
                <div className="insight-value">
                  <span className={getProductivityTrend() >= 0 ? 'positive' : 'negative'}>
                    {getProductivityTrend() >= 0 ? '📈' : '📉'} {Math.abs(getProductivityTrend())}%
                  </span>
                </div>
                <div className="insight-description">
                  vs. previous week
                </div>
              </div>
              
              <div className="insight-card">
                <div className="insight-title">Average Session</div>
                <div className="insight-value">
                  {writingSessions.length > 0 
                    ? Math.round(writingSessions.reduce((acc, s) => acc + s.words_written, 0) / writingSessions.length).toLocaleString()
                    : 0
                  } words
                </div>
                <div className="insight-description">
                  per writing session
                </div>
              </div>
              
              <div className="insight-card">
                <div className="insight-title">Best Writing Day</div>
                <div className="insight-value">
                  {writingStats?.most_productive_day || 'No data'}
                </div>
                <div className="insight-description">
                  highest word count
                </div>
              </div>
              
              <div className="insight-card">
                <div className="insight-title">Average Daily</div>
                <div className="insight-value">
                  {writingStats?.avg_words_per_day ? Math.round(writingStats.avg_words_per_day).toLocaleString() : 0} words
                </div>
                <div className="insight-description">
                  words per day
                </div>
              </div>
            </div>
          </div>

          {/* Recent Sessions */}
          <div className="section">
            <h3>⏱️ Recent Writing Sessions</h3>
            
            <div className="sessions-list">
              {writingSessions.slice(0, 10).map(session => (
                <div key={session.id} className="session-item">
                  <div className="session-info">
                    <div className="session-date">{formatDate(session.start_time)}</div>
                    <div className="session-document">
                      {documents.find(doc => doc.id === session.document_id)?.title || 'Unknown Document'}
                    </div>
                  </div>
                  <div className="session-stats">
                    <span className="session-words">{session.words_written.toLocaleString()} words</span>
                    <span className="session-time">{formatTime(session.time_spent_minutes)}</span>
                  </div>
                </div>
              ))}
              
              {writingSessions.length === 0 && (
                <div className="empty-sessions">
                  <p>No writing sessions recorded yet. Start writing to see your progress!</p>
                </div>
              )}
            </div>
          </div>

          {/* Recent Documents */}
          <div className="section">
            <h3>📝 Recently Updated</h3>
            
            <div className="recent-documents">
              {getRecentDocuments(5).map(doc => (
                <div key={doc.id} className="recent-doc-item">
                  <div className="doc-icon">
                    {doc.document_type === 'novel' ? '📖' : 
                     doc.document_type === 'chapter' ? '📃' : 
                     doc.document_type === 'character_sheet' ? '👤' : 
                     doc.document_type === 'outline' ? '📋' : '📝'}
                  </div>
                  <div className="doc-info">
                    <div className="doc-title">{doc.title}</div>
                    <div className="doc-meta">
                      {(doc.word_count || 0).toLocaleString()} words • {formatDate(doc.updated_at)}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Goal Creation Modal */}
        {showGoalModal && (
          <div className="modal-overlay">
            <div className="modal">
              <h3>🎯 Create Writing Goal</h3>
              
              <div className="form-group">
                <label>Goal Type</label>
                <select 
                  value={newGoal.goal_type} 
                  onChange={(e) => setNewGoal({...newGoal, goal_type: e.target.value as any})}
                >
                  <option value="daily">Daily Goal</option>
                  <option value="weekly">Weekly Goal</option>
                  <option value="monthly">Monthly Goal</option>
                  <option value="project">Project Goal</option>
                </select>
              </div>
              
              <div className="form-group">
                <label>Target Words</label>
                <input 
                  type="number" 
                  value={newGoal.target_words}
                  onChange={(e) => setNewGoal({...newGoal, target_words: Number(e.target.value)})}
                  min="1"
                />
              </div>
              
              <div className="form-group">
                <label>Specific Document (Optional)</label>
                <select 
                  value={newGoal.document_id} 
                  onChange={(e) => setNewGoal({...newGoal, document_id: e.target.value})}
                >
                  <option value="">All Documents</option>
                  {documents.map(doc => (
                    <option key={doc.id} value={doc.id}>{doc.title}</option>
                  ))}
                </select>
              </div>
              
              <div className="form-group">
                <label>Specific Series (Optional)</label>
                <select 
                  value={newGoal.series_id} 
                  onChange={(e) => setNewGoal({...newGoal, series_id: e.target.value})}
                >
                  <option value="">All Series</option>
                  {series.map(s => (
                    <option key={s.id} value={s.id}>{s.name}</option>
                  ))}
                </select>
              </div>
              
              <div className="modal-actions">
                <button onClick={handleCreateGoal} className="create-goal-button">
                  Create Goal
                </button>
                <button onClick={() => setShowGoalModal(false)} className="cancel-button">
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default WritingAnalytics; 
import { useDocuments } from '../hooks/useDocuments';
import { useAuth } from '../contexts/AuthContext';
import './WritingAnalytics.css';

interface WritingAnalyticsProps {
  onClose: () => void;
}

const WritingAnalytics: React.FC<WritingAnalyticsProps> = ({ onClose }) => {
  const { user } = useAuth();
  const {
    documents,
    series,
    writingStats,
    writingSessions,
    writingGoals,
    loadWritingStats,
    loadWritingSessions,
    createWritingGoal,
    getTotalWordCount,
    getRecentDocuments
  } = useDocuments();

  const [selectedPeriod, setSelectedPeriod] = useState<'week' | 'month' | 'year'>('month');
  const [showGoalModal, setShowGoalModal] = useState(false);
  const [newGoal, setNewGoal] = useState({
    goal_type: 'daily' as 'daily' | 'weekly' | 'monthly' | 'project',
    target_words: 500,
    document_id: '',
    series_id: ''
  });

  useEffect(() => {
    if (user) {
      loadWritingStats(selectedPeriod);
      loadWritingSessions();
    }
  }, [user, selectedPeriod, loadWritingStats, loadWritingSessions]);

  if (!user) {
    return (
      <div className="analytics-overlay">
        <div className="analytics-container">
          <div className="analytics-header">
            <h2>📊 Writing Analytics</h2>
            <button onClick={onClose} className="close-button">✕</button>
          </div>
          <div className="auth-prompt">
            <h3>🔐 Sign In Required</h3>
            <p>Please sign in to view your writing analytics and progress.</p>
          </div>
        </div>
      </div>
    );
  }

  const handleCreateGoal = async () => {
    try {
      await createWritingGoal({
        goal_type: newGoal.goal_type,
        target_words: newGoal.target_words,
        start_date: new Date().toISOString(),
        document_id: newGoal.document_id || undefined,
        series_id: newGoal.series_id || undefined
      });
      setShowGoalModal(false);
      setNewGoal({
        goal_type: 'daily',
        target_words: 500,
        document_id: '',
        series_id: ''
      });
    } catch (error) {
      console.error('Failed to create goal:', error);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  const formatTime = (minutes: number) => {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return hours > 0 ? `${hours}h ${mins}m` : `${mins}m`;
  };

  const getStreakDays = () => {
    if (!writingSessions.length) return 0;
    
    const today = new Date();
    let streak = 0;
    let currentDate = new Date(today);
    
    while (streak < 365) { // Max 365 day check
      const dayHasSessions = writingSessions.some(session => {
        const sessionDate = new Date(session.start_time);
        return sessionDate.toDateString() === currentDate.toDateString();
      });
      
      if (!dayHasSessions) break;
      
      streak++;
      currentDate.setDate(currentDate.getDate() - 1);
    }
    
    return streak;
  };

  const getProductivityTrend = () => {
    const last7Days = writingSessions
      .filter(session => {
        const sessionDate = new Date(session.start_time);
        const weekAgo = new Date();
        weekAgo.setDate(weekAgo.getDate() - 7);
        return sessionDate >= weekAgo;
      })
      .reduce((total, session) => total + session.words_written, 0);

    const previous7Days = writingSessions
      .filter(session => {
        const sessionDate = new Date(session.start_time);
        const twoWeeksAgo = new Date();
        twoWeeksAgo.setDate(twoWeeksAgo.getDate() - 14);
        const weekAgo = new Date();
        weekAgo.setDate(weekAgo.getDate() - 7);
        return sessionDate >= twoWeeksAgo && sessionDate < weekAgo;
      })
      .reduce((total, session) => total + session.words_written, 0);

    if (previous7Days === 0) return last7Days > 0 ? 100 : 0;
    return Math.round(((last7Days - previous7Days) / previous7Days) * 100);
  };

  const getGoalProgress = (goal: any) => {
    const progress = goal.current_words / goal.target_words;
    return Math.min(progress * 100, 100);
  };

  return (
    <div className="analytics-overlay">
      <div className="analytics-container">
        {/* Header */}
        <div className="analytics-header">
          <h2>📊 Writing Analytics</h2>
          <div className="header-controls">
            <select 
              value={selectedPeriod} 
              onChange={(e) => setSelectedPeriod(e.target.value as 'week' | 'month' | 'year')}
              className="period-selector"
            >
              <option value="week">This Week</option>
              <option value="month">This Month</option>
              <option value="year">This Year</option>
            </select>
            <button onClick={onClose} className="close-button">✕</button>
          </div>
        </div>

        <div className="analytics-content">
          {/* Quick Stats */}
          <div className="quick-stats">
            <div className="stat-card primary">
              <div className="stat-icon">📈</div>
              <div className="stat-info">
                <div className="stat-value">{getTotalWordCount().toLocaleString()}</div>
                <div className="stat-label">Total Words</div>
              </div>
            </div>
            
            <div className="stat-card">
              <div className="stat-icon">🔥</div>
              <div className="stat-info">
                <div className="stat-value">{getStreakDays()}</div>
                <div className="stat-label">Day Streak</div>
              </div>
            </div>
            
            <div className="stat-card">
              <div className="stat-icon">📄</div>
              <div className="stat-info">
                <div className="stat-value">{documents.length}</div>
                <div className="stat-label">Documents</div>
              </div>
            </div>
            
            <div className="stat-card">
              <div className="stat-icon">📚</div>
              <div className="stat-info">
                <div className="stat-value">{series.length}</div>
                <div className="stat-label">Series</div>
              </div>
            </div>
          </div>

          {/* Writing Goals */}
          <div className="section">
            <div className="section-header">
              <h3>🎯 Writing Goals</h3>
              <button onClick={() => setShowGoalModal(true)} className="add-goal-button">
                ➕ Add Goal
              </button>
            </div>
            
            <div className="goals-grid">
              {writingGoals.map(goal => (
                <div key={goal.id} className="goal-card">
                  <div className="goal-header">
                    <div className="goal-type">{goal.goal_type.charAt(0).toUpperCase() + goal.goal_type.slice(1)} Goal</div>
                    <div className="goal-progress-text">
                      {goal.current_words.toLocaleString()} / {goal.target_words.toLocaleString()} words
                    </div>
                  </div>
                  <div className="goal-progress">
                    <div 
                      className="goal-progress-bar" 
                      style={{ width: `${getGoalProgress(goal)}%` }}
                    ></div>
                  </div>
                  <div className="goal-percentage">{Math.round(getGoalProgress(goal))}% complete</div>
                </div>
              ))}
              
              {writingGoals.length === 0 && (
                <div className="empty-goals">
                  <p>No writing goals set yet. Create your first goal to track your progress!</p>
                </div>
              )}
            </div>
          </div>

          {/* Productivity Insights */}
          <div className="section">
            <h3>📊 Productivity Insights</h3>
            
            <div className="insights-grid">
              <div className="insight-card">
                <div className="insight-title">Weekly Trend</div>
                <div className="insight-value">
                  <span className={getProductivityTrend() >= 0 ? 'positive' : 'negative'}>
                    {getProductivityTrend() >= 0 ? '📈' : '📉'} {Math.abs(getProductivityTrend())}%
                  </span>
                </div>
                <div className="insight-description">
                  vs. previous week
                </div>
              </div>
              
              <div className="insight-card">
                <div className="insight-title">Average Session</div>
                <div className="insight-value">
                  {writingSessions.length > 0 
                    ? Math.round(writingSessions.reduce((acc, s) => acc + s.words_written, 0) / writingSessions.length).toLocaleString()
                    : 0
                  } words
                </div>
                <div className="insight-description">
                  per writing session
                </div>
              </div>
              
              <div className="insight-card">
                <div className="insight-title">Best Writing Day</div>
                <div className="insight-value">
                  {writingStats?.most_productive_day || 'No data'}
                </div>
                <div className="insight-description">
                  highest word count
                </div>
              </div>
              
              <div className="insight-card">
                <div className="insight-title">Average Daily</div>
                <div className="insight-value">
                  {writingStats?.avg_words_per_day ? Math.round(writingStats.avg_words_per_day).toLocaleString() : 0} words
                </div>
                <div className="insight-description">
                  words per day
                </div>
              </div>
            </div>
          </div>

          {/* Recent Sessions */}
          <div className="section">
            <h3>⏱️ Recent Writing Sessions</h3>
            
            <div className="sessions-list">
              {writingSessions.slice(0, 10).map(session => (
                <div key={session.id} className="session-item">
                  <div className="session-info">
                    <div className="session-date">{formatDate(session.start_time)}</div>
                    <div className="session-document">
                      {documents.find(doc => doc.id === session.document_id)?.title || 'Unknown Document'}
                    </div>
                  </div>
                  <div className="session-stats">
                    <span className="session-words">{session.words_written.toLocaleString()} words</span>
                    <span className="session-time">{formatTime(session.time_spent_minutes)}</span>
                  </div>
                </div>
              ))}
              
              {writingSessions.length === 0 && (
                <div className="empty-sessions">
                  <p>No writing sessions recorded yet. Start writing to see your progress!</p>
                </div>
              )}
            </div>
          </div>

          {/* Recent Documents */}
          <div className="section">
            <h3>📝 Recently Updated</h3>
            
            <div className="recent-documents">
              {getRecentDocuments(5).map(doc => (
                <div key={doc.id} className="recent-doc-item">
                  <div className="doc-icon">
                    {doc.document_type === 'novel' ? '📖' : 
                     doc.document_type === 'chapter' ? '📃' : 
                     doc.document_type === 'character_sheet' ? '👤' : 
                     doc.document_type === 'outline' ? '📋' : '📝'}
                  </div>
                  <div className="doc-info">
                    <div className="doc-title">{doc.title}</div>
                    <div className="doc-meta">
                      {(doc.word_count || 0).toLocaleString()} words • {formatDate(doc.updated_at)}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Goal Creation Modal */}
        {showGoalModal && (
          <div className="modal-overlay">
            <div className="modal">
              <h3>🎯 Create Writing Goal</h3>
              
              <div className="form-group">
                <label>Goal Type</label>
                <select 
                  value={newGoal.goal_type} 
                  onChange={(e) => setNewGoal({...newGoal, goal_type: e.target.value as any})}
                >
                  <option value="daily">Daily Goal</option>
                  <option value="weekly">Weekly Goal</option>
                  <option value="monthly">Monthly Goal</option>
                  <option value="project">Project Goal</option>
                </select>
              </div>
              
              <div className="form-group">
                <label>Target Words</label>
                <input 
                  type="number" 
                  value={newGoal.target_words}
                  onChange={(e) => setNewGoal({...newGoal, target_words: Number(e.target.value)})}
                  min="1"
                />
              </div>
              
              <div className="form-group">
                <label>Specific Document (Optional)</label>
                <select 
                  value={newGoal.document_id} 
                  onChange={(e) => setNewGoal({...newGoal, document_id: e.target.value})}
                >
                  <option value="">All Documents</option>
                  {documents.map(doc => (
                    <option key={doc.id} value={doc.id}>{doc.title}</option>
                  ))}
                </select>
              </div>
              
              <div className="form-group">
                <label>Specific Series (Optional)</label>
                <select 
                  value={newGoal.series_id} 
                  onChange={(e) => setNewGoal({...newGoal, series_id: e.target.value})}
                >
                  <option value="">All Series</option>
                  {series.map(s => (
                    <option key={s.id} value={s.id}>{s.name}</option>
                  ))}
                </select>
              </div>
              
              <div className="modal-actions">
                <button onClick={handleCreateGoal} className="create-goal-button">
                  Create Goal
                </button>
                <button onClick={() => setShowGoalModal(false)} className="cancel-button">
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default WritingAnalytics; 