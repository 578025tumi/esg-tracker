# 🌍 Autonomous ESG Supply Chain Tracker
**An AI-driven data pipeline for real-time corporate ethics & sustainability auditing.**

[![Tech Stack](https://img.shields.io/badge/Stack-FastAPI%20|%20Next.js%20|%20Redis%20|%20OpenAI-blue)]()

## 🚀 The Problem
Corporate sustainability reports are often "greenwashed" and updated only once a year. Investors need real-time, ground-truth data on supply chain violations, environmental impact, and labor practices as they happen in the global news.

## 🛠️ System Architecture
This platform uses a **distributed worker pattern** to process unstructured data at scale.

```mermaid
graph TD
    A[Next.js Dashboard] -->|Submit URL| B(FastAPI Gateway)
    B -->|Task Queue| C[Redis]
    C -->|Pick up Job| D[Python Worker]
    D -->|Scrape| E[Web Source]
    D -->|Analyze| F[GPT-4o Structured Output]
    F -->|Persist| G[(PostgreSQL)]
    B -->|Poll Status| G
    G -->|Stream Results| A