<div align="center">
  <img src="assets/storyboard/storyboard_preview.png" alt="SOC Copilot Hero Image" width="800">
  
  <h1>SOC Copilot</h1>
  <p><b>Next-Generation AI-Driven Security Operations Center Platform</b></p>
  
  <a href="#features">Features</a> •
  <a href="#architecture">Architecture</a> •
  <a href="#installation">Installation</a> •
  <a href="#documentation">Documentation</a>
</div>

<br/>

SOC Copilot is an enterprise-grade, AI-native platform designed to accelerate incident response, automate threat intelligence correlation, and provide analysts with an intuitive, visually rich environment for investigating cyber threats.

---

## 🌟 Features

- **AI-Powered Investigations**: Automated log summarization, anomaly detection, and natural language querying of security events.
- **Real-Time Correlation**: Instantly correlate Indicators of Compromise (IoCs) against global threat feeds and historical data.
- **Immersive Visualizer**: (Upcoming) A scroll-triggered WebGL frontend that dynamically maps the attack lifecycle.
- **MITRE ATT&CK Mapping**: Automatic alignment of detected behaviors to the MITRE framework.
- **Air-Gap Ready**: Fully localized LLM inference via Ollama ensures sensitive data never leaves your environment.
- **Comprehensive API**: REST and WebSocket APIs for seamless integration with existing SIEM/SOAR platforms.

## 🏗️ Architecture

SOC Copilot leverages a highly scalable, decoupled microservices architecture:

- **API Gateway**: FastAPI (Python)
- **Asynchronous Processing**: Celery Workers & Redis
- **Relational Storage**: PostgreSQL
- **Vector Search**: Qdrant (for RAG and semantic correlation)
- **Object Storage**: MinIO (PCAPs, memory dumps)
- **Local AI Inference**: Ollama
- **Observability**: Prometheus & Grafana

*For a deep dive into system diagrams and data flows, see the [Architecture Documentation](docs/architecture/ARCHITECTURE.md).*

## 💻 Tech Stack

- **Backend**: Python 3.12, FastAPI, SQLAlchemy, Celery, Pydantic
- **Frontend** *(In Development)*: Next.js, React, TailwindCSS, Three.js/WebGL
- **Infrastructure**: Docker, Docker Compose, Nginx
- **Databases**: PostgreSQL, Redis, Qdrant, MinIO

## 🚀 Installation

### Prerequisites
- Docker (v24+)
- Docker Compose (v2+)
- Git

### 1. Clone the Repository
```bash
git clone https://github.com/Aadithya-kl/SOC_Copilet.git
cd SOC_Copilet
```

### 2. Environment Variables
Copy the example environment file and configure it according to your setup:
```bash
cp .env.example .env
```
Key variables to configure:
- `POSTGRES_USER` / `POSTGRES_PASSWORD`
- `REDIS_URL`
- `OLLAMA_BASE_URL`
- `JWT_SECRET`

### 3. Docker Setup
Launch the entire stack using Docker Compose:
```bash
docker compose up --build -d
```

Verify that all services are healthy:
```bash
docker compose ps
```

## 🧩 Backend Modules

The backend is modularized to handle specific domains of the incident response lifecycle:
- **Authentication Module**: JWT-based RBAC.
- **Investigation Pipeline**: Automates data gathering and AI synthesis for new incidents.
- **Evidence Management**: Secure handling of PCAPs, logs, and artifacts via MinIO.
- **Threat Intel Engine**: Asynchronous IoC lookups and caching.

## 🧠 AI Pipeline

SOC Copilot implements an advanced Retrieval-Augmented Generation (RAG) pipeline:
1. Evidence and logs are embedded and stored in **Qdrant**.
2. Analyst queries trigger semantic searches against the vector store.
3. Contextualized prompts are sent to **Ollama** (e.g., running Llama 3).
4. The AI generates actionable summaries, MITRE mappings, and remediation steps securely.

## 📸 Screenshots

*(UI currently in development. Placeholders below.)*

| Dashboard | Investigation Graph | AI Chat |
|:---:|:---:|:---:|
| ![Dashboard Placeholder](https://via.placeholder.com/400x225?text=Dashboard) | ![Graph Placeholder](https://via.placeholder.com/400x225?text=Investigation+Graph) | ![Chat Placeholder](https://via.placeholder.com/400x225?text=AI+Chat) |

## 🎨 Frontend Status

**Status: Pending Integration (RC1)**
The backend API is completely finalized and production-ready. 
The `frontend/` directory has been structurally prepared. The interactive, WebGL-driven UI will be built in the next phase. Storyboard assets guiding the frontend development are available in `assets/storyboard/`.

## 🚢 Deployment

For production deployment, we recommend deploying to a Kubernetes cluster using our provided Helm charts (coming soon). Ensure that the Ollama node is provisioned with adequate GPU resources (NVIDIA RTX 3090 / A10G or better) for optimal AI performance.

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contribution

We welcome contributions! Please review our [Contributing Guidelines](CONTRIBUTING.md) and [Code of Conduct](CODE_OF_CONDUCT.md) before submitting a Pull Request.

---
*Built for the modern SOC analyst.*
