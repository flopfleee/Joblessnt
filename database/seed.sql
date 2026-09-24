-- ============================================
-- Test data for Internship Finder
-- ============================================

-- Subjects
INSERT INTO subjects (name)
VALUES
    ('Computer Science'),
    ('Software Engineering'),
    ('Finance'),
    ('Business'),
    ('Engineering'),
    ('Marketing'),
    ('Mathematics')
ON CONFLICT (name) DO NOTHING;


-- Companies
INSERT INTO companies (name, website)
VALUES
    ('TechCorp', 'https://example.com'),
    ('FinanceCo', 'https://example.com'),
    ('Engineering Ltd', 'https://example.com');


-- Sources
INSERT INTO sources (name, website)
VALUES
    ('Example Careers', 'https://example.com')
ON CONFLICT (name) DO NOTHING;


-- Locations
INSERT INTO locations (city, region, country)
VALUES
    ('London', 'England', 'UK'),
    ('Manchester', 'England', 'UK'),
    ('Birmingham', 'England', 'UK')
;


-- Jobs
INSERT INTO jobs (
    company_id,
    source_id,
    title,
    description,
    type,
    duration_months,
    salary_min,
    salary_max,
    salary_currency,
    work_mode,
    deadline,
    application_url,
    source_job_id,
    source_url
)
VALUES

(
    (SELECT id FROM companies WHERE name = 'TechCorp'),
    (SELECT id FROM sources WHERE name = 'Example Careers'),
    'Software Engineering Industrial Placement',
    'A 12-month placement working with a software engineering team.',
    'placement',
    12,
    28000,
    32000,
    'GBP',
    'hybrid',
    '2026-11-30',
    'https://example.com/software-placement',
    'TEST-001',
    'https://example.com'
),

(
    (SELECT id FROM companies WHERE name = 'TechCorp'),
    (SELECT id FROM sources WHERE name = 'Example Careers'),
    'Summer Software Engineering Internship',
    'A summer internship for students interested in software engineering.',
    'internship',
    3,
    25000,
    28000,
    'GBP',
    'hybrid',
    '2027-01-15',
    'https://example.com/software-internship',
    'TEST-002',
    'https://example.com'
),

(
    (SELECT id FROM companies WHERE name = 'FinanceCo'),
    (SELECT id FROM sources WHERE name = 'Example Careers'),
    'Finance Industrial Placement',
    'A year-long placement within a finance team.',
    'placement',
    12,
    26000,
    30000,
    'GBP',
    'onsite',
    '2026-12-15',
    'https://example.com/finance-placement',
    'TEST-003',
    'https://example.com'
),

(
    (SELECT id FROM companies WHERE name = 'Engineering Ltd'),
    (SELECT id FROM sources WHERE name = 'Example Careers'),
    'Mechanical Engineering Placement',
    'A 12-month engineering placement.',
    'placement',
    12,
    24000,
    28000,
    'GBP',
    'onsite',
    '2026-12-01',
    'https://example.com/engineering-placement',
    'TEST-004',
    'https://example.com'
);


-- Connect jobs to subjects

INSERT INTO job_subjects (job_id, subject_id)
VALUES
(
    (SELECT id FROM jobs WHERE source_job_id = 'TEST-001'),
    (SELECT id FROM subjects WHERE name = 'Computer Science')
),
(
    (SELECT id FROM jobs WHERE source_job_id = 'TEST-001'),
    (SELECT id FROM subjects WHERE name = 'Software Engineering')
),
(
    (SELECT id FROM jobs WHERE source_job_id = 'TEST-002'),
    (SELECT id FROM subjects WHERE name = 'Computer Science')
),
(
    (SELECT id FROM jobs WHERE source_job_id = 'TEST-002'),
    (SELECT id FROM subjects WHERE name = 'Software Engineering')
),
(
    (SELECT id FROM jobs WHERE source_job_id = 'TEST-003'),
    (SELECT id FROM subjects WHERE name = 'Finance')
),
(
    (SELECT id FROM jobs WHERE source_job_id = 'TEST-003'),
    (SELECT id FROM subjects WHERE name = 'Business')
),
(
    (SELECT id FROM jobs WHERE source_job_id = 'TEST-004'),
    (SELECT id FROM subjects WHERE name = 'Engineering')
),
(
    (SELECT id FROM jobs WHERE source_job_id = 'TEST-004'),
    (SELECT id FROM subjects WHERE name = 'Mathematics')
);


-- Connect jobs to locations

INSERT INTO job_locations (job_id, location_id)
VALUES
(
    (SELECT id FROM jobs WHERE source_job_id = 'TEST-001'),
    (SELECT id FROM locations WHERE city = 'London')
),
(
    (SELECT id FROM jobs WHERE source_job_id = 'TEST-002'),
    (SELECT id FROM locations WHERE city = 'London')
),
(
    (SELECT id FROM jobs WHERE source_job_id = 'TEST-003'),
    (SELECT id FROM locations WHERE city = 'London')
),
(
    (SELECT id FROM jobs WHERE source_job_id = 'TEST-004'),
    (SELECT id FROM locations WHERE city = 'Birmingham')
);