# Long Read Nanopore Methylation Agent

> **Domain:** Clinical Decision Support & Biomedical Computing  
> **Reference Guidelines & Standards:** `Standard Clinical Formulations & ISO/IEC Quality Frameworks`

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?logo=fastapi&logoColor=white)
![Audit Trail](https://img.shields.io/badge/Audit-HMAC--SHA256_Tamper--Evident-brightgreen.svg)
![Zero-PHI Guard](https://img.shields.io/badge/Guard-Zero--PHI_Outbound-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)

</div>

---

## 📖 What It Does

**Long Read Nanopore Methylation Agent** is an advanced analytical and computational platform implementing Oxford Nanopore raw squiggle current deviation 5mC/5hmC methylation agent.

---

## ⚙️ Key Capabilities & Algorithmic Modules

- **Deterministic Calculation Engine**: Strict compliance with standard reference formulations and thresholds.
- **Risk & Urgency Classification**: Multi-tier categorization with automated clinical/operational action recommendations.
- **Validation & Guardrails**: Rigorous input bounds checking and anomaly detection.

---

## 💻 CLI Quickstart & Usage

### 1. Single Task Evaluation
```bash
python cli.py audit --task-id TASK-001 --target KEY-01 --primary 28.5 --secondary 14.2 --critical --status DISCORDANT
```

### 2. Supervisory Chat Query
```bash
python cli.py chat "What is the system status?"
```

### 3. Batch CSV Processing
```bash
python cli.py batch -i sample.csv -o results.csv
```

### 4. Verify Audit Trail Integrity
```bash
python cli.py verify-audit
```

### 5. Launch REST API Server
```bash
python cli.py serve --host 127.0.0.1 --port 8000
```

### Parameter Reference
- `--task-id`: Unique task/case identifier (required, max 128 chars).
- `--target`: Target identifier (required, max 256 chars).
- `--primary`: Primary measurement value (float, required).
- `--secondary`: Secondary metric (float, default 0.0).
- `--critical`: Flag for critical/emergency escalation.
- `--status`: Status descriptor (default "NOMINAL", max 128 chars).
- `-i/--input`: Input CSV file path for batch mode (must be within project directory).
- `-o/--output`: Output CSV file path for batch mode (must be within project directory).

### Input Data Schema

| Field | Type | Description | Requirement |
|:------|:-----|:------------|:------------|
| `task_id` | string | Unique task / case identifier | Required, max 128 chars |
| `target_identifier` | string | Entity, patient key, or genomic target | Required, max 256 chars |
| `primary_metric` | float | Primary domain measurement or score | Required |
| `secondary_metric` | float | Secondary kinetic or confidence score | Optional (default 0.0) |
| `is_critical_flag` | boolean | Emergency escalation trigger | Optional (default false) |
| `status_descriptor` | string | Status code or phenotype descriptor | Optional (default "NOMINAL") |

---

## 🛡️ Security & Enterprise Architecture

* **Zero-PHI Outbound Interceptor:** Active regex inspection blocking SSNs, MRNs, phone numbers, emails, and patient identifiers.
* **Tamper-Evident HMAC-SHA256 Audit Trail:** Chained, cryptographically signed logs for every evaluation and state transition.
* **Secure Key Management:** HMAC audit key sourced from `AUDIT_SECRET_KEY` environment variable; generates a cryptographically secure random key at runtime if not set (with warning).
* **Path Traversal Protection:** Batch CLI validates that input/output file paths remain within the project working directory.
* **Input Validation:** All string fields are stripped, length-limited, and checked for path traversal attempts.
* **Air-Gapped LLM Reasoning Adapter:** Agnostic integration for local Ollama instances, Claude, OpenAI, and deterministic test mocks.
* **Active Learning Bayesian Calibration:** Dynamic tracker updating worker reliability weights.
* **FastAPI & Prometheus Telemetry:** Exposes REST endpoints and operational Prometheus metrics (`/metrics`).

### Environment Variables

| Variable | Description | Default |
|:---------|:------------|:--------|
| `AUDIT_SECRET_KEY` | Secret key for HMAC-SHA256 audit trail signing | Random ephemeral key (not persisted) |
| `MODEL_PROVIDER` | LLM provider (`mock`, `ollama`, `claude`, `openai`) | `mock` |

---

## 🧪 Testing & Verification

Run the automated test suite:

```bash
pytest -v
```

Execute high-throughput batch simulation benchmarks:

```bash
python simulator.py --tasks 1000 --concurrency 8
```

---

## 🐳 Container Deployment

```bash
docker build -t long-read-nanopore-methylation-agent .
docker run -p 8000:8000 long-read-nanopore-methylation-agent
```
