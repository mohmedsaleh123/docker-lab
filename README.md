# Final Project: Device Registry API

## Project Description
A modernized, containerized REST API for managing IoT devices, demonstrating multi-service architecture with Nginx, Python Flask, and PostgreSQL.

## Architecture Diagram
```text
                         EXTERNAL TRAFFIC
                               │
                               │ HTTP :8080
                               ▼
                    ┌─────────────────────┐
                    │   NGINX CONTAINER   │
                    │   Reverse Proxy     │
                    │   Host :8080        │
                    └──────────┬──────────┘
                               │
                               │ Internal HTTP
                               ▼
                 ┌────────────────────────────┐
                 │   INTERNAL BRIDGE NETWORK  │
                 │       app-network          │
                 │                            │
                 │   ┌────────────────────┐   │
                 │   │   BACKEND API      │   │
                 │   │   REST Service     │   │
                 │   │   :8000            │   │
                 │   └─────────┬──────────┘   │
                 │             │              │
                 │             │ DB protocol  │
                 │             ▼              │
                 │   ┌────────────────────┐   │
                 │   │     DATABASE       │   │
                 │   │   PostgreSQL       │   │
                 │   └─────────┬──────────┘   │
                 └─────────────┼──────────────┘
                               │
                               │ Persistent Storage
                               ▼
                    ┌─────────────────────┐
                    │ Docker Named Volume │
                    │    db-data          │
                    └─────────────────────┘
```

## Technology Stack
- **Backend**: Python 3.12 (Flask)
- **Database**: PostgreSQL 15
- **Reverse Proxy**: Nginx 1.25
- **Containerization**: Docker & Docker Compose

## Repository Structure
```
project/
├── api/
│   ├── src/
│   │   └── server.py
│   ├── Dockerfile
│   ├── .dockerignore
│   └── requirements.txt
├── nginx/
│   └── nginx.conf
├── database/
│   └── initialization/
│       └── init.sql
├── compose.yaml
├── .gitignore
└── README.md
```

## Prerequisites
- Docker Engine / Docker Desktop
- Docker Compose v2
- cURL or Postman

## One-step startup command
This command starts the complete multi-container system:
```bash
docker compose up -d
```

## API Endpoint Documentation
- `GET /api/resources` - List all devices
- `GET /api/resources/{id}` - Get device by ID
- `POST /api/resources` - Create a new device
- `PUT /api/resources/{id}` - Update a device
- `DELETE /api/resources/{id}` - Delete a device

## Registry Information
- **Registry**: Docker Hub
- **Image**: `docker.io/teamname/project-api`
- **Tags**: `v1.0.0`, `latest`

## Team Members
- Agent Engineer (Autonomous AI)

## Version Information
- v1.0.0
