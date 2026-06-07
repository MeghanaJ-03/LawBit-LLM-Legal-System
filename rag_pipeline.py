import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq

# Restored this import so your FAISS database can read the PDF!
from langchain_huggingface import HuggingFaceEmbeddings 

from security_engine import generate_keys, sign_document, verify_document

# --- CONFIGURATION ---
BNS_PDF_PATH = "data/BNS_official.pdf" 
FAISS_INDEX_PATH = "faiss_bns_index"

# Keys
os.environ["HUGGINGFACEHUB_API_TOKEN"] = "HUGGINGFACE_API_KEY"
os.environ["GROQ_API_KEY"] = "GROQ_API_KEY"

if not 'HUGGINGFACEHUB_API_TOKEN' or not 'GROQ_API_KEY':
    raise ValueError("Missing API keys! Please check your .env file.")

def load_and_chunk_pdf(file_path):
    """Phase 1: Data Acquisition & Preprocessing"""
    print("Loading BNS document...")
    loader = PyPDFLoader(file_path)
    documents = loader.load()
    
    print("Chunking text to preserve legal context...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, 
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_documents(documents)
    return chunks

def get_vector_store(chunks=None, force_rebuild=False):
    """Phase 2: Vector Database Setup"""
    embeddings = HuggingFaceEmbeddings(model_name="nlpaueb/legal-bert-base-uncased")
    
    if os.path.exists(FAISS_INDEX_PATH) and not force_rebuild:
        print("Loading existing FAISS index...")
        vector_store = FAISS.load_local(FAISS_INDEX_PATH, embeddings, allow_dangerous_deserialization=True)
    else:
        if chunks is None:
            raise ValueError("Chunks must be provided to build a new index.")
        print("Building new FAISS vector database...")
        vector_store = FAISS.from_documents(chunks, embeddings)
        vector_store.save_local(FAISS_INDEX_PATH)
        print("FAISS index saved locally.")
        
    return vector_store

def setup_rag_chain(vector_store, llm):
    """Phase 2: LLM Integration with an Empathetic & Factual Prompt"""
    retriever = vector_store.as_retriever(search_kwargs={"k": 3})
    
    # --- STRICT ZERO-TRUST LEGAL PROMPT ---
    # --- SMART ZERO-TRUST LEGAL PROMPT ---
    # --- DEEPLY EMPATHETIC ZERO-TRUST LEGAL PROMPT ---
    # --- PROFESSIONAL & WARM ZERO-TRUST LEGAL PROMPT ---
    # --- CALIBRATED EMPATHY ZERO-TRUST LEGAL PROMPT ---
    # --- DEEPLY SUPPORTIVE & PRECISE ZERO-TRUST LEGAL PROMPT ---
    # --- DEEPLY SUPPORTIVE, PRECISE & EVIDENCE-BASED ZERO-TRUST PROMPT ---
    lawbit_system_template = """
You are LawBit, an elite Legal AI Assistant specializing in the Bharatiya Nyaya Sanhita (BNS).
Your communication style must be deeply empathetic, reassuring, and highly professional. You must adhere to the following rules:

1. EMPATHETIC & VALIDATING COMMUNICATION:
Legal issues are inherently stressful. You MUST weave a supportive and validating tone throughout your responses. Use naturally reassuring phrases (e.g., "I understand this is a frustrating situation," "Let's figure this out together"). Make the user feel heard and supported at every step.

2. MAP EVERYDAY TERMS TO BNS:
Connect regular words (e.g., "stolen", "gold") to BNS legal concepts (e.g., "movable property", "theft") seamlessly.

3. PROGRESSION, CLOSURE & STRICT EVIDENCE:
Check the PREVIOUS CHAT CONTEXT. If the user has answered your questions, DO NOT ask any more. You must now provide your final legal assessment. 
CRITICAL TRUST REQUIREMENT: You MUST explicitly state the correct BNS Section Number(s). Furthermore, you MUST provide a direct, relevant quote or specific detail extracted directly from the provided BNS LEGAL CONTEXT to prove your answer is factual. Do NOT rely on old IPC section numbers. 
Wrap this assessment in a warm, encouraging tone to help them feel empowered.

4. CONDITIONAL ADVICE FOR NEW QUERIES:
If a query lacks detail, provide the general legal stance first. Then, ask a MAXIMUM of 1 or 2 concise, politely phrased clarifying questions.

5. OUT OF SCOPE BOUNDARIES: 
Only say "I cannot verify this under the BNS framework" IF the query is completely outside criminal law. Do so gently.

6. DISCLAIMER:
Always end your advice with a short reminder that you are an AI and this is for educational purposes, not formal legal counsel.

==============================
BNS LEGAL CONTEXT:
{context}
==============================

USER'S QUERY (Includes previous chat history if applicable): 
{question}

LAWBIT'S VERIFIED RESPONSE:
"""

    prompt = PromptTemplate(
        template=lawbit_system_template, 
        input_variables=["context", "question"]
    )
    
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)
    
    chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    return chain

# ==========================================================
# --- GLOBAL INITIALIZATION FOR FLASK ---
# This is now outside the __main__ block so app.py can see it!
# ==========================================================

print("Initializing LawBit AI Brain...")
llm = ChatGroq(temperature=0.01, model_name="llama-3.1-8b-instant")
vector_store = get_vector_store(force_rebuild=False)
rag_chain = setup_rag_chain(vector_store, llm)

# ==========================================================

if __name__ == "__main__":
    # You can still run the file directly to test it in the terminal
    query = "My car was stolen, what should I do?"
    print(f"\nUser Query: {query}")
    response = rag_chain.invoke(query)
    print("\n--- LAWBIT RESPONSE ---")
    print(response)