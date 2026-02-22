import { Link } from 'react-router-dom';

const features = [
    {
        icon: '🎙',
        title: 'Studio-Quality Voices',
        desc: 'Choose from 25+ realistic AI voices trained on professional studio recordings.',
    },
    {
        icon: '⚡',
        title: 'Lightning Fast',
        desc: 'Get your audio back in seconds. Our optimised inference engine runs on dedicated GPU clusters.',
    },
    {
        icon: '🎛',
        title: 'Full Control',
        desc: 'Fine-tune speed, pitch, and target duration. Inline voice tags let you mix speakers in a single script.',
    },
    {
        icon: '📁',
        title: 'History & Storage',
        desc: 'Every generation is saved to your account. Replay, download, or share your audio anytime.',
    },
    {
        icon: '🔒',
        title: 'Private & Secure',
        desc: 'Your scripts never leave our encrypted infrastructure. Data is isolated per account.',
    },
    {
        icon: '🛠',
        title: 'REST API',
        desc: 'Integrate voice generation directly into your product with our developer-friendly API.',
    },
];

export default function Home() {
    return (
        <div className="home-page animate-fade">

            {/* ── Navbar ── */}
            <nav className="home-nav">
                <div className="home-nav-brand">
                    VoiceGen Pro
                </div>
                <div className="home-nav-actions">
                    <Link to="/login" className="btn btn-ghost" style={{ textDecoration: 'none', fontSize: '0.875rem' }}>
                        Login
                    </Link>
                    <Link to="/register" className="btn btn-primary" style={{ textDecoration: 'none', fontSize: '0.875rem', padding: '0.6rem 1.25rem' }}>
                        Get Started
                    </Link>
                </div>
            </nav>

            {/* ── Hero ── */}
            <section className="hero-section">
                <div className="hero-tag">
                    <span className="pulse"></span>
                    AI-Powered Voice Generation
                </div>

                <h1 className="hero-title">
                    Transform text into{' '}
                    <span className="gradient-text">lifelike speech</span>
                </h1>

                <p className="hero-subtitle">
                    Professional AI voices for content creators, developers, and businesses.
                    Generate natural-sounding audio from any script in seconds.
                </p>

                <div className="hero-actions">
                    <Link
                        to="/register"
                        className="btn btn-primary"
                        style={{ textDecoration: 'none', padding: '0.875rem 2rem', fontSize: '0.95rem', borderRadius: '14px' }}
                    >
                        Start for free →
                    </Link>
                    <Link
                        to="/login"
                        className="btn btn-ghost"
                        style={{ textDecoration: 'none', padding: '0.875rem 2rem', fontSize: '0.95rem', borderRadius: '14px' }}
                    >
                        Sign in
                    </Link>
                </div>

                <div className="hero-stats">
                    <div className="hero-stat">
                        <span className="hero-stat-value">25+</span>
                        <span className="hero-stat-label">Voices</span>
                    </div>
                    <div style={{ width: '1px', height: '32px', background: 'var(--border)' }} />
                    <div className="hero-stat">
                        <span className="hero-stat-value">&lt; 15s</span>
                        <span className="hero-stat-label">Generation</span>
                    </div>
                    <div style={{ width: '1px', height: '32px', background: 'var(--border)' }} />
                    <div className="hero-stat">
                        <span className="hero-stat-value">HD</span>
                        <span className="hero-stat-label">Audio Quality</span>
                    </div>
                </div>
            </section>

            {/* ── Features ── */}
            <section className="features-section">
                <p className="features-label">Features</p>
                <h2 className="features-heading">Everything you need</h2>
                <p className="features-subheading">
                    A complete voice generation platform built for speed, quality, and developer experience.
                </p>

                <div className="features-grid">
                    {features.map((f) => (
                        <div key={f.title} className="feature-card">
                            <div className="feature-icon">{f.icon}</div>
                            <h3 className="feature-title">{f.title}</h3>
                            <p className="feature-desc">{f.desc}</p>
                        </div>
                    ))}
                </div>
            </section>

            {/* ── CTA ── */}
            <section className="home-cta-section">
                <div className="cta-card">
                    <h2 className="cta-title">
                        Ready to <span className="gradient-text">get started?</span>
                    </h2>
                    <p className="cta-subtitle">
                        Create your free account and generate your first voice in under a minute.
                    </p>
                    <div className="cta-actions">
                        <Link
                            to="/register"
                            className="btn btn-primary"
                            style={{ textDecoration: 'none', padding: '0.875rem 2rem', borderRadius: '14px' }}
                        >
                            Create free account
                        </Link>
                        <Link
                            to="/login"
                            className="btn btn-ghost"
                            style={{ textDecoration: 'none', padding: '0.875rem 2rem', borderRadius: '14px' }}
                        >
                            Sign in
                        </Link>
                    </div>
                </div>
            </section>

        </div>
    );
}
