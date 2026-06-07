document.addEventListener("DOMContentLoaded", () => {
    
    // --- 1. GLOBAL STATE ---
    let currentUser = null; 
    let previousGuestId = null; 

    // DOM Elements
    const fullHistory = document.getElementById('full-history');
    const currentChat = document.getElementById('current-chat');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const predictBtn = document.getElementById('predict-btn');

    // --- 2. INITIALIZATION & NAVIGATION ---
    const navTabs = document.querySelectorAll('.nav-tab');
    const viewSections = document.querySelectorAll('.view-section');

    navTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            if(tab.id === 'nav-login-btn') return; // Handled separately
            
            navTabs.forEach(t => t.classList.remove('active'));
            viewSections.forEach(v => v.classList.remove('active'));
            
            tab.classList.add('active');
            const targetId = tab.getAttribute('data-target');
            if(targetId) document.getElementById(targetId).classList.add('active');
        });
    });

    // --- 3. CLIENT-SIDE AUTHENTICATION GATEWAY ---
    const loginOverlay = document.getElementById('login-overlay');
    
    document.getElementById('nav-login-btn')?.addEventListener('click', () => {
        loginOverlay.style.display = 'flex';
    });

    document.getElementById('login-btn')?.addEventListener('click', () => {
        const user = document.getElementById('username-input').value.trim().toLowerCase();
        if (user) {
            handleUserMerge(user);
            loginOverlay.style.display = 'none'; 
            
            // --- NEW: Update Navbar UI ---
            const navLogin = document.getElementById('nav-login-btn');
            const navLogout = document.getElementById('nav-logout-btn');
            
            if(navLogin) {
                navLogin.innerHTML = `👤 ${user}`;
                navLogin.style.pointerEvents = 'none'; // Locks the login button
            }
            if(navLogout) {
                navLogout.style.display = 'block'; // Un-hides the logout button
            }
            
            document.getElementById('username-input').value = ''; 
        }
    });

    document.getElementById('guest-btn')?.addEventListener('click', () => {
        const uniqueId = Math.random().toString(36).substring(2, 6);
        currentUser = `guest_${uniqueId}`; 
        previousGuestId = currentUser; 
        
        loginOverlay.style.display = 'none'; 
        
        // --- NEW: Update Navbar UI ---
        const navLogin = document.getElementById('nav-login-btn');
        const navLogout = document.getElementById('nav-logout-btn');
        
        if(navLogin) {
            navLogin.innerHTML = `👤 Guest-${uniqueId}`;
            navLogin.style.pointerEvents = 'auto'; // Locks the login button
        }
        if(navLogout) {
            navLogout.style.display = 'block'; // Un-hides the logout button
        }
        
        loadUserHistory(); 
    });

    function handleUserMerge(newUser) {
        if (previousGuestId && previousGuestId.startsWith('guest_')) {
            const guestHistory = localStorage.getItem(`lawbit_history_${previousGuestId}`);
            if (guestHistory && guestHistory.includes('history-card')) {
                let existingUserHistory = localStorage.getItem(`lawbit_history_${newUser}`) || '';
                const emptyTextHTML = '<p id="empty-history-text" style="color: #b3b3b3; font-style: italic;">No secure history found for this user.</p>';
                
                existingUserHistory = existingUserHistory.replace(emptyTextHTML, '');
                const cleanGuestHistory = guestHistory.replace(emptyTextHTML, '');
                
                localStorage.setItem(`lawbit_history_${newUser}`, existingUserHistory + cleanGuestHistory);
            }
            localStorage.removeItem(`lawbit_history_${previousGuestId}`);
            previousGuestId = null;
        }
        currentUser = newUser;
        loadUserHistory();
    }

    function loadUserHistory() {
        const savedHistory = localStorage.getItem(`lawbit_history_${currentUser}`);
        if (savedHistory) {
            fullHistory.innerHTML = savedHistory;
        } else {
            fullHistory.innerHTML = '<p id="empty-history-text" style="color: #b3b3b3; font-style: italic;">No secure history found for this user.</p>';
        }
    }

    // --- 4. CHATBOT ENGINE ---
    async function sendMessage() {
        const text = userInput.value.trim();
        if (!text) return;

        const emptyText = document.getElementById('empty-history-text');
        if (emptyText) emptyText.style.display = 'none';

        // 1. Render User Message
        currentChat.innerHTML += `<div class="message user-message"><p>${text}</p></div>`;
        userInput.value = ''; 
        currentChat.scrollTop = currentChat.scrollHeight;

        // 2. Show Typing Indicator
        const typingId = 'typing-' + Date.now();
        currentChat.innerHTML += `
            <div id="${typingId}" class="typing-indicator">
                <div class="dot"></div><div class="dot"></div><div class="dot"></div>
            </div>`;
        currentChat.scrollTop = currentChat.scrollHeight;

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query: text })
            });
            const data = await response.json();

            // 3. Remove Indicator & Render Bot Message
            document.getElementById(typingId)?.remove();

            const formattedResponse = data.response
                .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                .replace(/\n/g, '<br>');

            const verifiedBadge = data.verified ? '✅ Verified Secure' : '❌ Unverified';
            const botHtml = `
                <div class="message ai-message">
                    <p style="line-height: 1.6;">${formattedResponse}</p>
                    <small style="color: #4ade80; display: block; margin-top: 15px; font-size: 0.75rem; border-top: 1px solid rgba(74, 222, 128, 0.3); padding-top: 8px;">
                        ${verifiedBadge} | Sig: ${data.signature}
                    </small>
                </div>`;
            
            currentChat.innerHTML += botHtml;
            
            // 4. Save to Encrypted Vault (History Tab)
            const timestamp = new Date().toLocaleString(); 
            const shortQuery = text.length > 30 ? text.substring(0, 30) + '...' : text;
            
            const historyCard = `
                <div class="history-card">
                    <div class="history-header" onclick="this.nextElementSibling.classList.toggle('open')">
                        <span>Query: "${shortQuery}"</span>
                        <span class="timestamp">${timestamp}</span>
                    </div>
                    <div class="history-body">
                        <div class="history-query"><strong>Full Query:</strong> ${text}</div>
                        ${botHtml}
                    </div>
                </div>`;
            
            fullHistory.innerHTML += historyCard; 
            localStorage.setItem(`lawbit_history_${currentUser}`, fullHistory.innerHTML);
            
            // 5. Auto-Scroll to the exact message
            const allAiMessages = currentChat.querySelectorAll('.ai-message');
            allAiMessages[allAiMessages.length - 1]?.scrollIntoView({ behavior: "smooth", block: "start" });

        } catch (error) {
            document.getElementById(typingId)?.remove();
            console.error("Error communicating with server:", error);
        }
    }

    sendBtn?.addEventListener('click', sendMessage);
    userInput?.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // --- 5. FHE PREDICTOR ENGINE ---
    predictBtn?.addEventListener('click', async () => {
        const winPercentage = document.getElementById('win-percentage');
        winPercentage.innerText = "Encrypting..."; 
        
        const payload = {
            evidence: document.getElementById('evidence').value,
            complexity: document.getElementById('complexity').value,
            precedent: document.getElementById('precedent').value
        };

        try {
            const response = await fetch('/api/predict', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const data = await response.json();
            winPercentage.innerText = `${data.win_probability}%`;
        } catch (error) {
            winPercentage.innerText = "Error";
        }
    });

    // --- 6. CLEANUP CONTROLS ---
    document.getElementById('clear-chat-btn')?.addEventListener('click', () => {
        if (confirm("Clear the active chat? This won't delete your saved history.")) {
            currentChat.innerHTML = ''; 
        }
    });

    document.getElementById('clear-history-btn')?.addEventListener('click', () => {
        if (confirm("WARNING: This will permanently delete your encrypted case history. Proceed?")) {
            localStorage.removeItem(`lawbit_history_${currentUser}`);
            fullHistory.innerHTML = '<p id="empty-history-text" style="color: #b3b3b3; font-style: italic;">No secure history found for this user.</p>';
        }
    });
});

// =========================================================
// 7. SECURE PDF GENERATION (Global Scope)
// =========================================================
async function generateSecureReport() {
    const sessionCheck = await fetch('/api/check-session');
    const sessionData = await sessionCheck.json();

    if (!sessionData.logged_in) {
        alert("Authentication required. Please log in to download encrypted reports.");
        openAuthModal(); 
        return; 
    }

    // FIX: Use innerHTML to preserve line breaks and formatting in the PDF
    const chatElement = document.getElementById("current-chat");
    const chatHistoryHtml = chatElement ? chatElement.innerHTML : "<p>No consultation history available.</p>";

    const predictionElement = document.getElementById("prediction-result");
    const predictionResult = predictionElement ? predictionElement.innerText.replace("🔒 Calculated in the dark. Raw data never exposed to server.", "").trim() : "No prediction run yet.";

    const reportContainer = document.createElement("div");
    reportContainer.style.padding = "40px";
    reportContainer.style.fontFamily = "Arial, sans-serif";
    reportContainer.style.color = "#333";

    reportContainer.innerHTML = `
        <h1 style="color: #2c3e50; border-bottom: 2px solid #2c3e50; padding-bottom: 10px;">LawBit: Secure Case Evaluation</h1>
        <p><strong>Generated on:</strong> ${new Date().toLocaleString()}</p>
        <p style="color: #e74c3c; font-size: 12px;">🔒 <em>Zero-Trust Verified: Server has retained zero plaintext records of this evaluation.</em></p>

        <h2 style="margin-top: 30px; color: #34495e;">1. FHE Encrypted Prediction</h2>
        <div style="background: #f8f9fa; padding: 15px; border-left: 4px solid #3498db;">
            <h3 style="margin: 0; color: #2980b9;">${predictionResult}</h3>
        </div>

        <h2 style="margin-top: 30px; color: #34495e;">2. Legal Consultation Transcript</h2>
        <div style="background: #f4f6f6; padding: 20px; border-radius: 5px; font-size: 14px; border: 1px solid #bdc3c7;">
            ${chatHistoryHtml}
        </div>
    `;

    const opt = {
        margin:       0.5,
        filename:     'LawBit_Secure_Report.pdf',
        image:        { type: 'jpeg', quality: 0.98 },
        html2canvas:  { scale: 2 },
        jsPDF:        { unit: 'in', format: 'letter', orientation: 'portrait' }
    };

    html2pdf().set(opt).from(reportContainer).save();
}

// =========================================================
// 8. SERVER-SIDE AUTH MODAL (For Downloads)
// =========================================================
let currentAuthMode = 'login'; 

function openAuthModal() {
    document.getElementById('auth-modal').style.display = 'flex';
    document.getElementById('auth-error').style.display = 'none';
    document.getElementById('username').value = '';
    document.getElementById('password').value = '';
}

function closeAuthModal() { document.getElementById('auth-modal').style.display = 'none'; }

function toggleAuthMode() {
    const title = document.getElementById('auth-title');
    const submitBtn = document.getElementById('auth-submit-btn');
    const toggleText = document.getElementById('auth-toggle-text');
    
    if (currentAuthMode === 'login') {
        currentAuthMode = 'signup';
        title.innerText = "✨ Create Account";
        submitBtn.innerText = "Sign Up";
        submitBtn.setAttribute('onclick', "submitAuth('signup')");
        toggleText.innerHTML = `Already have an account? <span class="text-link" onclick="toggleAuthMode()">Log In</span>`;
    } else {
        currentAuthMode = 'login';
        title.innerText = "🔒 Secure Login";
        submitBtn.innerText = "Log In";
        submitBtn.setAttribute('onclick', "submitAuth('login')");
        toggleText.innerHTML = `Don't have an account? <span class="text-link" onclick="toggleAuthMode()">Sign Up</span>`;
    }
}

async function submitAuth(action) {
    const user = document.getElementById('username').value;
    const pass = document.getElementById('password').value;
    const errorDisplay = document.getElementById('auth-error');
    
    if (!user || !pass) {
        errorDisplay.innerText = "Please fill in both fields.";
        errorDisplay.style.display = 'block'; return;
    }

    const endpoint = action === 'login' ? '/api/login' : '/api/signup';
    
    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: user, password: pass })
        });
        const result = await response.json();
        
        if (result.success) {
            document.getElementById('auth-modal').style.display = 'none';

            document.getElementById('nav-login-btn').innerHTML = `👤 ${user}`;
            document.getElementById('nav-login-btn').style.pointerEvents = 'none';
            document.getElementById('nav-logout-btn').style.display = 'block';

            // FIX: Reliable button unlocking logic
            const actionBtn = document.getElementById('locked-report-btn');
            if (actionBtn) {
                actionBtn.id = 'download-report-btn'; 
                actionBtn.innerHTML = '📥 Download Secure Case Report';
                actionBtn.style.backgroundColor = ''; 
                actionBtn.onclick = generateSecureReport;
            }
        } else {
            errorDisplay.innerText = result.message;
            errorDisplay.style.display = 'block';
        }
    } catch (err) {
        errorDisplay.innerText = "Could not connect to the server.";
        errorDisplay.style.display = 'block';
    }
}