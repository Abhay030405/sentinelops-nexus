import React from 'react';
import './KanbanBoard.css';

const KanbanBoard = ({ issues = [], completedIssues = [], onDragStart, onDrop, onDragOver }) => {
  return (
    <div className="kanban-board">
      <div className="kanban-column">
        <div className="kanban-header">
          <h3>Active Issues</h3>
          <span className="issue-count">{issues.length}</span>
        </div>
        <div 
          className="kanban-content"
          onDrop={(e) => onDrop && onDrop(e, 'active')}
          onDragOver={(e) => onDragOver && onDragOver(e)}
        >
          {issues.length === 0 ? (
            <p className="empty-state">No active issues</p>
          ) : (
            issues.map((issue) => (
              <div
                key={issue.id}
                className="kanban-card"
                draggable
                onDragStart={(e) => onDragStart && onDragStart(e, issue)}
              >
                <div className="card-header">
                  <h4>{issue.title}</h4>
                  <span className={`priority-badge priority-${issue.priority}`}>
                    {issue.priority}
                  </span>
                </div>
                <p className="card-description">{issue.description}</p>
                {issue.assignedTo && (
                  <div className="card-footer">
                    <span className="assigned-to">Assigned: {issue.assignedTo}</span>
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      </div>

      <div className="kanban-column completed">
        <div className="kanban-header">
          <h3>Completed</h3>
          <span className="issue-count">{completedIssues.length}</span>
        </div>
        <div 
          className="kanban-content"
          onDrop={(e) => onDrop && onDrop(e, 'completed')}
          onDragOver={(e) => onDragOver && onDragOver(e)}
        >
          {completedIssues.length === 0 ? (
            <p className="empty-state">No completed issues</p>
          ) : (
            completedIssues.map((issue) => (
              <div
                key={issue.id}
                className="kanban-card completed-card"
                draggable
                onDragStart={(e) => onDragStart && onDragStart(e, issue)}
              >
                <div className="card-header">
                  <h4>{issue.title}</h4>
                </div>
                <p className="card-description">{issue.description}</p>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default KanbanBoard;
