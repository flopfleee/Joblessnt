"""
Generic scraper for companies that host their careers site on Workday
(myworkdayjobs.com). Workday renders its job board client-side, but the
page is backed by a JSON API ("CXS") that we can call directly — no
browser/Playwright needed, which is far faster and more reliable than
screen-scraping.

How to find a company's config
-------------------------------
Open the company's careers site, e.g.:

    https://ag.wd3.myworkdayjobs.com/Airbus/job/Filton/Software-Engineering-Placement--125-months-_JR10429196
              ^^         ^^^ ^^^^^^
              tenant     |   site
                       wd_host

    tenant   = "ag"       (subdomain before .wd3.myworkdayjobs.com)
    wd_host  = "wd3"      (the wdN part)
    site     = "Airbus"   (first path segment after the domain)

The search/listing API lives at:
    POST https://{tenant}.{wd_host}.myworkdayjobs.com/wday/cxs/{tenant}/{site}/jobs

Individual job detail lives at:
    GET https://{tenant}.{wd_host}.myworkdayjobs.com/wday/cxs/{tenant}/{site}{externalPath}

NOTE: Workday tenants can customise field names slightly (extra custom
questions, different bullet fields, etc). If a company's jobs come back
looking wrong, open browser devtools -> Network tab -> filter "cxs" while
browsing their careers site, and compare the real response shape against
the parsing below.
"""

import re
from dataclasses import dataclass

import requests
from datetime import date
from models import Job
from normalizer import normalize_job


HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
    ),
}

PAGE_SIZE = 20


@dataclass
class WorkdayConfig:
    tenant: str            # e.g. "ag"
    wd_host: str           # e.g. "wd3"
    site: str              # e.g. "Airbus"
    company_name: str      # e.g. "Airbus" (display name for our DB)
    company_website: str | None = None
    search_text: str = ""  # optional keyword filter, e.g. "placement"

    @property
    def base_url(self) -> str:
        return f"https://{self.tenant}.{self.wd_host}.myworkdayjobs.com"

    @property
    def jobs_endpoint(self) -> str:
        return f"{self.base_url}/wday/cxs/{self.tenant}/{self.site}/jobs"

    def job_detail_url(self, external_path: str) -> str:
        return f"{self.base_url}/wday/cxs/{self.tenant}/{self.site}{external_path}"

    def public_job_url(self, external_path: str) -> str:
        return f"{self.base_url}/{self.site}{external_path}"


def fetch_job_list(config: WorkdayConfig) -> list[dict]:
    """Fetch every job posting summary from the listing API (paginated)."""

    postings = []
    offset = 0

    with requests.Session() as session:
        session.headers.update(HEADERS)

        while True:
            response = session.post(
                config.jobs_endpoint,
                json={
                    "appliedFacets": {},
                    "limit": PAGE_SIZE,
                    "offset": offset,
                    "searchText": config.search_text,
                },
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()

            batch = data.get("jobPostings", [])
            postings.extend(batch)

            total = data.get("total", len(postings))
            offset += PAGE_SIZE

            if not batch or offset >= total:
                break

    return postings


def fetch_job_detail(config: WorkdayConfig, external_path: str) -> dict:
    with requests.Session() as session:
        session.headers.update(HEADERS)
        response = session.get(config.job_detail_url(external_path), timeout=30)
        response.raise_for_status()
        return response.json()


# ------------------------------------------------------------------
# Parsing helpers
# ------------------------------------------------------------------

DURATION_PATTERN = re.compile(r"(\d+(?:\.\d+)?)\s*[- ]?month", re.IGNORECASE)


def parse_duration_months(text: str) -> float | None:
    match = DURATION_PATTERN.search(text)
    if not match:
        return None
    return float(match.group(1))


def parse_job_type(title: str, duration_months: float | None) -> str:
    lowered = title.lower()

    if "placement" in lowered or "year in industry" in lowered or "industrial" in lowered:
        return "placement"
    if "intern" in lowered or "summer" in lowered:
        return "internship"
    if "graduate" in lowered:
        return "graduate"
    if duration_months and duration_months >= 9:
        return "placement"
    return "internship"


def parse_locations(location_text: str) -> list[tuple[str, str | None, str]]:
    """Workday location strings look like "Filton, United Kingdom" or list
    multiple options separated by " or ", e.g.
    "Bristol, United Kingdom or Broughton, United Kingdom"."""

    if not location_text:
        return []

    parts = re.split(r"\s+or\s+", location_text, flags=re.IGNORECASE)
    locations = []

    for part in parts:
        part = part.strip()
        if not part:
            continue

        pieces = [p.strip() for p in part.split(",")]
        city = pieces[0] if pieces else part
        country = pieces[-1] if len(pieces) > 1 else "United Kingdom"
        region = pieces[1] if len(pieces) > 2 else None

        locations.append((city, region, country))

    return locations

def parse_date(value: str | None) -> date | None:
    if not value:
        return None

    try:
        return date.fromisoformat(value[:10])
    except ValueError:
        return None

SALARY_PATTERN = re.compile(
    r"salary\s*:\s*£\s*([\d,]+)",
    re.IGNORECASE,
)


def parse_salary(text: str | None) -> tuple[int | None, int | None]:
    if not text:
        return None, None

    match = SALARY_PATTERN.search(text)

    if not match:
        return None, None

    salary = int(match.group(1).replace(",", ""))

    return salary, salary

def parse_work_mode(text: str | None) -> str | None:
    if not text:
        return None

    lowered = text.lower()

    if "hybrid" in lowered:
        return "hybrid"

    if "remote" in lowered:
        return "remote"

    if "on-site" in lowered or "onsite" in lowered:
        return "onsite"

    return None


def strip_html(html: str | None) -> str | None:
    if not html:
        return None
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"\s+", " ", text)
    return text.strip() or None

def repair_mojibake(text: str | None) -> str | None:
    """Repair text that has been incorrectly decoded through multiple encodings."""
    if not text:
        return text

    # First layer: CP850 mojibake -> the intermediate UTF-8-looking text
    try:
        text = text.encode("cp850").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        pass

    # Second layer: CP850 mojibake -> actual Unicode
    try:
        text = text.encode("cp850").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        pass

    return text

def is_relevant_opportunity(title: str, description: str | None) -> bool:
    """
    Decide whether a job looks like a student, placement,
    internship, or graduate opportunity.

    We primarily trust the title because job descriptions can
    contain generic words such as "student" or "graduate".
    """

    title_lower = title.lower()

    title_keywords = [
        "placement",
        "industrial placement",
        "year in industry",
        "internship",
        "intern ",
        "summer intern",
        "student placement",
        "graduate programme",
        "graduate program",
        "graduate role",
        "graduate engineer",
        "early careers",
        "early career",
    ]

    return any(keyword in title_lower for keyword in title_keywords)

def to_job(config: WorkdayConfig, posting: dict, detail: dict) -> Job:
    info = detail.get("jobPostingInfo", {})
    title = info.get("title") or posting.get("title", "")
    description = strip_html(info.get("jobDescription"))
    description = repair_mojibake(description)
    external_path = info.get("externalPath") or posting.get("externalPath", "")
    deadline = parse_date(info.get("endDate"))
    duration_months = parse_duration_months(title) or parse_duration_months(description or "")
    job_type = parse_job_type(title, duration_months)
    salary_min, salary_max = parse_salary(description)
    location_text = info.get("location") or posting.get("locationsText", "")
    work_mode = parse_work_mode(description)
    return normalize_job(
        title=title,
        company=config.company_name,
        location=location_text,
        application_url=config.public_job_url(external_path),
        description=description,
        job_type=job_type,
        duration_months=duration_months,
        deadline=deadline,
        work_mode=work_mode,
        salary_min=salary_min,
        salary_max=salary_max,
        source_job_id=info.get("jobReqId") or _bullet_req_id(posting),
        source_url=config.public_job_url(external_path),
    )


def _bullet_req_id(posting: dict) -> str | None:
    for bullet in posting.get("bulletFields", []):
        if re.match(r"^[A-Z]+-?\d+$", bullet):
            return bullet
    return None


def scrape(config: WorkdayConfig) -> list[Job]:
    """Scrape and filter current jobs for a Workday-hosted company."""
    jobs = []

    for posting in fetch_job_list(config):
        external_path = posting.get("externalPath")

        if not external_path:
            continue

        detail = fetch_job_detail(config, external_path)

        info = detail.get("jobPostingInfo", {})

        title = info.get("title") or posting.get("title", "")
        description = strip_html(info.get("jobDescription"))

        if not is_relevant_opportunity(title, description):
            continue

        jobs.append(to_job(config, posting, detail))

    return jobs