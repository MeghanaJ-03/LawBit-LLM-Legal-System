import os
import numpy as np
from concrete.ml.sklearn.xgb import XGBClassifier
from sklearn.model_selection import train_test_split
from concrete.ml.deployment import FHEModelDev

def build_fhe_model():
    print("Generating Logical Historical Court Data (1 to 10 scale)...")
    np.random.seed(42)
    
    # Generate 1000 synthetic court cases
    # Features: [Evidence (1-10), Complexity (1-10), Precedent (1-10)]
    X = np.random.uniform(1.0, 10.0, size=(1000, 3))
    
    # Define a logical rule for Winning:
    # High Evidence and High Precedent easily overcome High Complexity
    # Score = (Evidence * 1.5) + (Precedent * 1.5) - Complexity
    scores = (X[:, 0] * 1.5) + (X[:, 2] * 1.5) - X[:, 1]
    
    # Let's say if the score is above 12, it's a Win (Class 0), else Loss (Class 1)
    y = (scores < 12).astype(int) 

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    print("Training XGBoost Model...")
    model = XGBClassifier(n_jobs=1)
    model.fit(X_train, y_train)

    print("Compiling Model into Fully Homomorphic Encryption (FHE)...")
    model.compile(X_train)

    print("Saving New Client and Server Zip Files...")
    base_dir = os.path.dirname(os.path.abspath(__file__))
    export_dir = os.path.join(base_dir, "the_model_package")
    
    dev = FHEModelDev(export_dir, model)
    dev.save()
    
    print(f"✅ SUCCESS! Logical Model generated at: {export_dir}")

if __name__ == "__main__":
    build_fhe_model()