# PHASE 18: PRODUCTION CONFIGURATION & ENVIRONMENT MATRIX

**Audit Date:** 2026-09-27  
**Configuration Management:** Pydantic v2 `BaseSettings` + Environment Variable Injection  
**Status:** `CONFIGURATION_MATRIX_VERIFIED`  

---

### 1. Environment Separation Tiering

The platform enforces strict decoupling across four deployment tiers:

| Parameter | Development (`dev`) | Testing (`test`) | Staging (`staging`) | Production (`prod`) |
|---|---|---|---|---|
| **`ENVIRONMENT`** | `development` | `testing` | `staging` | `production` |
| **`DATABASE_URL`** | `sqlite:///./platform/storage/scidata_platform.db` | `sqlite:///:memory:` | `postgresql://scidata_stg:...@stg-db:5432/scidata` | `postgresql://${DB_USER}:${DB_PASS}@prod-db:5432/scidata_prod` |
| **`SECRET_KEY`** | Default dev key (tracked) | ephemeral random key | Injected via Vault / Secrets Manager | Injected via Cloud KMS / Vault |
| **`ACCESS_TOKEN_EXPIRE`** | 1440 min (24 hours) | 15 min | 60 min | 60 min |
| **`RATE_LIMIT_MAX_REQ`** | 600 / min | Unlimited | 300 / min | 300 / min |
| **`STORAGE_BACKEND`** | Local Filesystem (`LOCAL`) | Local Temporary (`LOCAL`) | S3-Compatible (MinIO cluster) | S3-Compatible / Private Ceph Store |
| **`DEBUG`** | `True` | `False` | `False` | `False` |
| **`LOG_LEVEL`** | `DEBUG` | `WARNING` | `INFO` | `INFO` (JSON formatted) |
| **`CORS_ORIGINS`** | `["*"]` | `["*"]` | `["https://staging.scidata.internal"]` | Explicit domain whitelist (No wildcards) |

---

### 2. Secret Hygiene Protocol

- **Source Control Gate:** Zero production credentials, API tokens, private SSH/RSA keys, or database passwords are committed to Git.
- **Runtime Secret Ingestion:** The production container (`scientific-platform-api:v2.0.0`) reads secrets strictly from environment variables or mounted secret files (`/run/secrets/`), preventing leaks in image layers or build logs.
- **Template Reference:** `.env.example` provides the exact schema and type definitions without sensitive values.
