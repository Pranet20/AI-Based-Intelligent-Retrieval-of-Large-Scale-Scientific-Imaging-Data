-- Publication-Grade PostgreSQL Database Schema for Phase 8 Production Platform
-- Platform: AI-Powered Scientific Image Data Management Platform

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'RESEARCHER', -- ADMIN, RESEARCHER, REVIEWER
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS projects (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    created_by INT REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS images (
    id SERIAL PRIMARY KEY,
    project_id INT REFERENCES projects(id) ON DELETE CASCADE,
    original_filename VARCHAR(255) NOT NULL,
    storage_path VARCHAR(500) NOT NULL UNIQUE,
    thumbnail_path VARCHAR(500),
    sha256 VARCHAR(64) NOT NULL UNIQUE,
    mime_type VARCHAR(100) NOT NULL,
    width INT,
    height INT,
    file_size BIGINT NOT NULL,
    processing_status VARCHAR(50) NOT NULL DEFAULT 'PENDING', -- PENDING, PROCESSING, READY, FAILED
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS image_metadata (
    id SERIAL PRIMARY KEY,
    image_id INT UNIQUE REFERENCES images(id) ON DELETE CASCADE,
    microscope VARCHAR(100),
    detector VARCHAR(50),
    accelerating_voltage_kv FLOAT,
    magnification FLOAT,
    pixel_size_nm FLOAT,
    beam_current_na FLOAT,
    dwell_time_us FLOAT,
    working_distance_mm FLOAT,
    chamber_pressure_pa FLOAT,
    metadata_source VARCHAR(50) NOT NULL DEFAULT 'embedded', -- embedded, manual, dataset, unknown
    metadata_completeness FLOAT NOT NULL DEFAULT 0.0,
    raw_metadata_json JSONB,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS model_versions (
    id SERIAL PRIMARY KEY,
    model_id VARCHAR(100) NOT NULL UNIQUE,
    version VARCHAR(50) NOT NULL,
    architecture VARCHAR(100) NOT NULL,
    embedding_dimension INT NOT NULL,
    weights_hash VARCHAR(64) NOT NULL,
    preprocessing_version VARCHAR(50) NOT NULL,
    source VARCHAR(255) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS embeddings (
    id SERIAL PRIMARY KEY,
    image_id INT REFERENCES images(id) ON DELETE CASCADE,
    model_id INT REFERENCES model_versions(id),
    embedding_type VARCHAR(50) NOT NULL, -- dinov2_base, phase4_adapted
    embedding_vector JSONB NOT NULL,
    l2_normalized BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(image_id, model_id, embedding_type)
);

CREATE TABLE IF NOT EXISTS quality_profiles (
    id SERIAL PRIMARY KEY,
    image_id INT UNIQUE REFERENCES images(id) ON DELETE CASCADE,
    laplacian_variance FLOAT,
    edge_density FLOAT,
    shannon_entropy FLOAT,
    dynamic_range FLOAT,
    clipping_ratio FLOAT,
    high_freq_fft_ratio FLOAT,
    composite_quality_risk FLOAT NOT NULL,
    quality_label VARCHAR(50) NOT NULL DEFAULT 'NOMINAL', -- NOMINAL, RISK_FLAGGED
    evaluated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS duplicate_profiles (
    id SERIAL PRIMARY KEY,
    image_id INT UNIQUE REFERENCES images(id) ON DELETE CASCADE,
    phash VARCHAR(64),
    dhash VARCHAR(64),
    duplicate_status VARCHAR(50) NOT NULL DEFAULT 'NO_DECLARED_REDUNDANCY_DETECTED', -- EXACT_DUPLICATE, POTENTIAL_NEAR_DUPLICATE, NO_DECLARED_REDUNDANCY_DETECTED
    matched_image_id INT REFERENCES images(id) ON DELETE SET NULL,
    similarity_score FLOAT,
    match_stage VARCHAR(50),
    evaluated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS provenance_events (
    id SERIAL PRIMARY KEY,
    image_id INT REFERENCES images(id) ON DELETE CASCADE,
    event_type VARCHAR(100) NOT NULL, -- UPLOAD, METADATA_EXTRACTION, QUALITY_ANALYSIS, EMBEDDING_GENERATION, DUPLICATE_ANALYSIS, INDEXING, SEARCH, REVIEW
    software_version VARCHAR(50) NOT NULL,
    model_version VARCHAR(50),
    parameters JSONB,
    status VARCHAR(50) NOT NULL DEFAULT 'SUCCESS',
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS retrieval_queries (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    query_image_id INT REFERENCES images(id),
    query_mode VARCHAR(50) NOT NULL DEFAULT 'visual_only',
    top_k INT NOT NULL DEFAULT 10,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS retrieval_results (
    id SERIAL PRIMARY KEY,
    query_id INT REFERENCES retrieval_queries(id) ON DELETE CASCADE,
    rank INT NOT NULL,
    result_image_id INT REFERENCES images(id) ON DELETE CASCADE,
    similarity_score FLOAT NOT NULL,
    metadata_summary JSONB,
    duplicate_status VARCHAR(50),
    novelty_score FLOAT
);

CREATE TABLE IF NOT EXISTS review_items (
    id SERIAL PRIMARY KEY,
    image_id INT REFERENCES images(id) ON DELETE CASCADE,
    reviewer_id INT REFERENCES users(id),
    decision VARCHAR(50) NOT NULL, -- KEEP, REVIEW_LATER, DUPLICATE, LOW_QUALITY, INTERESTING_NOVEL, INCORRECT_METADATA
    comment TEXT,
    priority FLOAT NOT NULL DEFAULT 0.0,
    algorithmic_recommendation VARCHAR(50),
    status VARCHAR(50) NOT NULL DEFAULT 'PENDING', -- PENDING, COMPLETED
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    reviewed_at TIMESTAMP WITH TIME ZONE
);

CREATE TABLE IF NOT EXISTS processing_runs (
    id SERIAL PRIMARY KEY,
    run_id VARCHAR(100) UNIQUE NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'RUNNING',
    items_total INT NOT NULL DEFAULT 0,
    items_processed INT NOT NULL DEFAULT 0,
    errors JSONB,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(100) NOT NULL,
    resource_id INT,
    model_version VARCHAR(50),
    parameters JSONB,
    result_status VARCHAR(50) NOT NULL DEFAULT 'SUCCESS',
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_images_project_id ON images(project_id);
CREATE INDEX IF NOT EXISTS idx_images_sha256 ON images(sha256);
CREATE INDEX IF NOT EXISTS idx_embeddings_image_id ON embeddings(image_id);
CREATE INDEX IF NOT EXISTS idx_provenance_image_id ON provenance_events(image_id);
CREATE INDEX IF NOT EXISTS idx_review_items_status ON review_items(status);
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id);
