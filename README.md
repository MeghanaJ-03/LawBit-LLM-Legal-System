# ⚖️ LawBit: LLM-Powered Legal Awareness & Analytics Platform

LawBit is an advanced legal intelligence platform designed to simplify complex legal texts and improve legal literacy. By combining Large Language Models (LLMs) with a robust Retrieval-Augmented Generation (RAG) pipeline, LawBit provides highly accurate, context-aware legal summaries and answers. The platform enforces strict cryptographic protocols to protect sensitive user inputs and query histories.

## 🚀 Key Features

* **High-Speed RAG Pipeline:** Utilizes an optimized Retrieval-Augmented Generation framework powered by **Groq** for ultra-fast LLM inference and **Hugging Face** for contextual embeddings.
* **Predictive Legal Analytics:** Integrates predictive modeling to streamline data workflows, anticipate user query patterns, and enhance overall information retrieval.
* **Applied Cryptography (ECDSA):** Implements the Elliptic Curve Digital Signature Algorithm (ECDSA) alongside secure data encryption mechanics to authenticate data and safeguard user privacy.
* **Production-Ready Configuration:** Enforces zero-hardcoded secrets by isolating API credentials within a secure local environment via `python-dotenv`.

## 🛠️ Tech Stack

* **Frontend Interface:** HTML5, CSS3, JavaScript
* **Backend & Core Language:** Python 3.x
* **LLM Inference Engine:** Groq Cloud API
* **Embeddings & Models:** Hugging Face API
* **Security & Environment:** Python `cryptography` (ECDSA), `python-dotenv`
* **Data Processing:** Scikit-learn, Pandas, NumPy

## 🔒 Security Architecture

This repository complies with modern application security standards:
* **Zero Credential Leakage:** Real API tokens are strictly isolated within a local `.env` file which is blocked from deployment via a `.gitignore` policy.
* **Dynamic Variable Loading:** Code structures dynamically reference configuration keys via system environment parameters using `os.getenv()`.

## 🤝 Contributing

Contributions to enhance LawBit's analytics or security layers are welcome! Please fork the repository, create a feature branch, and submit a detailed Pull Request.
