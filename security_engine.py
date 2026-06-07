import hashlib
from ecdsa import SigningKey, SECP256k1

def generate_keys():
    """Generates the LawBit Server's private and public keys."""
    print("Generating Cryptographic Keys (SECP256k1 Curve)...")
    # The Private Key is kept secret by the server to create the seal.
    private_key = SigningKey.generate(curve=SECP256k1)
    
    # The Public Key is given to the user's browser to verify the seal.
    public_key = private_key.get_verifying_key()
    
    return private_key, public_key

def sign_document(private_key, document_text):
    """Creates the Digital Wax Seal (Hash + ECDSA Signature)."""
    # 1. Compress the text into a unique fingerprint (SHA-256)
    document_bytes = document_text.encode('utf-8')
    fingerprint = hashlib.sha256(document_bytes).digest()
    
    # 2. Lock the fingerprint using the private key
    signature = private_key.sign(fingerprint)
    
    return signature

def verify_document(public_key, document_text, signature):
    """Checks if the document is authentic and untouched."""
    # Re-calculate the fingerprint of the text being checked
    document_bytes = document_text.encode('utf-8')
    fingerprint = hashlib.sha256(document_bytes).digest()
    
    try:
        # Try to unlock the signature with the public key
        # If the fingerprint changed even slightly, this will fail.
        is_valid = public_key.verify(signature, fingerprint)
        return True
    except:
        return False

# --- MAIN EXECUTION (FOR TESTING) ---
if __name__ == "__main__":
    # 1. Setup the keys
    private_key, public_key = generate_keys()
    
    # 2. Pretend this is the answer your AI just generated
    ai_answer = "Under BNS Section 303, theft is punishable by up to 3 years imprisonment."
    
    # 3. Sign the answer (Create the Wax Seal)
    my_signature = sign_document(private_key, ai_answer)
    print("\n[+] Document Signed Successfully.")
    
    # 4. Verify it! (This represents what happens on the user's screen)
    print("\nVerifying Authentic Document...")
    is_authentic = verify_document(public_key, ai_answer, my_signature)
    print(f"Is it authentic? {'✅ YES' if is_authentic else '❌ NO'}")
    
    # 5. Let's pretend a hacker intercepted the message and changed just ONE word
    hacked_answer = "Under BNS Section 303, theft is NOT punishable."
    
    print("\nVerifying Hacked Document...")
    is_still_authentic = verify_document(public_key, hacked_answer, my_signature)
    print(f"Is it authentic? {'✅ YES' if is_still_authentic else '❌ NO (TAMPERING DETECTED)'}")