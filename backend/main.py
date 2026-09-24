from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import get_connection

app = FastAPI(
    title="Internship Finder API",
    description="API for internships and placement years",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "Internship Finder API is running"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/database-health")
def database_health():
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()

    return {"database": "connected", "result": result[0]}


@app.get("/jobs")
def get_jobs(
    subject: Optional[str] = None,
    location: Optional[str] = None,
    job_type: Optional[str] = None,
):
    query = """
        SELECT DISTINCT
            jobs.id,
            jobs.title,
            jobs.description,
            jobs.type,
            jobs.duration_months,
            jobs.salary_min,
            jobs.salary_max,
            jobs.salary_currency,
            jobs.work_mode,
            jobs.deadline,
            jobs.application_url,
            companies.name AS company,
            locations.city,
            locations.region,
            locations.country
        FROM jobs
        JOIN companies ON jobs.company_id = companies.id
        LEFT JOIN job_subjects ON jobs.id = job_subjects.job_id
        LEFT JOIN subjects ON job_subjects.subject_id = subjects.id
        LEFT JOIN job_locations ON jobs.id = job_locations.job_id
        LEFT JOIN locations ON job_locations.location_id = locations.id
        WHERE jobs.is_active = TRUE
    """

    parameters = []

    if subject:
        query += " AND subjects.name ILIKE %s"
        parameters.append(f"%{subject}%")

    if location:
        query += " AND locations.city ILIKE %s"
        parameters.append(f"%{location}%")

    if job_type:
        query += " AND jobs.type = %s"
        parameters.append(job_type)

    query += " ORDER BY jobs.deadline ASC NULLS LAST"

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query, parameters)
            rows = cursor.fetchall()

            jobs = []

            for row in rows:
                jobs.append({
                    "id": row[0],
                    "title": row[1],
                    "description": row[2],
                    "type": row[3],
                    "duration_months": row[4],
                    "salary_min": row[5],
                    "salary_max": row[6],
                    "salary_currency": row[7],
                    "work_mode": row[8],
                    "deadline": row[9],
                    "application_url": row[10],
                    "company": row[11],
                    "city": row[12],
                    "region": row[13],
                    "country": row[14],
                })

    return {
        "count": len(jobs),
        "jobs": jobs,
    }