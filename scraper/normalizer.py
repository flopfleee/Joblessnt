from datetime import date

from models import Job


def normalize_job(
    title: str,
    company: str,
    location: str,
    application_url: str,
    description: str | None = None,
    job_type: str | None = None,
    duration_months: int | None = None,
    salary_min: int | None = None,
    salary_max: int | None = None,
    work_mode: str | None = None,
    deadline: date | None = None,
    source_job_id: str | None = None,
    source_url: str | None = None,
) -> Job:
    return Job(
        title=title.strip(),
        company=company.strip(),
        location=location.strip(),
        description=description.strip() if description else None,
        job_type=job_type,
        duration_months=duration_months,
        salary_min=salary_min,
        salary_max=salary_max,
        salary_currency="GBP",
        work_mode=work_mode,
        deadline=deadline,
        application_url=application_url.strip(),
        source_job_id=source_job_id,
        source_url=source_url,
    )