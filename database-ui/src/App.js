import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

const API_URL = process.env.REACT_APP_API_URL || 'https://secret-database-api.onrender.com/api';

function App() {
  const [tables, setTables] = useState([]);
  const [currentTable, setCurrentTable] = useState(null);
  const [tableData, setTableData] = useState([]);
  const [columns, setColumns] = useState([]);
  const [view, setView] = useState('login'); // 'login', 'folders', 'table', 'edit', 'create', 'files'
  const [editRow, setEditRow] = useState(null);
  const [formData, setFormData] = useState({});
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [deleteRow, setDeleteRow] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [codeInput, setCodeInput] = useState('');
  const [codeError, setCodeError] = useState('');
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [showHomePage, setShowHomePage] = useState(true);

  // File management states
  const [files, setFiles] = useState([]);
  const [currentFolder, setCurrentFolder] = useState('/');
  const [showNewFolderModal, setShowNewFolderModal] = useState(false);
  const [newFolderName, setNewFolderName] = useState('');
  const [uploadingFile, setUploadingFile] = useState(false);

  useEffect(() => {
    if (isAuthenticated) {
      loadTables();
    }
  }, [isAuthenticated]);

  // Auto-login with code from localStorage or URL
  useEffect(() => {
    // Check localStorage first (from game)
    const codeFromStorage = localStorage.getItem('access_code');
    let codeToUse = codeFromStorage;

    // Fallback to URL parameter
    if (!codeToUse) {
      const urlParams = new URLSearchParams(window.location.search);
      codeToUse = urlParams.get('code');
    }

    if (codeToUse && !isAuthenticated) {
      setCodeInput(codeToUse.toUpperCase());
      setShowHomePage(false);
      setView('login');

      // Auto-submit the code
      setTimeout(async () => {
        try {
          // First, store the code in the API (from game)
          await axios.post(`${API_URL}/store-code`, {
            code: codeToUse.trim().toUpperCase()
          });

          // Then verify it
          const response = await axios.post(`${API_URL}/verify-code`, {
            code: codeToUse.trim().toUpperCase()
          });

          if (response.data.valid) {
            setIsAuthenticated(true);
            setView('folders');
            // Clean URL and localStorage
            window.history.replaceState({}, document.title, "/");
            localStorage.removeItem('access_code');
          } else {
            setCodeError(response.data.message || 'Invalid code');
          }
        } catch (err) {
          setCodeError(err.response?.data?.message || 'Invalid code. Please try again.');
        }
      }, 500);
    }
  }, []);

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

  // File management functions
  const loadFiles = async (folder = '/') => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_URL}/files`, {
        params: { folder }
      });
      setFiles(response.data.files);
      setCurrentFolder(folder);
      setLoading(false);
    } catch (err) {
      setError('Failed to load files');
      setLoading(false);
    }
  };

  const handleCreateFolder = async () => {
    try {
      await axios.post(`${API_URL}/files/folder`, {
        name: newFolderName,
        parent_folder: currentFolder
      });
      setShowNewFolderModal(false);
      setNewFolderName('');
      loadFiles(currentFolder);
    } catch (err) {
      setError('Failed to create folder');
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setUploadingFile(true);
    const reader = new FileReader();

    reader.onload = async (e) => {
      try {
        const base64Data = e.target.result.split(',')[1]; // Remove data:...;base64, prefix

        await axios.post(`${API_URL}/files/upload`, {
          name: file.name,
          parent_folder: currentFolder,
          file_data: base64Data,
          mime_type: file.type,
          file_size: file.size
        });

        loadFiles(currentFolder);
      } catch (err) {
        setError('Failed to upload file');
      } finally {
        setUploadingFile(false);
      }
    };

    reader.readAsDataURL(file);
  };

  const handleDownloadFile = async (fileId, fileName) => {
    try {
      const response = await axios.get(`${API_URL}/files/${fileId}`);
      const { file_data, mime_type } = response.data;

      // Create blob from base64
      const byteCharacters = atob(file_data);
      const byteNumbers = new Array(byteCharacters.length);
      for (let i = 0; i < byteCharacters.length; i++) {
        byteNumbers[i] = byteCharacters.charCodeAt(i);
      }
      const byteArray = new Uint8Array(byteNumbers);
      const blob = new Blob([byteArray], { type: mime_type });

      // Download
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = fileName;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setError('Failed to download file');
    }
  };

  const handleDeleteFile = async (fileId) => {
    try {
      await axios.delete(`${API_URL}/files/${fileId}`);
      loadFiles(currentFolder);
    } catch (err) {
      setError('Failed to delete file');
    }
  };

  const openFolder = (folderName) => {
    const newPath = currentFolder === '/' ? `/${folderName}` : `${currentFolder}/${folderName}`;
    loadFiles(newPath);
    setView('files');
  };

  return (
    <div className="App">
      {showHomePage && (
        <div className="home-view">
          <div className="home-container">
            <div className="home-box">
              <h1>🎮 Secret Game</h1>
              <p className="home-description">
                Un jeu de plateforme 2D
              </p>

              <div className="home-options">
                <div className="option-card">
                  <div className="option-icon">🎮</div>
                  <h3>Jouer au jeu</h3>
                  <p>Jouez directement dans votre navigateur</p>
                  <a
                    href="/game/index.html"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="option-btn download-btn"
                  >
                    Jouer
                  </a>
                </div>

                <div className="option-card">
                  <div className="option-icon">🔒</div>
                  <h3>Accès sécurisé</h3>
                  <p>Vous avez un code d'accès? Entrez-le ici!</p>
                  <button
                    className="option-btn enter-btn"
                    onClick={() => {
                      setShowHomePage(false);
                      setView('login');
                    }}
                  >
                    Entrer le code
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {!showHomePage && view === 'login' && (
        <div className="login-view">
          <div className="login-container">
            <div className="login-box">
              <button
                className="back-to-home-btn"
                onClick={() => {
                  setShowHomePage(true);
                  setView('login');
                }}
              >
                ← Retour
              </button>
              <h1>🔒 Accès sécurisé</h1>
              <p className="login-description">
                Entrez votre code d'accès
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
              </form>
            </div>
          </div>
        </div>
      )}

      {view === 'folders' && (
        <div className="folders-view">
          <div className="header">
            <h1>BIENVENU MAX</h1>
            <div className="status">
              <span className="status-dot connected"></span>
              Connected
            </div>
          </div>
          <div className="folders-grid">
            <div className="folder-card" onClick={() => { loadFiles('/'); setView('files'); }}>
              <div className="folder-icon">
                <div style={{fontSize: '48px'}}>📁</div>
              </div>
              <div className="folder-name">FILES</div>
              <div className="folder-type">Storage</div>
            </div>
            {tables.map(table => (
              <div key={table} className="folder-card" onClick={() => loadTableData(table)}>
                <div className="folder-icon">
                  <svg viewBox="0 0 60 50" width="60" height="50">
                    <polygon points="0,10 20,10 25,0 60,0 60,10" fill="#0ff" />
                    <rect x="0" y="10" width="60" height="40" rx="3" fill="#0ff" />
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
            <span className="breadcrumb">Area / {currentTable}</span>
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

      {view === 'files' && (
        <div className="folders-view">
          <div className="header">
            <button className="back-btn" onClick={() => setView('folders')}>← BACK</button>
            <span className="breadcrumb">AREA / FILES {currentFolder !== '/' && `/ ${currentFolder}`}</span>
            <button className="new-btn" onClick={() => setShowNewFolderModal(true)}>+ NEW FOLDER</button>
            <label className="new-btn" style={{cursor: 'pointer', marginLeft: '10px'}}>
              {uploadingFile ? 'UPLOADING...' : '↑ UPLOAD FILE'}
              <input
                type="file"
                onChange={handleFileUpload}
                style={{display: 'none'}}
                disabled={uploadingFile}
              />
            </label>
          </div>
          <div className="folders-grid">
            {files.map(file => (
              <div key={file.id} className="folder-card">
                <div className="folder-icon" onClick={() => file.type === 'folder' ? openFolder(file.name) : null}>
                  <div style={{fontSize: '48px'}}>
                    {file.type === 'folder' ? '📁' : '📄'}
                  </div>
                </div>
                <div className="folder-name">{file.name}</div>
                <div className="folder-type">
                  {file.type === 'folder' ? 'Folder' : `${(file.file_size / 1024).toFixed(1)} KB`}
                </div>
                <div className="file-actions" style={{marginTop: '10px'}}>
                  {file.type === 'file' && (
                    <button
                      className="edit-btn"
                      onClick={() => handleDownloadFile(file.id, file.name)}
                      style={{fontSize: '12px', padding: '6px 12px'}}
                    >
                      DOWNLOAD
                    </button>
                  )}
                  <button
                    className="delete-btn"
                    onClick={() => handleDeleteFile(file.id)}
                    style={{fontSize: '12px', padding: '6px 12px', marginLeft: '5px'}}
                  >
                    DELETE
                  </button>
                </div>
              </div>
            ))}
            {files.length === 0 && (
              <div style={{gridColumn: '1 / -1', textAlign: 'center', color: '#0ff', padding: '40px', fontSize: '18px'}}>
                NO FILES OR FOLDERS
              </div>
            )}
          </div>
        </div>
      )}

      {showNewFolderModal && (
        <div className="modal-overlay">
          <div className="modal-content">
            <h2>CREATE NEW FOLDER</h2>
            <div className="form-fields">
              <div className="form-field">
                <label>FOLDER NAME</label>
                <input
                  type="text"
                  value={newFolderName}
                  onChange={(e) => setNewFolderName(e.target.value)}
                  placeholder="Enter folder name"
                  autoFocus
                />
              </div>
            </div>
            <div className="modal-actions">
              <button onClick={() => { setShowNewFolderModal(false); setNewFolderName(''); }}>CANCEL</button>
              <button className="save-btn" onClick={handleCreateFolder}>CREATE</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
