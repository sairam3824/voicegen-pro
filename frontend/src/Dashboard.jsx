import { useState, useEffect, useRef } from 'react'
import { useAuth } from './AuthContext'

const API_BASE = 'http://localhost:8000';

function Dashboard() {
    const { token, user, logout } = useAuth();
    const [text, setText] = useState('');
    const [duration, setDuration] = useState(0);
    const [speaker, setSpeaker] = useState('p226');
    const [voices, setVoices] = useState([]);
    const [loading, setLoading] = useState(false);
    const [audioUrl, setAudioUrl] = useState(null);
    const [error, setError] = useState(null);
    const [playingDemo, setPlayingDemo] = useState(null);
    const [generations, setGenerations] = useState([]);
    const audioRef = useRef(new Audio());

    useEffect(() => {
        fetch(`${API_BASE}/voices`, {
            headers: { Authorization: `Bearer ${token}` }
        })
            .then(res => res.json())
            .then(data => setVoices(data.voices))
            .catch(err => console.error("Failed to load voices", err));

        fetchGenerations();

        return () => { audioRef.current.pause(); };
    }, [token]);

    const fetchGenerations = async () => {
        try {
            const res = await fetch(`${API_BASE}/generations`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            if (res.ok) {
                const data = await res.json();
                setGenerations(data);
            }
        } catch (err) {
            console.error("Failed to load generations", err);
        }
    };

    const handleGenerate = async () => {
        if (!text.trim()) { setError("Please enter some text first."); return; }
        setLoading(true);
        setError(null);
        setAudioUrl(null);
        try {
            const response = await fetch(`${API_BASE}/generate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
                body: JSON.stringify({ text, target_duration: parseFloat(duration) || 0, speaker }),
            });
            if (!response.ok) throw new Error('Generation failed. Please try again.');
            const data = await response.json();
            setAudioUrl(`${API_BASE}${data.url}`);
            fetchGenerations();
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const playDemo = (url, id) => {
        if (playingDemo === id) {
            audioRef.current.pause();
            setPlayingDemo(null);
        } else {
            audioRef.current.src = `${API_BASE}${url}`;
            audioRef.current.play();
            setPlayingDemo(id);
            audioRef.current.onended = () => setPlayingDemo(null);
        }
    };

    const selectedVoice = voices.find(v => v.id === speaker);

    return (
        <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>

            {/* ── Navbar ── */}
            <header className="navbar">
                <div className="navbar-brand">
                    VoiceGen Pro
                </div>
                <div className="navbar-right">
                    <div className="user-badge">
                        <span className="dot" />
                        {user?.email}
                    </div>
                    <button
                        onClick={logout}
                        className="btn btn-ghost"
                        style={{ padding: '0.45rem 1rem', fontSize: '0.8rem', borderRadius: '8px' }}
                    >
                        Sign out
                    </button>
                </div>
            </header>

            {/* ── Main Content ── */}
            <main className="app-container animate-fade" style={{ paddingTop: '2rem' }}>

                {/* Page heading */}
                <div style={{ marginBottom: '1.5rem' }}>
                    <h1 style={{ fontSize: '1.6rem', fontWeight: 700, letterSpacing: '-0.03em', marginBottom: '0.35rem' }}>
                        Voice Studio
                    </h1>
                    <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
                        Convert your scripts into lifelike speech with AI precision.
                    </p>
                </div>

                <div className="main-grid">

                    {/* ── Script Editor ── */}
                    <div className="card">
                        <p className="section-title">
                            <span className="icon">✏</span>
                            Script Editor
                        </p>
                        <div className="script-editor-wrapper">
                            <textarea
                                className="script-textarea"
                                placeholder={"Type or paste your script here…\n\nTip: Use [Voice: p226] tags to switch speakers mid-script."}
                                value={text}
                                onChange={(e) => setText(e.target.value)}
                            />
                            <span className="char-count">{text.length} chars</span>
                        </div>

                        {/* Audio result sits below the editor */}
                        {audioUrl && (
                            <div className="audio-result">
                                <div className="audio-result-label">
                                    <span>✓</span> Generation complete
                                </div>
                                <audio controls src={audioUrl} />
                                <div>
                                    <a href={audioUrl} download className="download-link">
                                        ↓ Download WAV
                                    </a>
                                </div>
                            </div>
                        )}
                    </div>

                    {/* ── Configuration ── */}
                    <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: 0, height: 'fit-content' }}>

                        <p className="section-title">
                            <span className="icon">⚙</span>
                            Configuration
                        </p>

                        {/* Voice Picker */}
                        <div style={{ marginBottom: '1.5rem' }}>
                            <label>Voice</label>
                            {selectedVoice && (
                                <div className="badge" style={{ marginBottom: '0.75rem' }}>
                                    🎙 {selectedVoice.name}
                                </div>
                            )}
                            <div className="voice-grid">
                                {voices.map(v => (
                                    <div
                                        key={v.id}
                                        className={`voice-item ${speaker === v.id ? 'selected' : ''}`}
                                        onClick={() => setSpeaker(v.id)}
                                    >
                                        <div className="voice-info">
                                            <div className="voice-avatar">{v.id.substring(1)}</div>
                                            <span className="voice-name">{v.name}</span>
                                        </div>
                                        {v.demo_url && (
                                            <button
                                                className={`play-btn ${playingDemo === v.id ? 'playing' : ''}`}
                                                onClick={(e) => { e.stopPropagation(); playDemo(v.demo_url, v.id); }}
                                            >
                                                {playingDemo === v.id ? '■ Stop' : '▶ Play'}
                                            </button>
                                        )}
                                    </div>
                                ))}
                                {voices.length === 0 && (
                                    <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', padding: '1rem 0' }}>
                                        Loading voices…
                                    </p>
                                )}
                            </div>
                        </div>

                        {/* Duration */}
                        <div style={{ marginBottom: '1rem' }}>
                            <label>Target Duration (seconds)</label>
                            <input
                                type="number"
                                placeholder="0 — natural speed"
                                value={duration}
                                onChange={(e) => setDuration(e.target.value)}
                                min="0"
                                step="0.5"
                            />
                        </div>

                        {error && (
                            <div className="error-msg">
                                <span>⚠</span> {error}
                            </div>
                        )}

                        <button
                            onClick={handleGenerate}
                            disabled={loading}
                            className="generate-btn"
                            style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem' }}
                        >
                            {loading && <span className="spinner" />}
                            {loading ? 'Generating…' : 'Generate Voice'}
                        </button>
                    </div>
                </div>

                {/* ── History ── */}
                <div className="card" style={{ marginTop: '1.5rem' }}>
                    <p className="section-title">
                        <span className="icon">📜</span>
                        History
                    </p>
                    <div className="history-list">
                        {generations.map(gen => (
                            <div key={gen.id} className="history-item">
                                <div className="history-meta">
                                    <span className="history-time">
                                        {new Date(gen.created_at).toLocaleString(undefined, {
                                            month: 'short', day: 'numeric',
                                            hour: '2-digit', minute: '2-digit'
                                        })}
                                    </span>
                                    <span className="history-text">
                                        {gen.original_text.substring(0, 80)}{gen.original_text.length > 80 ? '…' : ''}
                                    </span>
                                </div>
                                <a
                                    href={`${API_BASE}/download/${gen.filename}`}
                                    target="_blank"
                                    rel="noreferrer"
                                    className="history-download"
                                >
                                    ↓ WAV
                                </a>
                            </div>
                        ))}
                        {generations.length === 0 && (
                            <div className="empty-state">
                                No generations yet. Create your first voice above.
                            </div>
                        )}
                    </div>
                </div>

            </main>
        </div>
    );
}

export default Dashboard;
