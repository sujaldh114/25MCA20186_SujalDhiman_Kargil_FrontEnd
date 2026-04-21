import { useState } from 'react'
import './App.css'

function App() {
  const [notes, setNotes] = useState([])
  const [inputValue, setInputValue] = useState('')
  const [editingId, setEditingId] = useState(null)

  const handleAddNote = () => {
    if (inputValue.trim() === '') {
      alert('Please enter a note')
      return
    }

    if (editingId !== null) {
      // Update existing note
      setNotes(notes.map(note =>
        note.id === editingId ? { ...note, text: inputValue } : note
      ))
      setEditingId(null)
    } else {
      // Add new note
      const newNote = {
        id: Date.now(),
        text: inputValue
      }
      setNotes([...notes, newNote])
    }
    setInputValue('')
  }

  const handleDelete = (id) => {
    setNotes(notes.filter(note => note.id !== id))
    if (editingId === id) {
      setEditingId(null)
      setInputValue('')
    }
  }

  const handleUpdate = (note) => {
    setInputValue(note.text)
    setEditingId(note.id)
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleAddNote()
    }
  }

  return (
    <div className="app-container">
      <div className="note-app">
        <h1>My Notes</h1>
        
        <div className="input-section">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Enter your note..."
            className="note-input"
          />
          <button onClick={handleAddNote} className="add-btn">
            {editingId !== null ? 'Update' : 'Add'}
          </button>
        </div>

        <div className="notes-list">
          {notes.length === 0 ? (
            <p className="no-notes">No notes yet. Add one to get started!</p>
          ) : (
            notes.map(note => (
              <div key={note.id} className="note-item">
                <p className="note-text">{note.text}</p>
                <div className="button-group">
                  <button
                    onClick={() => handleUpdate(note)}
                    className="update-btn"
                  >
                    Update
                  </button>
                  <button
                    onClick={() => handleDelete(note.id)}
                    className="delete-btn"
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  )
}

export default App
