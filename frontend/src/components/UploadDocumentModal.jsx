import { useState } from 'react';
import knowledgeCrystalService from '../services/knowledgeCrystalService';

export default function UploadDocumentModal({ onClose, onSuccess }) {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    category: 'agent',
    mission_id: '',
    country: '',
    tags: '',
    file: null,
  });
  const [fileContent, setFileContent] = useState('');
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');

  const handleFileChange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setFormData({ ...formData, file });
    
    // Read file content
    const reader = new FileReader();
    reader.onload = (event) => {
      setFileContent(event.target.result);
    };
    reader.onerror = () => {
      setError('Failed to read file');
    };
    reader.readAsText(file);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    // Validation
    if (!formData.title.trim()) {
      setError('Title is required');
      return;
    }

    if (!formData.file || !fileContent) {
      setError('Please select a file');
      return;
    }

    try {
      setUploading(true);

      // Prepare upload data
      const uploadData = {
        title: formData.title,
        file_content: fileContent,
        category: formData.category,
        description: formData.description,
        mission_id: formData.mission_id,
        country: formData.country,
        tags: formData.tags ? formData.tags.split(',').map(t => t.trim()).filter(t => t) : [],
        uploaded_by: 'admin',
        metadata: {
          original_filename: formData.file.name,
          file_size: formData.file.size,
          file_type: formData.file.type,
          description: formData.description,
        },
      };

      await knowledgeCrystalService.uploadDocument(uploadData);
      onSuccess();
    } catch (err) {
      setError(err.message || 'Failed to upload document');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div style={styles.overlay} onClick={onClose}>
      <div style={styles.modal} onClick={(e) => e.stopPropagation()}>
        <div style={styles.header}>
          <h2 style={styles.title}>Upload Document</h2>
          <button onClick={onClose} style={styles.closeButton}>×</button>
        </div>

        <form onSubmit={handleSubmit} style={styles.form}>
          {error && (
            <div style={styles.errorBox}>
              {error}
            </div>
          )}

          {/* Title */}
          <div style={styles.formGroup}>
            <label style={styles.label}>
              Document Title <span style={styles.required}>*</span>
            </label>
            <input
              type="text"
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              placeholder="Enter document title"
              style={styles.input}
              required
            />
          </div>

          {/* Description */}
          <div style={styles.formGroup}>
            <label style={styles.label}>Short Description</label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              placeholder="Brief description of the document"
              style={styles.textarea}
              rows="3"
            />
          </div>

          {/* Category */}
          <div style={styles.formGroup}>
            <label style={styles.label}>
              Category <span style={styles.required}>*</span>
            </label>
            <select
              value={formData.category}
              onChange={(e) => setFormData({ ...formData, category: e.target.value })}
              style={styles.select}
              required
            >
              <option value="agent">Agent - Mission Documents</option>
              <option value="technician">Technician - Technical Documentation</option>
            </select>
            <p style={styles.hint}>
              {formData.category === 'agent' 
                ? 'Mission-related documents for agents' 
                : 'Technical documentation for technicians'}
            </p>
          </div>

          {/* Mission ID (for agent documents) */}
          {formData.category === 'agent' && (
            <div style={styles.formGroup}>
              <label style={styles.label}>Mission ID (Optional)</label>
              <input
                type="text"
                value={formData.mission_id}
                onChange={(e) => setFormData({ ...formData, mission_id: e.target.value })}
                placeholder="e.g., MISSION-2024-001"
                style={styles.input}
              />
            </div>
          )}

          {/* Country (for agent documents) */}
          {formData.category === 'agent' && (
            <div style={styles.formGroup}>
              <label style={styles.label}>Country (Optional)</label>
              <input
                type="text"
                value={formData.country}
                onChange={(e) => setFormData({ ...formData, country: e.target.value })}
                placeholder="e.g., USA, UK, France"
                style={styles.input}
              />
            </div>
          )}

          {/* Tags */}
          <div style={styles.formGroup}>
            <label style={styles.label}>Tags (Optional)</label>
            <input
              type="text"
              value={formData.tags}
              onChange={(e) => setFormData({ ...formData, tags: e.target.value })}
              placeholder="Enter tags separated by commas (e.g., urgent, classified, technical)"
              style={styles.input}
            />
          </div>

          {/* File Upload */}
          <div style={styles.formGroup}>
            <label style={styles.label}>
              Upload File <span style={styles.required}>*</span>
            </label>
            <input
              type="file"
              onChange={handleFileChange}
              accept=".txt,.pdf,.jpg,.jpeg,.png,.doc,.docx,.md"
              style={styles.fileInput}
              required
            />
            <p style={styles.hint}>
              Supported formats: TXT, PDF, JPG, PNG, DOC, DOCX, MD
            </p>
            {formData.file && (
              <p style={styles.fileName}>
                Selected: {formData.file.name}
              </p>
            )}
          </div>

          {/* Buttons */}
          <div style={styles.buttonGroup}>
            <button
              type="button"
              onClick={onClose}
              style={styles.cancelButton}
              disabled={uploading}
            >
              Cancel
            </button>
            <button
              type="submit"
              style={styles.submitButton}
              disabled={uploading}
            >
              {uploading ? 'Uploading...' : 'Upload Document'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

const styles = {
  overlay: {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(10, 14, 39, 0.85)',
    backdropFilter: 'blur(8px)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 9999,
    padding: '20px',
  },
  modal: {
    backgroundColor: '#1a1f3a',
    borderRadius: '12px',
    width: '100%',
    maxWidth: '600px',
    maxHeight: '90vh',
    overflow: 'auto',
    border: '1px solid #2d3354',
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '20px 24px',
    borderBottom: '1px solid #2d3354',
  },
  title: {
    color: '#29a399',
    fontSize: '1.5rem',
    fontWeight: '600',
    margin: 0,
  },
  closeButton: {
    background: 'none',
    border: 'none',
    color: '#8b92b0',
    fontSize: '2rem',
    cursor: 'pointer',
    padding: 0,
    width: '32px',
    height: '32px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
  form: {
    padding: '24px',
  },
  errorBox: {
    backgroundColor: '#dc3545',
    color: 'white',
    padding: '12px',
    borderRadius: '8px',
    marginBottom: '20px',
    fontSize: '0.9rem',
  },
  formGroup: {
    marginBottom: '20px',
  },
  label: {
    display: 'block',
    color: '#c5c7d4',
    fontSize: '0.95rem',
    fontWeight: '500',
    marginBottom: '8px',
  },
  required: {
    color: '#dc3545',
  },
  input: {
    width: '100%',
    padding: '12px',
    backgroundColor: '#0a0e27',
    border: '1px solid #2d3354',
    borderRadius: '8px',
    color: 'white',
    fontSize: '1rem',
    boxSizing: 'border-box',
  },
  textarea: {
    width: '100%',
    padding: '12px',
    backgroundColor: '#0a0e27',
    border: '1px solid #2d3354',
    borderRadius: '8px',
    color: 'white',
    fontSize: '1rem',
    fontFamily: 'inherit',
    resize: 'vertical',
    boxSizing: 'border-box',
  },
  select: {
    width: '100%',
    padding: '12px',
    backgroundColor: '#0a0e27',
    border: '1px solid #2d3354',
    borderRadius: '8px',
    color: 'white',
    fontSize: '1rem',
    cursor: 'pointer',
    boxSizing: 'border-box',
  },
  fileInput: {
    width: '100%',
    padding: '12px',
    backgroundColor: '#0a0e27',
    border: '1px solid #2d3354',
    borderRadius: '8px',
    color: 'white',
    fontSize: '1rem',
    cursor: 'pointer',
    boxSizing: 'border-box',
  },
  hint: {
    color: '#8b92b0',
    fontSize: '0.85rem',
    marginTop: '6px',
    margin: '6px 0 0 0',
  },
  fileName: {
    color: '#29a399',
    fontSize: '0.9rem',
    marginTop: '8px',
    margin: '8px 0 0 0',
  },
  buttonGroup: {
    display: 'flex',
    gap: '12px',
    marginTop: '24px',
  },
  cancelButton: {
    flex: 1,
    padding: '12px',
    backgroundColor: 'transparent',
    border: '1px solid #2d3354',
    borderRadius: '8px',
    color: '#c5c7d4',
    fontSize: '1rem',
    fontWeight: '600',
    cursor: 'pointer',
  },
  submitButton: {
    flex: 1,
    padding: '12px',
    backgroundColor: '#29a399',
    border: 'none',
    borderRadius: '8px',
    color: 'white',
    fontSize: '1rem',
    fontWeight: '600',
    cursor: 'pointer',
  },
};
