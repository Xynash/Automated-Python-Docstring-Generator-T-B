# 🐍 PyDoc AI: Intelligent Documentation Engine

**PyDoc AI** is a professional-grade, production-ready ecosystem designed to automate the most tedious part of software engineering: documentation. By leveraging **Abstract Syntax Trees (AST)** and the **Llama 3.3 70B** model, it performs deep semantic analysis to generate industry-standard docstrings that actually understand your code's intent.

# ✨ Features

*   🔍 **Logic-Aware Synthesis:** Unlike static templates, our AI analyzes the mathematical and logical operations within a function to describe *how* and *why* it works.
*   🌳 **AST Precision:** Uses Python's Abstract Syntax Tree to surgically identify functions, class scopes, and arguments without ever executing the source code.
*   🌐 **Headless API Architecture:** A robust FastAPI backend that can power Web UIs, CLI tools, and IDE extensions (VS Code) simultaneously.
*   🎨 **Enterprise Multi-Style:** One-click support for **Google**, **NumPy**, and **Sphinx** documentation standards.
*   🛡️ **Defensive Engineering:** A built-in Heuristic Fallback system ensures you get documentation even if the AI cloud service is offline.

## 🛠️ Tech Stack

*   **Frontend:** Streamlit (Custom Dark/Neon Engineering Theme).
*   **Backend:** Python, FastAPI, Uvicorn (Asynchronous Concurrency).
*   **Parsing Engine:** Python AST (Abstract Syntax Tree).
*   **AI Engine:** Groq SDK (Llama 3.3 70B Model) for sub-second inference.
*   **Environment:** Pydantic (Data Models), Python-Dotenv.

```text
📂 File Directory Structure

Automated-Python-Docstring-Generator-T-B/
├── app/
│   ├── api/                # FastAPI Entry point & REST routes
│   │   ├── main.py
│   │   └── __init__.py
│   ├── core/               # The "Brain" (AST & AI Logic)
│   │   ├── parser.py       # Metadata extraction
│   │   ├── ai_engine.py    # Logic analysis
│   │   ├── inserter.py     # Surgical code injection
│   │   ├── prompt_builder.py
│   │   └── ai_docstring_engine.py
│   ├── utils/              # File validation & helpers
│   ├── streamlit_app.py    # Web-based UI Dashboard
│   └── __init__.py
├── .env                    # API Keys (Environment Variables)
├── .gitignore              # Git exclusion rules
├── requirements.txt        # Project dependencies
└── README.md               # Documentation

# 🚀 Installation & Setup

### 1. Prerequisites
*   **Python 3.10+**
*   **Groq API Key** (Get it free at [console.groq.com](https://console.groq.com))

### 2. Environment Setup
```bash
# Clone the repository
git clone https://github.com/Xynash/Automated-Python-Docstring-Generator-T-B.git
cd Automated-Python-Docstring-Generator-T-B

# Create and activate a virtual environment
python -m venv venv

# On Windows:
.\venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
