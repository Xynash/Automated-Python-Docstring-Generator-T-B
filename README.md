# 📄 Docgen : Automated Universal Documentation tool

[![Version](https://img.shields.io/badge/Release-Stable-gold?style=for-the-badge)](https://github.com/Xynash/Automated-Python-Docstring-Generator-T-B)
[![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/API-FastAPI-green?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Groq AI](https://img.shields.io/badge/AI-Llama%203.3--70B-orange?style=for-the-badge)](https://groq.com/)

**Docgen** is a professional-grade, service-oriented platform designed to automate the lifecycle of code documentation and quality auditing across multiple programming languages. By orchestrating **Abstract Syntax Trees (AST)** with the **Llama 3.3 70B** model via Groq’s high-speed LPU architecture, the platform performs deep semantic analysis to produce production-ready code intelligence for **Python, Java, JavaScript, and C++**.

## 📌 Project Overview

The Docgen Platform allows users to:

*   **Generate Docstrings**: Automatically insert professional documentation into Python code using AST logic.
*   **Polyglot Support**: Document and analyze logic for *Java, JavaScript, and C++* via intelligent AI routing.
*   **Logic-Aware Code Review**: Perform structured audits to detect bugs, security risks, and optimization needs.
*   **README Generation**: Synthesize entire codebases into a professional GitHub-style README.md.
*   **Interactive Code Chat**: Query specific code blocks and logic via a real-time conversational assistant.
*   **Multi-Style Formatting**: Toggle between *Google, NumPy, and Sphinx* documentation standards.
*   **Batch Processing**: Upload multiple files or a **Project ZIP** for bulk documentation.

This project is suitable for:
*   Engineering teams maintaining large codebases.
*   Open-source contributors requiring standardized documentation.
*   Automated CI/CD documentation pipelines.

## 🛠️ Tech Stack

| Category                      | Technology                         |
| ----------------------------- | ---------------------------------- |
| Frontend                      | Streamlit                          |
| Backend                       | FastAPI                            |
| AI Engine                     | Groq LPU + Llama 3.3 70B Model     |
| Static Analysis               | Python AST (Abstract Syntax Tree)  |
| Telemetry                     | PSUtil (RAM & Latency Tracking)    |
| Data Validation               | Pydantic Models                    |
| Environment                   | Python Virtual Environment (.venv) |

---

## 📂 Project Architecture

The platform follows a **Decoupled Service-Oriented Architecture (SOA)** to ensure modularity and scalability.

```text
AUTOMATED-PYTHON-DOCSTRING-GENERATOR-T-B/
├── .streamlit/                 # UI Configuration & Dashboard Theming
│   └── config.toml
├── app/                        # Main Application Logic
│   ├── api/                    # RESTful Service Layer (FastAPI)
│   │   ├── main.py             # Unified Gateway & Task Routing logic
│   │   └── __init__.py
│   ├── core/                   # The Intelligence Engine (Brain)
│   │   ├── ai_docstring_engine.py # Core LLM Orchestration (Groq/Llama)
│   │   ├── ai_engine.py        # Feature extraction & context analysis
│   │   ├── chat_engine.py      # Conversational code assistant logic
│   │   ├── code_reviewer.py    # Structured bug & security auditing
│   │   ├── docstring_gen.py    # Heuristic fallback system
│   │   ├── file_handler.py     # File I/O orchestration
│   │   ├── inserter.py         # Surgical AST code re-insertion
│   │   ├── parser.py           # AST node mapping & metadata extraction
│   │   ├── prompt_builder.py   # High-context prompt engineering
│   │   └── readme_generator.py # Automatic project documentation logic
│   ├── utils/                  # Shared Helpers
│   │   ├── validators.py       # Syntax and file-integrity checks
│   │   └── __init__.py
│   ├── streamlit_app.py        # Enterprise Dashboard UI
│   └── __init__.py
├── docgen-extension/           # VS Code Extension source code
├── docgen.py                   # Main CLI Entry point
├── docstring.py                # Standalone documentation utility
├── requirements.txt            # Production-grade dependencies
├── .env                        # Environment Secrets (Local only)
├── .gitignore                  # Professional Git exclusion rules
├── LICENSE                     # MIT License
└── README.md                   # Platform Documentation
```

---
## ✅ Prerequisites

Ensure the following are installed on your system:

*  **Python 3.9 or higher**
*  **pip** (Python package manager)
*  **Git**
*  **Groq API Key (Available at console.groq.com)**

Check your versions:
```bash
python --version
pip --version
git --version
```
---

## ⚙️ Step-by-Step Setup Guide

### 1. Create and Activate Virtual Environment

```bash
python -m venv .venv
```

Activate:

**Windows:**

```bash
.venv\Scripts\activate
```

**macOS / Linux:**

```bash
source .venv/bin/activate
```

---

### 2. Install Required Dependencies

Create / verify `requirements.txt`:

```text
streamlit
fastapi
groq
uvicorn
dotenv
```

Install all dependencies:

```bash
pip install -r requirements.txt
```

---

### 3. Configure API Keys

Create a file named .env in the root directory and add your key:
code Text
```bash
GROQ_API_KEY=gsk_your_key_here
```

---

## ▶️ Running the Application
### Option 1: Web Dashboard (Streamlit)
```bash

python -m streamlit run app/streamlit_app.py
```
---
Accessible at:
```bash
 http://localhost:8501
```
---
### Option 2: Backend API (FastAPI)
```bash

python -m uvicorn app.api.main:app --reload
```
---
Interactive Documentation: http://127.0.0.1:8000/docs
### 🧪 Supported Capabilities
## 📄 Source Inputs

  * ✅ Python (.py) - Full AST Support

  * ✅ Java (.java) - Routed AI Logic

  *  ✅ JavaScript (.js) - Routed AI Logic

  * ✅ C/C++ (.c, .cpp) - Routed AI Logic

  *  ✅ Project ZIP - Automated Batch Extraction

## 🔊 Intelligence Tasks

  *  ✅ Documentation: Generates Google, NumPy, or Sphinx docstrings.

  *  ✅ Code Review: Structured JSON analysis of bugs and security risks.

  *  ✅ README Gen: Comprehensive Markdown project overviews.

  *  ✅ Telemetry: Real-time RAM (MB) and Latency monitoring per request.
---

### 🔐 Git Workflow (Important)
Add and Commit Changes
```bash

git add .
git commit -m "Feature: Added Multi-Language Routing"
```
---

Push ONLY to Your Branch
 ```bash

git push origin Member-x
```
---
## 🚫 Never push directly to main without a Pull Request review.
## 🚨 Common Errors & Fixes
Error	Solution
* JSON Decode Error (422)	Ensure input code is wrapped in a {"code": "..."} JSON object.
* Attribute "app" not found	Ensure app = FastAPI() is defined in app/api/main.py.
* ModuleNotFoundError	Ensure you have activated the .venv and run pip install.
* Memory Error	Ensure psutil is installed for telemetry features.

### 👥 Team B

* Ansh Sharma

* Sreya Merin Sam

* Kasa Navyasa Durga

* Vattikoti Pooja

## ⭐ Acknowledgements

* Streamlit Team
* Open-source Python Community
* Mentor Guidance

---
✨ This project follows professional Git and Python development practices for AI-driven code intelligence.
