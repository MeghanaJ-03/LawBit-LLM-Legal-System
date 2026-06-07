import os
import numpy as np
from concrete.ml.deployment import FHEModelClient, FHEModelServer

# --- CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PACKAGE_DIR = os.path.join(BASE_DIR, "the_model_package")
KEY_DIR = os.path.join(BASE_DIR, "fhe_keys")

def run_fhe_prediction(evidence, complexity, precedent):
    """
    Receives dynamic numbers from the web UI, encrypts them, 
    runs the XGBoost prediction blindly, and returns the decrypted result.
    """
    print("\n[FHE ENGINE] Initializing Zero-Trust Client/Server Environment...")
    
    # 1. CLIENT SETUP & ENCRYPTION
    client = FHEModelClient(path_dir=MODEL_PACKAGE_DIR, key_dir=KEY_DIR)
    
    # Check if keys exist, if not generate them (saves time on subsequent runs)
    if not os.path.exists(KEY_DIR) or not os.listdir(KEY_DIR):
        print("[CLIENT] Generating Cryptographic Keys...")
        client.generate_private_and_evaluation_keys()
        
    eval_keys = client.get_serialized_evaluation_keys()

    # Load the dynamic UI variables into the numpy array!
    sensitive_case_facts = np.array([[float(evidence), float(complexity), float(precedent)]])    
    print(f"[CLIENT] Encrypting UI Data: {sensitive_case_facts}")
    
    encrypted_payload = client.quantize_encrypt_serialize(sensitive_case_facts)

    # 2. SERVER EXECUTION (In the dark)
    print("[SERVER] Running XGBoost Prediction on Ciphertext...")
    server = FHEModelServer(path_dir=MODEL_PACKAGE_DIR)
    encrypted_prediction = server.run(encrypted_payload, eval_keys)

    # 3. CLIENT DECRYPTION
    print("[CLIENT] Decrypting Result from Server...")
    final_prediction = client.deserialize_decrypt_dequantize(encrypted_prediction)

    print(f"[DEBUG] Raw Model Output array looks like: {final_prediction}")

   # Extract the Win % (Grabbing Class 0 instead of Class 1)
    win_probability = final_prediction[0][0] * 100 
    
    return float(win_probability)

# Keep the test block so you can still run the file directly if needed
if __name__ == "__main__":
    test_result = run_fhe_prediction(8.5, 3.2, 5.0)
    print(f"Test Run Complete. Win Probability: {test_result:.1f}%")