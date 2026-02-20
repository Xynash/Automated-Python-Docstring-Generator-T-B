🐍 Automated Python Docstring Generator

An intelligent tool that automatically generates professional, industry-standard documentation (docstrings) for Python code using Abstract Syntax Trees (AST) and Large Language Models (LLMs).

📌 Project Overview

The Problem 

Developers often view manual documentation as time-consuming and tedious. This results in codebases with poor readability, high maintenance costs, and difficult onboarding for new team members.
Our Solution

An AI-powered system that reads Python files, understands function logic through static analysis (AST), and generates clear, professional docstrings in seconds. It supports multiple formats (Google, NumPy, reStructuredText) and ensures 100% documentation coverage.

✨ Key Features

    AST-Based Parsing: Uses Python's ast module to accurately identify functions, classes, parameters, and return types without executing the code.

    AI-Driven Logic Analysis: Leverages OpenAI's GPT models to understand the "Why" and "How" behind function logic, moving beyond simple keyword matching.

    Context Awareness: Recognizes class methods and global functions to provide scope-accurate descriptions.

    Multiple Style Support: Generate docstrings in Google, NumPy, or reStructuredText formats.

    Safe Code Insertion: Reconstructs code with new docstrings while preserving original logic and indentation.

    FastAPI Ready: Built with a modular backend designed to transition from a prototype to a production-grade API.

🛠 Tech Stack

    Core: Python 3.x

    Parsing: ast (Abstract Syntax Tree)

    AI Integration: OpenAI API (GPT-4o-mini)

    Web Interface: Streamlit

    API (In Progress): FastAPI

    Environment Management: Python-dotenv, Pydantic


🚀 Getting Started
1. Prerequisites

    Python 3.9 or higher

    An OpenAI API Key

2. Installation
code Bash

# Clone the repository
git clone https://github.com/Xynash/Automated-Python-Docstring-Generator-T-B.git

# Navigate to the project directory
cd Automated-Python-Docstring-Generator-T-B

# Install dependencies
pip install -r requirements.txt

3. Configuration

Create a .env file in the root directory and add your OpenAI API key:
code Text

OPENAI_API_KEY=your_actual_api_key_here

4. Running the App
code Bash

python -m streamlit run app/streamlit_app.py

📊 Workflow & Collaboration

This project follows a professional Feature-Branch Workflow:

    main Branch: Contains the stable project skeleton and configuration.

    Member-1 Branch: Active development for the core AI engine and UI.

    Pull Requests: All new features are reviewed and merged into main only after passing quality checks.

🛣 Roadmap

    Core AST Parser

    AI Docstring Generation (Google Style)

    Streamlit Prototype

    FastAPI Backend Migration

    Support for JavaScript & Go

    VS Code Extension Integration

    CI/CD Pipeline for automatic documentation checks

👥 Contributors

    Member 1 : Ansh Sharma

    Member 2 : Sreya Merin Sam

    Member 3 : Kasa Navyasa Durga

    Member 4 : Vattkaoti Pooja


📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
