-- ============================================
-- Internship Finder Database
-- ============================================

-- Companies
CREATE TABLE companies (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    website TEXT,
    logo_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Job sources
CREATE TABLE sources (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    website TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Locations
CREATE TABLE locations (
    id SERIAL PRIMARY KEY,
    city VARCHAR(255),
    region VARCHAR(255),
    country VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Subjects
CREATE TABLE subjects (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE
);

-- Jobs
CREATE TABLE jobs (
    id SERIAL PRIMARY KEY,

    company_id INTEGER REFERENCES companies(id),
    source_id INTEGER REFERENCES sources(id),

    title VARCHAR(500) NOT NULL,
    description TEXT,

    type VARCHAR(50),
    duration_months INTEGER,

    salary_min INTEGER,
    salary_max INTEGER,
    salary_currency VARCHAR(10) DEFAULT 'GBP',

    work_mode VARCHAR(50),

    deadline DATE,
    application_url TEXT NOT NULL,

    source_job_id VARCHAR(500),
    source_url TEXT,

    first_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    is_active BOOLEAN DEFAULT TRUE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Many-to-many relationship:
-- jobs <-> subjects
CREATE TABLE job_subjects (
    job_id INTEGER REFERENCES jobs(id) ON DELETE CASCADE,
    subject_id INTEGER REFERENCES subjects(id) ON DELETE CASCADE,

    PRIMARY KEY (job_id, subject_id)
);

-- Many-to-many relationship:
-- jobs <-> locations
CREATE TABLE job_locations (
    job_id INTEGER REFERENCES jobs(id) ON DELETE CASCADE,
    location_id INTEGER REFERENCES locations(id) ON DELETE CASCADE,

    PRIMARY KEY (job_id, location_id)
);

-- Useful indexes for searching/filtering
CREATE INDEX idx_jobs_type
ON jobs(type);

CREATE INDEX idx_jobs_deadline
ON jobs(deadline);

CREATE INDEX idx_jobs_active
ON jobs(is_active);

CREATE INDEX idx_jobs_company
ON jobs(company_id);

CREATE INDEX idx_jobs_source
ON jobs(source_id);