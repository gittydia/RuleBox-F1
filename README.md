# RuleBox-F1

A fullstack AI-powered Formula 1 regulations assistant and search platform.

- **Backend:** FastAPI (Python), MongoDB, OpenRouter AI integration
- **Frontend:** Next.js (React, TypeScript)
- **Deployment:** Docker, Render, Nginx

---

## Table of Contents

- [Features](#features)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Docker Compose](#docker-compose)
- [API Endpoints](#api-endpoints)


---

## Features

- 🔍 **Semantic Search**: Search F1 regulations using natural language.
- 🤖 **AI Assistant**: Ask F1-related questions, get expert answers powered by LLMs (DeepSeek via OpenRouter).
- 🗃️ **PDF Ingestion**: Automatically downloads and processes FIA regulation PDFs.
- 🛡️ **Authentication**: User registration and login (JWT-based).
- 🖥️ **Modern Frontend**: Next.js app with React, TypeScript, and MUI components.
- 🚀 **Production Ready**: Dockerized, with Nginx reverse proxy and Render deployment configs.

---

## Getting Started

### Prerequisites

- [Python 3.10+](https://www.python.org/downloads/)
- [Node.js 18+](https://nodejs.org/)
- [Docker](https://www.docker.com/) (for containerized setup)
- [MongoDB](https://www.mongodb.com/) (local or cloud, e.g. [MongoDB Atlas](https://www.mongodb.com/cloud/atlas))

### Environment Variables

Create a `.env` file in the `backend/` directory with the following variables:



- Frontend: [http://localhost](http://localhost)
- Backend API: [http://localhost:8000](http://localhost:8000)

---

## API Endpoints

### Backend (FastAPI)

| Endpoint                | Method | Description                         |
|-------------------------|--------|-------------------------------------|
| `/`                     | GET    | API status                          |
| `/health`               | GET    | Health check                        |
| `/auth/register`        | POST   | Register a new user                 |
| `/auth/login`           | POST   | Login and get JWT                   |
| `/api/search`           | POST   | Semantic search of regulations      |
| `/api/ai-query`         | POST   | Ask AI assistant (LLM)              |
| `/api/ingest-data`      | POST   | Trigger PDF ingestion (admin only)  |
| `/api/data-status`      | GET    | Get DB status                       |

### Frontend (Next.js)

- Main app: `/`
- Auth: `/auth/login`, `/auth/register`
- AI Chat: `/ai-chat`
- Search: `/query`

---

## Deployment

### Render.com

- Use the provided `render.yaml`, `render-frontend.yaml`, and `render-nginx.yaml` for deploying backend, frontend, and nginx services.
- Set environment variables in the Render dashboard for secrets.

---
