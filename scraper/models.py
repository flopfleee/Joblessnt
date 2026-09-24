from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class Job:
    title: str
    company: str
    location: str
    description: Optional[str]
    job_type: Optional[str]
    duration_months: Optional[int]
    salary_min: Optional[int]
    salary_max: Optional[int]
    salary_currency: str
    work_mode: Optional[str]
    deadline: Optional[date]
    application_url: str
    source_job_id: Optional[str]
    source_url: Optional[str]