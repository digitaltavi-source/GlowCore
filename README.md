GlowCore

Applied AI Decision Intelligence Engine

Overview

GlowCore is a modular AI decision framework designed to transform structured inputs into actionable execution plans.

The system follows a clear architecture:

Sense → Decide → Act

GlowCore is built as a scalable decision intelligence layer, designed for future integration with IoT orchestration, automation frameworks, and robotics control systems.

Core Capabilities

Structured input schema (Goal, Situation, Constraints)

Root cause analysis

Prioritized action plan generation

KPI mapping

Risk assessment

Ethical compliance gate

JSON & Markdown export

Offline-first deterministic logic

Optional LLM routing (Gemini-ready)

Architecture

glowcore/
├── core/ # Decision engine logic
├── governance/ # Ethics gate
├── llm/ # LLM routing layer
├── memory/ # Logging system
├── app.py # Streamlit UI
└── README.md

Design principles:

Modular separation of concerns

Offline stability

API-ready extensibility

Expandable action schema

Installation (Local)
python -m pip install -r requirements.txt
python -m streamlit run app.py
Deployment (Streamlit Cloud)

Connect GitHub repository

Set main file path:

glowcore/app.py

(or app.py if placed at root)

Add required API keys in Secrets (optional)

Deploy

Optional: Gemini Integration

To enable LLM routing:

Add in Streamlit Secrets:

GEMINI_API_KEY = "your_api_key_here"

If no API key is provided, the system runs in offline deterministic mode.

Future Roadmap

Action schema output for IoT device control

Node-RED / Home Assistant integration

Robotics command orchestration layer

Edge-device compatible AI module

Engineering Focus

GlowCore demonstrates:

Applied AI architecture thinking

Structured reasoning frameworks

Ethical AI gating

Scalable modular system design

Deployment-ready AI prototyping

Author

Vu Ngoc Luan
Applied AI Systems Builder
Decision Intelligence & Automation Architecture
