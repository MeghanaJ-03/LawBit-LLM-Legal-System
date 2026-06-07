import os
# Suppress the Hugging Face tokenizer warning
os.environ["TOKENIZERS_PARALLELISM"] = "false"

from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# --- 1. AI & SECURITY ENGINES ---
from rag_pipeline import rag_chain
from security_engine import generate_keys, sign_document
from fhe_simulation import run_fhe_prediction

# Generate LawBit's master cryptographic keys when the server starts
SERVER_PRIVATE_KEY, SERVER_PUBLIC_KEY = generate_keys()

app = Flask(__name__)
app.secret_key = "super_secret_lawbit_key"

# --- 2. DATABASE CONFIGURATION ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lawbit.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

with app.app_context():
    db.create_all()


# =========================================================
# 3. CORE APPLICATION ROUTES
# =========================================================

@app.route('/')
def home():
    """Serves the main application interface."""
    user_status = 'user_id' in session 
    print(f"[DEBUG] Loading home page. Is user logged in? {user_status}")
    return render_template('index.html', is_logged_in=user_status)

@app.route('/api/chat', methods=['POST'])
def chat():
    """Receives user query, manages isolated session memory, and runs the RAG AI."""
    data = request.json
    user_query = data.get('query')
    
    print(f"\n[SERVER] Received query: {user_query}")
    
    # --- ISOLATED SESSION MEMORY ---
    # Create a fresh memory vault for this specific browser session if it doesn't exist
    if 'chat_memory' not in session:
        session['chat_memory'] = []
        
    current_memory = session['chat_memory']
    
    if current_memory:
        recent_context = "\n".join(current_memory[-4:]) # Grab last 2 exchanges
        enhanced_query = f"""You are LawBit, an AI legal assistant specializing in the BNS framework.
        
[PREVIOUS CHAT HISTORY]
{recent_context}

[CURRENT USER QUERY]
{user_query}

CRITICAL INSTRUCTIONS:
1. You must ONLY answer the CURRENT USER QUERY.
2. Do NOT write the user's next response. 
3. Stop generating text immediately after you finish your advice."""
    else:
        enhanced_query = f"""You are LawBit, an AI legal assistant specializing in the BNS framework.
        
[CURRENT USER QUERY]
{user_query}

CRITICAL INSTRUCTIONS:
1. You must ONLY answer the CURRENT USER QUERY.
2. Do NOT write the user's next response.
3. Stop generating text immediately after you finish your advice."""
        
    print("[SERVER] LawBit is consulting the vector database...")
    
    try:
        raw_ai_response = rag_chain.invoke(enhanced_query)
        
        # Handle dict or string response from LangChain
        actual_answer = raw_ai_response.get('result', str(raw_ai_response)) if isinstance(raw_ai_response, dict) else raw_ai_response
            
        # Update this specific user's memory securely
        current_memory.append(f"User: {user_query}")
        current_memory.append(f"LawBit: {actual_answer}")
        
        # Keep memory from getting too large (limit to last 6 messages)
        session['chat_memory'] = current_memory[-6:]
        session.modified = True # Tell Flask to save the cookie
            
        # Cryptographically seal the response
        signature = sign_document(SERVER_PRIVATE_KEY, actual_answer)
        print("[SERVER] Response generated and sealed.")
        
        return jsonify({
            "response": actual_answer,
            "signature": signature.hex()[:40] + "...", 
            "verified": True
        })
        
    except Exception as e:
        print(f"[ERROR] Chat failure: {str(e)}")
        return jsonify({"response": "System Error: Could not generate advice.", "verified": False})


@app.route('/api/predict', methods=['POST'])
def predict():
    """Runs the Concrete ML FHE model on encrypted parameters."""
    data = request.json
    evidence = data.get('evidence', 5.0)
    complexity = data.get('complexity', 5.0)
    precedent = data.get('precedent', 5.0)
    
    try:
        win_probability = run_fhe_prediction(evidence, complexity, precedent)
        return jsonify({"win_probability": round(win_probability, 1)})
    except Exception as e:
        print(f"[ERROR] FHE Prediction failed: {str(e)}")
        return jsonify({"win_probability": "Error"})


# =========================================================
# 4. AUTHENTICATION & SECURITY ROUTES
# =========================================================

@app.route('/api/signup', methods=['POST'])
def signup():
    """Creates a new user and securely hashes their password."""
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if User.query.filter_by(username=username).first():
        return jsonify({"success": False, "message": "Username already exists."})
        
    new_user = User(username=username, password_hash=generate_password_hash(password))
    db.session.add(new_user)
    db.session.commit()
    
    session['user_id'] = new_user.id 
    return jsonify({"success": True, "message": "Account created successfully!"})


@app.route('/api/login', methods=['POST'])
def login():
    """Verifies credentials and assigns a secure session cookie."""
    data = request.json
    user = User.query.filter_by(username=data.get('username')).first()
    
    if user and check_password_hash(user.password_hash, data.get('password')):
        session['user_id'] = user.id
        return jsonify({"success": True, "message": "Logged in successfully!"})
    
    return jsonify({"success": False, "message": "Invalid username or password."})


@app.route('/logout')
def logout():
    """Destroys the session cookie and clears memory."""
    session.clear()
    return redirect(url_for('home'))


@app.route('/api/check-session')
def check_session():
    """Validates active user session for secure actions."""
    return jsonify({"logged_in": 'user_id' in session})


# =========================================================
# 5. SERVER EXECUTION
# =========================================================
if __name__ == '__main__':
    print("🚀 LawBit Server is running! Open http://127.0.0.1:5000 in your browser.")
    app.run(port=5000, debug=True)