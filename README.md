# 📄 Docgen : Automated Universal Documentation tool

[![Version](https://img.shields.io/badge/Release-Stable-gold?style=for-the-badge)](https://github.com/Xynash/Automated-Python-Docstring-Generator-T-B)
[![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/API-FastAPI-green?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Groq AI](https://img.shields.io/badge/AI-Llama%203.3--70B-orange?style=for-the-badge)](https://groq.com/)

**Docgen** is a professional-grade, service-oriented platform designed to automate the lifecycle of code documentation and quality auditing across multiple programming languages. By orchestrating **Abstract Syntax Trees (AST)** with the **Llama 3.3 70B** model via Groq’s high-speed LPU architecture, the platform performs deep semantic analysis to produce production-ready code intelligence for **Python, Java, JavaScript, and C++**.

---

## 🚀 Universal Platform Capabilities

Docgen provides a centralized hub for developer productivity, moving beyond simple docstring generation into a comprehensive **Documentation-as-a-Service (DaaS)** suite:

*   **Polyglot Logic Routing:** Intelligent analysis supporting **Python, Java, JavaScript, and C++** by routing logic through language-specific AI prompts.
*   **Batch Project Ingestion:** Support for **Multiple File selection** and **ZIP Archive** uploads, allowing for the documentation of entire repositories in seconds.
*   **Intelligent Code Chat:** A persistent conversational assistant in the sidebar that allows developers to query their logic and refine documentation in real-time.
*   **Semantic Quality Auditing:** Logic-aware bug detection and security vulnerability scanning with structured JSON reporting.
*   **Unified Service Gateway:** A high-performance FastAPI hub orchestrating all tasks through a single, asynchronous `/process` endpoint.
*   **Operational Telemetry:** Real-time monitoring of RAM consumption (MB) and inference latency to ensure enterprise efficiency.

---

## 📂 Project Architecture

The platform follows a **Decoupled Service-Oriented Architecture (SOA)** to ensure modularity and scalability.

```text
Automated-Python-Docstring-Generator-T-B/
├── .streamlit/                 # UI Configuration & Theming
│   └── config.toml
├── app/                        # Main Application Logic
│   ├── api/                    # RESTful Service Layer (FastAPI)
│   │   ├── main.py             # Unified Gateway & Telemetry logic
│   │   └── __init__.py
│   ├── core/                   # The Intelligence Engine (Brain)
│   │   ├── ai_docstring_engine.py # Core LLM Orchestration
│   │   ├── ai_engine.py        # Logic extraction & context analysis
│   │   ├── chat_engine.py      # Conversational code assistant logic
│   │   ├── code_reviewer.py    # Structured bug & security auditing
│   │   ├── docstring_gen.py    # Heuristic fallback system
│   │   ├── inserter.py         # Surgical AST code re-insertion (Python)
│   │   ├── parser.py           # AST node mapping & metadata extraction
│   │   ├── prompt_builder.py   # High-context AI prompt engineering
│   │   └── readme_generator.py # Automatic project documentation logic
│   ├── utils/                  # Shared Helpers
│   │   ├── validators.py       # Syntax and file-integrity checks
│   │   └── __init__.py
│   ├── streamlit_app.py        # Universal Dashboard UI
│   └── __init__.py
├── docgen.py                   # Main CLI Entry point
├── requirements.txt            # Production-grade dependencies
├── .env                        # Environment Secrets (Local only)
├── .gitignore                  # Professional Git exclusion rules
└── README.md                   # Platform Documentation