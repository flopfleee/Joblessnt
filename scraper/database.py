import os
from datetime import datetime, timezone

import psycopg
from dotenv import load_dotenv

from models import Job


load_dotenv("../backend/.env")

DATABASE_URL = os.getenv("DATABASE_URL")


def get_connection():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL is not configured")

    return psycopg.connect(DATABASE_URL)


# ------------------------------------------------------------------
# Get-or-create helpers
# ------------------------------------------------------------------

def get_or_create_company(cursor, name: str, website: str | None = None) -> int:
    cursor.execute("SELECT id FROM companies WHERE name = %s", (name,))
    row = cursor.fetchone()

    if row:
        return row[0]

    cursor.execute(
        "INSERT INTO companies (name, website) VALUES (%s, %s) RETURNING id",
        (name, website),
    )
    return cursor.fetchone()[0]


def get_or_create_source(cursor, name: str, website: str | None = None) -> int:
    cursor.execute("SELECT id FROM sources WHERE name = %s", (name,))
    row = cursor.fetchone()

    if row:
        return row[0]

    cursor.execute(
        "INSERT INTO sources (name, website) VALUES (%s, %s) RETURNING id",
        (name, website),
    )
    return cursor.fetchone()[0]


def get_or_create_location(
    cursor, city: str | None, region: str | None = None, country: str | None = None
) -> int | None:
    if not city and not country:
        return None

    cursor.execute(
        """
        SELECT id FROM locations
        WHERE city IS NOT DISTINCT FROM %s
          AND region IS NOT DISTINCT FROM %s
          AND country IS NOT DISTINCT FROM %s
        """,
        (city, region, country),
    )
    row = cursor.fetchone()

    if row:
        return row[0]

    cursor.execute(
        "INSERT INTO locations (city, region, country) VALUES (%s, %s, %s) RETURNING id",
        (city, region, country),
    )
    return cursor.fetchone()[0]


def get_or_create_subject(cursor, name: str) -> int:
    cursor.execute("SELECT id FROM subjects WHERE name = %s", (name,))
    row = cursor.fetchone()

    if row:
        return row[0]

    cursor.execute(
        "INSERT INTO subjects (name) VALUES (%s) RETURNING id",
        (name,),
    )
    return cursor.fetchone()[0]


# ------------------------------------------------------------------
# Job upsert
# ------------------------------------------------------------------

def _find_existing_job_id(
    cursor, source_id: int, source_job_id: str | None, application_url: str
) -> int | None:
    if source_job_id:
        cursor.execute(
            "SELECT id FROM jobs WHERE source_id = %s AND source_job_id = %s",
            (source_id, source_job_id),
        )
        row = cursor.fetchone()
        if row:
            return row[0]

    cursor.execute(
        "SELECT id FROM jobs WHERE source_id = %s AND application_url = %s",
        (source_id, application_url),
    )
    row = cursor.fetchone()
    return row[0] if row else None


def upsert_job(cursor, job: Job, source_id: int, company_id: int) -> int:
    """Insert a new job, or update an existing one (matched on source +
    source_job_id, falling back to source + application_url) and mark it
    as seen. Returns the job's id."""

    existing_id = _find_existing_job_id(
        cursor, source_id, job.source_job_id, job.application_url
    )

    if existing_id is None:
        cursor.execute(
            """
            INSERT INTO jobs (
                company_id, source_id, title, description, type,
                duration_months, salary_min, salary_max, salary_currency,
                work_mode, deadline, application_url, source_job_id, source_url,
                is_active
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, TRUE
            )
            RETURNING id
            """,
            (
                company_id, source_id, job.title, job.description, job.job_type,
                job.duration_months, job.salary_min, job.salary_max, job.salary_currency,
                job.work_mode, job.deadline, job.application_url, job.source_job_id,
                job.source_url,
            ),
        )
        return cursor.fetchone()[0]

    cursor.execute(
        """
        UPDATE jobs SET
            company_id = %s,
            title = %s,
            description = %s,
            type = %s,
            duration_months = %s,
            salary_min = %s,
            salary_max = %s,
            salary_currency = %s,
            work_mode = %s,
            deadline = %s,
            application_url = %s,
            source_url = %s,
            last_seen_at = %s,
            is_active = TRUE,
            updated_at = %s
        WHERE id = %s
        """,
        (
            company_id, job.title, job.description, job.job_type,
            job.duration_months, job.salary_min, job.salary_max, job.salary_currency,
            job.work_mode, job.deadline, job.application_url, job.source_url,
            datetime.now(timezone.utc), datetime.now(timezone.utc), existing_id,
        ),
    )
    return existing_id


def set_job_locations(cursor, job_id: int, location_ids: list[int]) -> None:
    cursor.execute("DELETE FROM job_locations WHERE job_id = %s", (job_id,))

    for location_id in location_ids:
        cursor.execute(
            "INSERT INTO job_locations (job_id, location_id) VALUES (%s, %s) "
            "ON CONFLICT DO NOTHING",
            (job_id, location_id),
        )


def set_job_subjects(cursor, job_id: int, subject_ids: list[int]) -> None:
    cursor.execute("DELETE FROM job_subjects WHERE job_id = %s", (job_id,))

    for subject_id in subject_ids:
        cursor.execute(
            "INSERT INTO job_subjects (job_id, subject_id) VALUES (%s, %s) "
            "ON CONFLICT DO NOTHING",
            (job_id, subject_id),
        )


def deactivate_stale_jobs(cursor, source_id: int, seen_job_ids: set[int]) -> int:
    """Mark jobs from this source as inactive if they weren't seen in the
    current scrape run (they've likely closed/expired). Returns the count
    of jobs deactivated."""

    if seen_job_ids:
        cursor.execute(
    """
    UPDATE jobs
    SET is_active = FALSE, updated_at = %s
    WHERE source_id = %s
      AND is_active = TRUE
      AND id <> ALL(%s)
    """,
    (datetime.now(timezone.utc), source_id, list(seen_job_ids)),
)
    else:
        cursor.execute(
            """
            UPDATE jobs SET is_active = FALSE, updated_at = %s
            WHERE source_id = %s AND is_active = TRUE
            """,
            (datetime.now(timezone.utc), source_id),
        )

    return cursor.rowcount
