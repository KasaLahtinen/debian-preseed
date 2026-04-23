import React, { useState, useEffect } from 'react';
import htm from 'htm';

const html = htm.bind(React.createElement);

/**
 * PreseedForm - A dynamic form generator for Debian Preseed configuration.
 * 
 * @param {Array} data - The JSON output from the PreseedParser.
 * @param {Function} onSubmit - Callback function receiving the final configuration object.
 */
const PreseedForm = ({ data, onSubmit }) => {
    const [formData, setFormData] = useState({});

    // Initialize form data with default values from the parser
    useEffect(() => {
        const initialData = {};
        data.forEach(item => {
            if (item.key && item.value !== null) {
                // Handle multiselect defaults which might be comma separated
                if (item.type === 'multiselect' && typeof item.value === 'string') {
                    initialData[item.key] = item.value ? item.value.split(',').map(s => s.trim()) : [];
                } else {
                    initialData[item.key] = item.value;
                }
            }
        });
        setFormData(initialData);
    }, [data]);

    const handleChange = (key, value) => {
        setFormData(prev => ({ ...prev, [key]: value }));
    };

    const handleFormSubmit = (e) => {
        e.preventDefault();
        if (onSubmit) onSubmit(formData);
    };

    const renderField = (item) => {
        const { key, type, description, choices } = item;
        if (!key) return null;

        const label = html`<label htmlFor=${key} style=${{ display: 'block', fontWeight: 'bold', margin: '15px 0 5px' }}>${description || key}</label>`;

        switch (type) {
            case 'select':
            case 'boolean':
                return html`
                    <div key=${key} className="form-group">
                        ${label}
                        <select id=${key} value=${formData[key] || ''} onChange=${(e) => handleChange(key, e.target.value)}>
                            <option value="">-- Select an option --</option>
                            ${Array.isArray(choices) && choices.map(c => html`
                                <option key=${c} value=${c}>${c}</option>
                            `)}
                        </select>
                    </div>
                `;
            case 'multiselect':
                return html`
                    <div key=${key} className="form-group">
                        ${label}
                        <select multiple id=${key} value=${formData[key] || []} onChange=${(e) => {
                        const values = Array.from(e.target.selectedOptions, option => option.value);
                        handleChange(key, values);
                    }} size="5">
                            ${Array.isArray(choices) && choices.map(c => html`
                                <option key=${c} value=${c}>${c}</option>
                            `)}
                        </select>
                        <small style=${{ display: 'block', color: '#666' }}>Hold Ctrl (Cmd) to select multiple.</small>
                    </div>
                `;
            case 'password':
                return html`
                    <div key=${key} className="form-group">
                        ${label}
                        <input type="password" id=${key} value=${formData[key] || ''} onChange=${(e) => handleChange(key, e.target.value)} />
                    </div>
                `;
            case 'note':
                return html`<div key=${key} style=${{ fontStyle: 'italic', color: '#555', padding: '10px', background: '#f9f9f9', borderLeft: '4px solid #ccc', marginTop: '10px' }}>${description}</div>`;
            default:
                return html`
                    <div key=${key} className="form-group">
                        ${label}
                        <input type="text" id=${key} value=${formData[key] || ''} onChange=${(e) => handleChange(key, e.target.value)} placeholder=${item.value} />
                    </div>
                `;
        }
    };

    // Group items by their 'group' property
    const groupedData = data.reduce((acc, item) => {
        const group = item.group || 'General';
        if (!acc[group]) acc[group] = [];
        acc[group].push(item);
        return acc;
    }, {});

    return html`
        <form onSubmit={handleFormSubmit} className="preseed-form">
            ${Object.entries(groupedData).map(([groupName, items]) => html`
                <fieldset key=${groupName} style=${{ border: '1px solid #ddd', padding: '20px', marginBottom: '30px', borderRadius: '8px' }}>
                    <legend style=${{ padding: '0 10px', fontWeight: 'bold', fontSize: '1.2em', color: '#333' }}>
                        ${groupName}
                    </legend>
                    ${items.map(renderField)}
                </fieldset>
            `)}
            <hr style=${{ margin: '20px 0' }} />
            <button type="submit" style=${{ padding: '10px 20px', cursor: 'pointer' }}>Generate Configuration</button>
        </form>
    `;
};

export default PreseedForm;
