# Long Read Nanopore Methylation Agent

This repository contains two separate Python **demonstration threshold-evaluation workflows** and a static **modkit bedMethyl summarizer**. The browser tool aggregates existing nanopore base-modification calls; it does **not** infer methylation from raw current traces.

## Browser application

Open [web/index.html](web/index.html) in a modern browser or serve the repository's root directory with a static HTTP server. GitHub Pages can serve the root [index.html](index.html) (which redirects to the application). Files remain on the local device; the browser does not upload or transmit the data.

1. Generate an 18-column, uncompressed bedMethyl file using `modkit pileup`.
2. Choose the file, modification code (`m` = 5mC, `h` = 5hmC), and minimum valid coverage.
3. Select **Analyze file**; review per-chromosome/per-code counts and export summary CSV.
4. **Try example** works without an input file.

The tool accepts UTF-8 tab-separated, 18-column `modkit pileup` bedMethyl files up to 20 MiB. It checks 0-based BED coordinates, integer counts, and the per-row reported modified fraction. Invalid records are counted and skipped, and warnings show up to five errors.

**Computation:** For each chromosome and modification code, the reported percentage is `100 × sum(N_mod) / sum(N_valid_cov)` after filtering. Counts for 5mC and 5hmC are never pooled because their coverage can overlap. Input columns follow the [official modkit pileup specification](https://nanoporetech.github.io/modkit/intro_pileup.html). This is a descriptive, **not differential**, summary and is not a clinical assay or validated diagnostic model.

## Python workflows

The root [cli.py](cli.py) uses `agents/` for generic threshold auditing (25.0 for primary, 12.0 for secondary, or explicit critical flag), a keyword-based descriptor check, an in-memory HMAC audit trail, CSV batch processing, and a FastAPI server.

```bash
python -m pip install -e . pytest
python cli.py audit --task-id TASK-001 --target TARGET-01 --primary 28.5 --secondary 14.2 --critical --status DISCORDANT
python cli.py batch -i sample.csv -o results.csv
python cli.py verify-audit
python cli.py serve --host 127.0.0.1 --port 8000
```

The independent `nanomethyl_sentinel/` package has its own CLI, data model, and three threshold evaluators (primary 25.0, secondary 10.0). Launch with:

```bash
python -m nanomethyl_sentinel.cli audit --primary 29.4 --secondary 15.1
```

The REST server from `python cli.py serve` exposes `/health`, `/metrics`, `/api/audit`, `/api/chat`, and `/api/audit/logs`. The `/metrics` endpoint responds in JSON, not the Prometheus text format. These APIs have **no authentication** and should only be exposed to trusted networks. The LLM factory currently returns deterministic mock responses for every provider selection.

The separate [enrichment.py](enrichment.py) module provides generic threshold simulations named for methylation tasks. It does not implement the biological workflows implied by those names.

## Tests

```bash
python -m pytest -v
node --test tests/test_bedmethyl.cjs
```

GitHub Actions tests Python 3.10–3.12 and Node 22. The Python package requires Python 3.9+ and Pydantic v2, FastAPI, and Uvicorn. The browser tool requires a current JavaScript-enabled browser; no Python runtime, Pyodide, or backend service is needed for its calculations.

## Security and privacy

- The browser analyzer performs local-only file parsing and creates client-side CSV downloads. A Google Font or telemetry service is **not** required.
- The Python audit trail uses HMAC-SHA256 with chain links. It is **process-local** and is not a persistent audit log. Set a private `AUDIT_SECRET_KEY` environment variable to keep a consistent key between process restarts, but note that stored records themselves are not persisted.
- The Python PHI guard uses heuristic regular expressions; it **cannot guarantee de-identification**. Do not submit patient-identifying data to the API or place the API on the public Internet.
- `docker compose up --build` requires `AUDIT_SECRET_KEY` to be set, for example as an exported shell environment variable. Do not commit a real key or store it in a publicly accessible frontend.

## Project status

This is research/development demonstration software. There is no validated nanopore squiggle basecaller, differential methylation pipeline, or regulatory/clinical conformity claim. The static browser summarizer and Python threshold agents are intentionally distinct implementations.

Licensed under [MIT](LICENSE).
