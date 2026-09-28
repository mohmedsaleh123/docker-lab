# Final Project Technical Report
## Section 1 — Executive Summary
This project addresses the challenges of deploying monolithic legacy applications by modernizing a device management service into a containerized, multi-service architecture. We designed a RESTful backend API using Python (Flask) connected to a PostgreSQL database. Nginx is employed as a reverse proxy to manage external HTTP traffic and securely route it to the backend API without exposing internal ports. The engineering objective was to achieve process isolation, layered caching, non-root execution, and reproducible deployments using Docker and Docker Compose.

## Section 2 — System Architecture
The application comprises three core components: an Nginx reverse proxy, a Flask REST API, and a PostgreSQL database.
- **External network:** Receives HTTP traffic on host port 8080.
- **Nginx:** Routes external traffic from host port 8080 to the internal bridge network.
- **Internal bridge network:** A custom Docker network (`app-network`) connecting the containers.
- **API:** Runs as a non-root user, listening on port 8000 internally. It has no published host ports.
- **Database:** PostgreSQL storing application data, communicating with the API over the internal network.
- **Named volume:** `db-data` provides persistent storage for the database.

## Section 3 — Virtualization vs. Containerization Analysis
We used containers because they provide lightweight isolated environments that share the host OS kernel, making them highly suitable for independently deployable microservices.
- **Guest OS:** VMs require a full Guest OS; Containers do not package a guest OS.
- **Kernel:** VMs use a guest kernel; Containers share the host kernel.
- **Resource overhead:** VMs have higher overhead; Containers have lower overhead.
- **Startup:** VMs start slower; Containers start rapidly.
- **Isolation:** VMs provide hardware-level isolation; Containers provide process/user-space isolation.

## Section 4 — Dockerfile & Layer Optimization Analysis
The Dockerfile uses `python:3.12-slim` for a balance of small image size and compatibility.
Dependency caching is implemented by copying `requirements.txt` and running `pip install` BEFORE copying the application source code.
This ensures that:
`Dependency files unchanged -> Dependency layer remains cached -> Source code changes -> Only later layers rebuild`.
We use `.dockerignore` to exclude cache and environment files. The application runs as a non-root `appuser`.

## Section 5 — Security Practices
- **Non-root execution:** The API Dockerfile creates and switches to a non-root user.
- **Restricted host exposure:** The API and DB do not publish ports to the host; only Nginx is exposed.
- **Read-only Nginx configuration mount:** Nginx configuration is mounted with `:ro` to prevent container modifications.
- **Network isolation:** Services communicate exclusively over the custom `app-network`.
- **Trusted base image:** Official slim Python and Alpine Nginx/Postgres images reduce attack surface.

## Section 6 — Network Architecture
The `app-network` is a custom Docker bridge network. 
- **Host-to-container port publishing:** Only `8080:80` for Nginx.
- **Container-to-container communication:** The API connects to `database` via Docker's internal DNS service-name discovery.
- **Why API doesn't need a host port:** Nginx routes traffic securely within the Docker network, hiding the backend architecture.
- **Why DB shouldn't be publicly exposed:** Prevents direct external attacks on the data store.

## Section 7 — Storage Architecture
The database utilizes a **named volume** (`db-data`).
- **Named Volume:** Docker-managed persistent storage, ideal for databases where Docker manages the storage location and lifecycle.
- **Bind Mount:** Maps a specific host path to a container path, used for our `nginx.conf` (read-only) for easy configuration updates without rebuilding.

## Section 8 — Proof of Persistence Verification
When the system is started, a POST request adds a device.
Stopping the stack via `docker-compose down` removes the containers and network but retains the named volume.
Upon restarting with `docker-compose up -d`, a GET request confirms the previously created device still exists in the PostgreSQL database.

## Section 9 — Failure-Mode Scenarios
- **Scenario A (API Container Failure):** If the API is stopped (`docker compose stop api`), Nginx returns a 502 Bad Gateway error. The client cannot reach the API. The DB is unaffected. Recovered by `docker compose start api`.
- **Scenario B (Database Failure):** If the database is stopped (`docker compose stop database`), the API will fail to execute queries, returning 500 Internal Server Error. Nginx successfully routes to the API, but the API fails. Recovered by `docker compose start database`.
- **Scenario C (Container Recreation):** Running `docker compose down` and `docker compose up -d` destroys and recreates the containers, but data persists via the named volume, demonstrating state separation from container lifecycle.

## Section 10 — Registry & Versioning
- **Registry:** Docker Hub (docker.io)
- **Repository name:** `project-api`
- **Image name:** `teamname/project-api`
- **Version tags:** `v1.0.0` and `latest`
- **Push command:** `docker push teamname/project-api:v1.0.0`
- **Pull command:** `docker pull teamname/project-api:v1.0.0`

## Section 11 — Testing Evidence
Tested endpoints: `GET /api/resources`, `POST /api/resources`, `PUT /api/resources/1`, `DELETE /api/resources/1`.
All requests routed successfully through Nginx. Persistence verified across container restarts.

## Section 12 — Team Contributions
- Agent Engineer (Autonomous AI): Designed architecture, implemented REST API, optimized Dockerfile, configured Nginx, and managed Docker Compose orchestration.
