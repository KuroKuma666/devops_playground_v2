# Content

This project is for educational purpose. It illustrates a project with some relevant tools for DevOps.

## Project Structure

```text
.
├── .git/                         # Git repository metadata
├── .github/
│   └── workflows/
│       └── CI.yml                # GitHub Actions CI workflow
├── client/
│   ├── Dockerfile                # Nginx container for the frontend
│   ├── index.html                # Static frontend page
│   └── nginx.conf                # Nginx configuration
├── grafana/
│   ├── dashboards/               # Grafana dashboard definitions
│   └── provisioning/             # Grafana datasource/dashboard provisioning
├── server/
│   ├── Dockerfile                # FastAPI backend container
│   ├── src/app/                  # Backend application code
│   └── tests/                    # Pytest backend tests
├── docker-compose.yml            # Local multi-container setup
├── requirements.txt              # Runtime dependency manifest for GitHub's dependency graph
├── myapp.yml                     # Minikube/Kubernetes backend deployment
├── prometheus.yml                # Prometheus scrape configuration
├── pyproject.toml                # Python project metadata and test dependencies
├── deploy-local.ps1              # Starts the local Docker Compose deployment
├── deploy-minikube.ps1           # Builds and deploys the backend to Minikube
└── stop-minikube.ps1             # Stops the Minikube deployment
```

## Included DevOps Concepts

This repository includes:

- Git version control with repository metadata in `.git/`.
- GitHub project automation with a GitHub Actions CI workflow in `.github/workflows/CI.yml`.
- A client-server architecture:
  - Backend: a FastAPI project in `server/src/app`, packaged with `pyproject.toml`.
  - Backend tests: pytest tests in `server/tests`.
  - Frontend: a static client served by Nginx from `client/`.
- Docker-based local deployment with `docker-compose.yml`.
- Minikube/Kubernetes deployment for the backend using `myapp.yml`.
- Prometheus metrics scraping using `prometheus.yml` and the backend `/metrics` endpoint.
- Grafana monitoring dashboards and provisioning in `grafana/`.

## Quickstart

### Run the full stack with Docker Compose

```sh
docker compose up --build
```

After the containers start, open:

| Service | URL |
| ------- | --- |
| Client | http://localhost:8080 |
| Server API | http://localhost:8000 |
| Grafana | http://localhost:3000 |
| Prometheus | http://localhost:9090 |

Stop the stack with:

```sh
docker compose down
```

### Run the server locally

```sh
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[test]"
uvicorn app.main:app --reload --app-dir server/src
```

The FastAPI server is available at http://localhost:8000.

Run the test suite with:

```sh
pytest
```

## Code
This repository contains a small FastAPI app in `server/src/app` and a simple Nginx client in `client/`.

## Dockerfile
The server Dockerfile lives at `server/Dockerfile` and builds the FastAPI app.

````sh
docker build -t test-server:latest -f server/Dockerfile .
docker run -p 8000:8000 test-server:latest
````

## Docker Compose
This repository contains a `docker-compose.yml` that starts the FastAPI server and the Nginx client.

````yml
services:
  server:
    build:
      context: .
      dockerfile: server/Dockerfile
    container_name: devops_test_server
    ports:
      - "8000:8000"
  client:
    build:
      context: ./client
      dockerfile: Dockerfile
    container_name: devops_test_client
    depends_on:
      - server
    ports:
      - "8080:80"
````

````sh
docker compose up --build
````

## Workflow
To demonstrate CI in GitHub, the workflow runs tests and imports the FastAPI app. The workflow is defined in `.github/workflows/CI.yml`.

## Local Deployment Simulation
A "deployment" via docker compose is defined in:
````sh
.\deploy-local.ps1
````

## Minikube
The `myapp.yml` contains deployment rules for **Minkube** and deploys **only the server** (no frontend is served via Kubernetes in this setup). Minkube has to be downloaded, e.g. *https://minikube.sigs.k8s.io/docs/start/* (eventually `minikube` has to be set as environment variable).

````sh
.\deploy-minikube.ps1
````

The service can be stopped with

````sh
.\stop-minikube.ps1
````

## Monitoring & Logging
In the ``docker-compose.yml`` images of **Grafana** and **Prometheus** are included. A simple dashboard is defined in `./grafana/dashboards`. In `./grafana/provisioning` the dashboard is provided and the Prometheus is set as data source.

*Note:* The server needs a route `/metrics` (see. `./server/src/app/main.py`) to work with Prometheus. In the `prometheus.yml` the block

````yml
  - job_name: "server"
    metrics_path: /metrics
    static_configs:
      - targets: ["server:8000"]
````
tells Prometheus to scrape http://server:8000/metrics (within the container!) and attach the label job="server" to those metrics (it pulls the data into Prometheus’ time‑series database with that job label.)

# Software Bill of Materials

The CI workflow submits the dependencies in `requirements.txt` to GitHub's
Dependency Graph and exports its SPDX JSON Software Bill of Materials (SBOM) as
the `dependency-graph-sbom` artifact for each workflow run. Keep
`requirements.txt` aligned with the runtime dependencies in `pyproject.toml`.
The SBOM is a useful inventory of the software components in this repository;
generating it does not by itself demonstrate compliance with any regulation.

The European Union's Cyber Resilience Act (CRA), [Regulation (EU)
2024/2847](https://eur-lex.europa.eu/eli/reg/2024/2847/oj/eng), applies to
products with digital elements within its scope. Under Article 13(6),
manufacturers must identify and document vulnerabilities and components,
including by drawing up a software bill of materials in a commonly used,
machine-readable format that covers at least the product's top-level
dependencies. The main CRA obligations, including this SBOM requirement, apply
from **11 December 2027**. The vulnerability-reporting obligations apply
earlier, from **11 September 2026**.

The SBOM requirement is not a general requirement to publish the SBOM for
everyone: manufacturers must make it available to market surveillance
authorities upon request. See the [European Commission's CRA
overview](https://digital-strategy.ec.europa.eu/en/policies/cyber-resilience-act)
and the [full Regulation](https://eur-lex.europa.eu/eli/reg/2024/2847/oj/eng)
for details. This repository's generated SBOM is an educational CI artifact,
not a claim that the project or its build process meets all CRA requirements.


# Ports
The script `deploy-local.ps1` will run `docker-compose.yml`. The services run on `127.0.0.1` (localhost) following ports:
| Service                  | Port |
| ------------------------ | ---- |
| Client (nginx)           | 8080 |
| Server (python fastapi)  | 8000 |
| Grafana                  | 3000 |
| Prometheus               | 9090 |

