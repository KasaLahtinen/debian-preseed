import React, { useState } from 'react';
import PreseedForm from './PreseedForm.jsx';

/**
 * PreseedLandingPage - A workspace to test and generate preseed forms.
 */
const PreseedLandingPage = () => {
    const [jsonInput, setJsonInput] = useState('');
    const [preseedData, setPreseedData] = useState(null);
    const [error, setError] = useState(null);
    const [finalConfig, setFinalConfig] = useState(null);

    const handleGenerate = () => {
        try {
            const parsed = JSON.parse(jsonInput);
            if (!Array.isArray(parsed)) {
                throw new Error("Parsed JSON must be an array of preseed items.");
            }
            setPreseedData(parsed);
            setError(null);
            setFinalConfig(null);
        } catch (err) {
            setError(`Failed to parse JSON: ${err.message}`);
            setPreseedData(null);
        }
    };

    const handleFormSubmit = (formData) => {
        setFinalConfig(formData);
    };

    return (
        <div style={{ maxWidth: '1000px', margin: '40px auto', padding: '20px', fontFamily: 'system-ui, sans-serif' }}>
            <header style={{ borderBottom: '1px solid #eee', marginBottom: '30px', paddingBottom: '10px' }}>
                <h1 style={{ margin: 0 }}>Debian Preseed Form Designer</h1>
                <p style={{ color: '#666' }}>Paste the JSON output from <code>parser.py</code> to generate your dynamic UI.</p>
            </header>

            <section style={{ marginBottom: '40px' }}>
                <label style={{ fontWeight: 'bold', display: 'block', marginBottom: '10px' }}>1. Parser Output (JSON Array):</label>
                <textarea
                    rows="10"
                    style={{
                        width: '100%',
                        padding: '12px',
                        fontSize: '14px',
                        fontFamily: 'monospace',
                        border: '1px solid #ccc',
                        borderRadius: '6px',
                        backgroundColor: '#f8fafc',
                        boxSizing: 'border-box'
                    }}
                    placeholder='[{"key": "debian-installer/locale", "type": "string", ...}, ...]'
                    value={jsonInput}
                    onChange={(e) => setJsonInput(e.target.value)}
                />
                <button
                    onClick={handleGenerate}
                    style={{
                        marginTop: '15px',
                        padding: '12px 24px',
                        backgroundColor: '#2563eb',
                        color: 'white',
                        border: 'none',
                        borderRadius: '6px',
                        cursor: 'pointer',
                        fontWeight: '600'
                    }}
                >
                    Generate Form View
                </button>
                {error && <div style={{ marginTop: '15px', color: '#dc2626', fontSize: '0.9rem' }}>{error}</div>}
            </section>

            {preseedData && (
                <section style={{ marginBottom: '40px' }}>
                    <h2 style={{ fontSize: '1.25rem', marginBottom: '20px' }}>2. Interactive Form Preview:</h2>
                    <div style={{ backgroundColor: '#fff', padding: '25px', borderRadius: '12px', border: '1px solid #e2e8f0', boxShadow: '0 1px 3px 0 rgb(0 0 0 / 0.1)' }}>
                        <PreseedForm data={preseedData} onSubmit={handleFormSubmit} />
                    </div>
                </section>
            )}

            {finalConfig && (
                <section style={{ marginTop: '40px' }}>
                    <h2 style={{ fontSize: '1.25rem', marginBottom: '10px' }}>3. Generated <code>preseed.cfg</code> Snippet:</h2>
                    <pre style={{ backgroundColor: '#1e293b', color: '#f1f5f9', padding: '20px', borderRadius: '8px', overflowX: 'auto', fontSize: '14px' }}>
                        {Object.entries(finalConfig)
                            .filter(([_, value]) => value !== '' && value !== null)
                            .map(([key, value]) => `d-i ${key} ${Array.isArray(value) ? value.join(', ') : value}`)
                            .join('\n')}
                    </pre>
                </section>
            )}
        </div>
    );
};

export default PreseedLandingPage;
