const API_BASE_URL = 'http://localhost:8000/api';

// DOM Elements
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const chatMessages = document.getElementById('chat-messages');
const resultsContainer = document.getElementById('results-container');
const sqlCode = document.getElementById('sql-code');
const resultsTable = document.getElementById('results-table');
const loadingDiv = document.getElementById('loading');
const loadingMessage = document.getElementById('loading-message');
const rowCount = document.getElementById('row-count');
const executionTime = document.getElementById('execution-time');
const cacheStatus = document.getElementById('cache-status');
const cacheSize = document.getElementById('cache-size');

// Enter key to send
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendQuery();
    }
});

// Send query to backend using SSE streaming
async function sendQuery() {
    const question = userInput.value.trim();
    
    if (!question) {
        alert('Please enter a question');
        return;
    }
    
    // Add user message to chat
    addMessage(question, 'user-message');
    
    // Clear input
    userInput.value = '';
    
    // Show loading
    showLoading('Connecting to server...');
    hideResults();
    disableInput(true);
    
    try {
        // Use EventSource for SSE streaming
        const eventSource = new EventSource(
            `${API_BASE_URL}/query/stream?` + new URLSearchParams({
                question: question
            }).toString()
        );
        
        // But EventSource doesn't support POST, so we'll use fetch with streaming
        const response = await fetch(`${API_BASE_URL}/query/stream`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'text/event-stream',
            },
            body: JSON.stringify({ question })
        });
        
        if (!response.ok) {
            throw new Error('Failed to connect to streaming endpoint');
        }
        
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let accumulatedSQL = '';
        
        while (true) {
            const { done, value } = await reader.read();
            
            if (done) break;
            
            const chunk = decoder.decode(value);
            const lines = chunk.split('\n');
            
            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    const data = JSON.parse(line.substring(6));
                    await handleStreamEvent(data, accumulatedSQL);
                } else if (line.startsWith('event: ')) {
                    const eventType = line.substring(7);
                    // Handle different event types
                    console.log('Event:', eventType);
                }
            }
        }
        
    } catch (error) {
        console.error('Streaming error:', error);
        // Fallback to non-streaming endpoint
        await sendQueryFallback(question);
    } finally {
        hideLoading();
        disableInput(false);
        updateCacheStats();
    }
}

// Handle streaming events
async function handleStreamEvent(data, accumulatedSQL) {
    if (data.event === 'progress') {
        updateLoadingMessage(data.data.message);
    } else if (data.event === 'sql_token') {
        // Show SQL as it's being generated
        const eventData = typeof data.data === 'string' ? JSON.parse(data.data) : data.data;
        accumulatedSQL = eventData.accumulated;
        if (sqlCode) {
            sqlCode.textContent = accumulatedSQL;
            resultsContainer.style.display = 'block';
        }
    } else if (data.event === 'sql_complete') {
        const eventData = typeof data.data === 'string' ? JSON.parse(data.data) : data.data;
        updateLoadingMessage('SQL generated! Executing...');
    } else if (data.event === 'complete') {
        const eventData = typeof data.data === 'string' ? JSON.parse(data.data) : data.data;
        displayResults(eventData);
        addMessage(`✅ Query executed! Found ${eventData.results.row_count} rows in ${eventData.execution_time.toFixed(2)}s`, 'assistant-message');
    } else if (data.event === 'error') {
        const eventData = typeof data.data === 'string' ? JSON.parse(data.data) : data.data;
        addMessage(`❌ Error: ${eventData.message}`, 'error-message');
        hideResults();
    }
}

// Fallback to non-streaming endpoint
async function sendQueryFallback(question) {
    showLoading('Analyzing your question...');
    
    try {
        // Update loading message
        setTimeout(() => updateLoadingMessage('Finding relevant tables...'), 500);
        setTimeout(() => updateLoadingMessage('Generating SQL query...'), 1500);
        setTimeout(() => updateLoadingMessage('Executing query...'), 3000);
        
        // Call API
        const response = await fetch(`${API_BASE_URL}/query`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ question })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Query failed');
        }
        
        const data = await response.json();
        
        // Display results
        displayResults(data);
        
        // Add success message to chat
        addMessage(`✅ Query executed successfully! Found ${data.results.row_count} rows.`, 'assistant-message');
        
    } catch (error) {
        console.error('Error:', error);
        addMessage(`❌ Error: ${error.message}`, 'error-message');
        hideResults();
    }
}

// Display query results
function displayResults(data) {
    // Show results container
    resultsContainer.style.display = 'block';
    
    // Display SQL
    sqlCode.textContent = data.sql;
    
    // Display execution stats
    executionTime.textContent = `⏱️ Execution Time: ${data.execution_time.toFixed(2)}s`;
    cacheStatus.textContent = data.cached ? '💾 Cached Result' : '🔄 Fresh Query';
    cacheStatus.style.background = data.cached ? '#4caf50' : '#ff9800';
    cacheStatus.style.color = 'white';
    cacheStatus.style.padding = '5px 10px';
    cacheStatus.style.borderRadius = '5px';
    
    // Display row count
    rowCount.textContent = `${data.results.row_count} rows`;
    
    // Build table
    buildTable(data.results);
    
    // Scroll to results
    resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Build HTML table from results
function buildTable(results) {
    const { columns, rows } = results;
    
    if (!rows || rows.length === 0) {
        resultsTable.innerHTML = '<p style="padding: 20px; text-align: center;">No results found</p>';
        return;
    }
    
    // Build table HTML
    let html = '<thead><tr>';
    columns.forEach(col => {
        html += `<th>${col}</th>`;
    });
    html += '</tr></thead><tbody>';
    
    rows.forEach(row => {
        html += '<tr>';
        columns.forEach(col => {
            const value = row[col];
            html += `<td>${value !== null && value !== undefined ? value : '-'}</td>`;
        });
        html += '</tr>';
    });
    
    html += '</tbody>';
    resultsTable.innerHTML = html;
}

// Add message to chat
function addMessage(text, className) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${className}`;
    messageDiv.textContent = text;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Show/hide loading
function showLoading(message) {
    loadingDiv.style.display = 'block';
    loadingMessage.textContent = message;
}

function hideLoading() {
    loadingDiv.style.display = 'none';
}

function updateLoadingMessage(message) {
    loadingMessage.textContent = message;
}

// Show/hide results
function hideResults() {
    resultsContainer.style.display = 'none';
}

// Enable/disable input
function disableInput(disabled) {
    userInput.disabled = disabled;
    sendBtn.disabled = disabled;
}

// Copy SQL to clipboard
function copySQL() {
    const sql = sqlCode.textContent;
    navigator.clipboard.writeText(sql).then(() => {
        alert('SQL copied to clipboard!');
    });
}

// Clear chat
function clearChat() {
    chatMessages.innerHTML = `
        <div class="message system-message">
            Chat cleared. Ask a new question!
        </div>
    `;
    hideResults();
}

// Clear cache
async function clearCache() {
    try {
        const response = await fetch(`${API_BASE_URL}/cache/clear`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            alert('Cache cleared successfully!');
            updateCacheStats();
        }
    } catch (error) {
        console.error('Error clearing cache:', error);
        alert('Failed to clear cache');
    }
}

// Update cache stats
async function updateCacheStats() {
    try {
        const response = await fetch(`${API_BASE_URL}/cache/stats`);
        const data = await response.json();
        cacheSize.textContent = `${data.size}/${data.max_size} (${data.hit_rate} hit rate)`;
    } catch (error) {
        console.error('Error fetching cache stats:', error);
    }
}

// Initialize on page load
window.addEventListener('load', () => {
    updateCacheStats();
    userInput.focus();
});
