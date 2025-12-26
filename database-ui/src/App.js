import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

const API_URL = 'http://localhost:5000/api';

function App() {
  const [tables, setTables] = useState([]);
  const [currentTable, setCurrentTable] = useState(null);
  const [tableData, setTableData] = useState([]);
  const [columns, setColumns] = useState([]);
  const [view, setView] = useState('login'); // 'login', 'folders', 'table', 'edit', 'create'
  const [editRow, setEditRow] = useState(null);
  const [formData, setFormData] = useState({});
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [deleteRow, setDeleteRow] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [codeInput, setCodeInput] = useState('');
  const [codeError, setCodeError] = useState('');
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    if (isAuthenticated) {
      loadTables();
    }
  }, [isAuthenticated]);

  const handleCodeSubmit = async (e) => {
    e.preventDefault();
    setCodeError('');
    setLoading(true);

    try {
      const response = await axios.post(`${API_URL}/verify-code`, {
        code: codeInput.trim().toUpperCase()
      });

      if (response.data.valid) {
        setIsAuthenticated(true);
        setView('folders');
      }
    } catch (err) {
      setCodeError(err.response?.data?.message || 'Invalid code. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const loadTables = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_URL}/tables`);
      setTables(response.data.tables);
      setLoading(false);
    } catch (err) {
      setError('Failed to load tables');
      setLoading(false);
    }
  };

  const loadTableData = async (tableName) => {
    try {
      const response = await axios.get(`${API_URL}/tables/${tableName}`);
      setTableData(response.data.data);
      setColumns(response.data.columns);
      setCurrentTable(tableName);
      setView('table');
    } catch (err) {
      setError(`Failed to load table: ${tableName}`);
    }
  };

  const handleCreateRow = () => {
    const newFormData = {};
    columns.forEach(col => {
      if (col.toLowerCase().includes('id')) {
        newFormData[col] = null;
      } else if (col.toLowerCase().includes('name') || col.toLowerCase().includes('username') || col.toLowerCase().includes('title')) {
        newFormData[col] = 'New Item';
      } else if (col.toLowerCase().includes('email')) {
        newFormData[col] = 'new@example.com';
      } else if (col.toLowerCase().includes('price')) {
        newFormData[col] = 0.00;
      } else if (col.toLowerCase().includes('age') || col.toLowerCase().includes('stock') || col.toLowerCase().includes('priority')) {
        newFormData[col] = 0;
      } else if (col.toLowerCase().includes('description')) {
        newFormData[col] = 'Description';
      } else if (col.toLowerCase().includes('category')) {
        newFormData[col] = 'General';
      } else if (col.toLowerCase().includes('completed')) {
        newFormData[col] = false;
      } else {
        newFormData[col] = '';
      }
    });
    setFormData(newFormData);
    setView('create');
  };

  const handleEditRow = (row) => {
    setEditRow(row);
    setFormData({ ...row });
    setView('edit');
  };

  const handleSave = async () => {
    try {
      if (view === 'create') {
        await axios.post(`${API_URL}/tables/${currentTable}/rows`, formData);
      } else {
        await axios.put(`${API_URL}/tables/${currentTable}/rows`, {
          old: editRow,
          new: formData
        });
      }
      loadTableData(currentTable);
      setView('table');
      setError(null);
    } catch (err) {
      setError(err.response?.data?.error || 'Save failed');
    }
  };

  const handleDelete = async () => {
    try {
      await axios.delete(`${API_URL}/tables/${currentTable}/rows`, { data: deleteRow });
      loadTableData(currentTable);
      setShowDeleteConfirm(false);
      setDeleteRow(null);
    } catch (err) {
      setError('Delete failed');
    }
  };

  const handleFormChange = (col, value) => {
    setFormData({ ...formData, [col]: value });
  };

  return (
    <div className="App">
      {view === 'login' && (
        <div className="login-view">
          <div className="login-container">
            <div className="login-box">
              <h1>🔒 Secret Database Access</h1>
              <p className="login-description">
                Enter the access code from the game to unlock the database
              </p>

              <form onSubmit={handleCodeSubmit}>
                <div className="code-input-group">
                  <input
                    type="text"
                    value={codeInput}
                    onChange={(e) => setCodeInput(e.target.value.toUpperCase())}
                    placeholder="ENTER CODE"
                    maxLength={6}
                    className="code-input"
                    autoFocus
                  />
                  <button type="submit" className="submit-btn" disabled={loading || codeInput.length !== 6}>
                    {loading ? 'Verifying...' : 'Unlock'}
                  </button>
                </div>

                {codeError && <div className="error-message">{codeError}</div>}

                <div className="login-hint">
                  <p>💡 Hint: Find the secret passage in the game to get the code</p>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      {view === 'folders' && (
        <div className="folders-view">
          <div className="header">
            <h1>Secret Database</h1>
            <div className="status">
              <span className="status-dot connected"></span>
              Connected
            </div>
          </div>
          <div className="folders-grid">
            {tables.map(table => (
              <div key={table} className="folder-card" onClick={() => loadTableData(table)}>
                <div className="folder-icon">
                  <svg viewBox="0 0 60 50" width="60" height="50">
                    <polygon points="0,10 20,10 25,0 60,0 60,10" fill="#4285f4" />
                    <rect x="0" y="10" width="60" height="40" rx="3" fill="#4285f4" />
                  </svg>
                </div>
                <div className="folder-name">{table}</div>
                <div className="folder-type">Table</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {view === 'table' && (
        <div className="table-view">
          <div className="header">
            <button className="back-btn" onClick={() => setView('folders')}>← Back</button>
            <span className="breadcrumb">Database / {currentTable}</span>
            <button className="new-btn" onClick={handleCreateRow}>+ New Row</button>
          </div>
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  {columns.slice(0, 5).map(col => (
                    <th key={col}>{col}</th>
                  ))}
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {tableData.map((row, idx) => (
                  <tr key={idx}>
                    {columns.slice(0, 5).map(col => (
                      <td key={col}>{String(row[col] || '').substring(0, 30)}</td>
                    ))}
                    <td className="actions">
                      <button className="edit-btn" onClick={() => handleEditRow(row)}>Edit</button>
                      <button className="delete-btn" onClick={() => { setDeleteRow(row); setShowDeleteConfirm(true); }}>Delete</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {(view === 'edit' || view === 'create') && (
        <div className="modal-overlay">
          <div className="modal-content">
            <h2>{view === 'create' ? 'Create New Row' : 'Edit Row'}</h2>
            <div className="form-fields">
              {columns.map(col => (
                <div key={col} className="form-field">
                  <label>{col}</label>
                  <input
                    type="text"
                    value={formData[col] || ''}
                    onChange={(e) => handleFormChange(col, e.target.value)}
                    disabled={col.toLowerCase().includes('id') && view === 'create'}
                  />
                </div>
              ))}
            </div>
            {error && <div className="error-message">{error}</div>}
            <div className="modal-actions">
              <button onClick={() => { setView('table'); setError(null); }}>Cancel</button>
              <button className="save-btn" onClick={handleSave}>Save</button>
            </div>
          </div>
        </div>
      )}

      {showDeleteConfirm && (
        <div className="modal-overlay">
          <div className="modal-content delete-confirm">
            <h2>Delete Row?</h2>
            <p>Are you sure you want to delete this row?</p>
            <p className="warning">This action cannot be undone.</p>
            <div className="modal-actions">
              <button onClick={() => { setShowDeleteConfirm(false); setDeleteRow(null); }}>Cancel</button>
              <button className="delete-btn" onClick={handleDelete}>Delete</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
