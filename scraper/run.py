"""
Scraper entrypoint. Run with:

    cd scraper
    venv\\Scripts\\activate   (or source venv/bin/activate on mac/linux)
    python run.py

For each configured source, this fetches current postings, upserts them
into the database, and marks any previously-seen job from that source that
didn't show up this run as inactive (closed/expired).
"""

from database import (
    get_connection,
    get_or_create_company,
    get_or_create_source,
    get_or_create_location,
    get_or_create_subject,
    upsert_job,
    set_job_locations,
    set_job_subjects,
    deactivate_stale_jobs,
)
from sources.companies import WORKDAY_COMPANIES
from sources.workday import scrape as scrape_workday, parse_locations
from subject_tagger import tag_subjects


def run_workday_source(connection, source_id: int, config) -> None:
    print(f"  Scraping {config.company_name}...")

    try:
        jobs = scrape_workday(config)
    except Exception as error:
        print(f"    Failed to scrape {config.company_name}: {error}")
        return

    print(f"    Found {len(jobs)} posting(s)")

    seen_job_ids = set()

    with connection.cursor() as cursor:
        company_id = get_or_create_company(cursor, config.company_name, config.company_website)

        for job in jobs:
            job_id = upsert_job(cursor, job, source_id, company_id)
            seen_job_ids.add(job_id)

            location_ids = []
            for city, region, country in parse_locations(job.location):
                location_id = get_or_create_location(cursor, city, region, country)
                if location_id:
                    location_ids.append(location_id)
            set_job_locations(cursor, job_id, location_ids)

            subject_ids = [
                get_or_create_subject(cursor, name)
                for name in tag_subjects(job.title, job.description)
            ]
            set_job_subjects(cursor, job_id, subject_ids)

        deactivated = deactivate_stale_jobs(cursor, source_id, seen_job_ids)

    connection.commit()
    print(f"    Upserted {len(seen_job_ids)}, deactivated {deactivated} stale posting(s)")


def main():
    connection = get_connection()

    try:
        print("Workday sources:")

        for config in WORKDAY_COMPANIES:
         with connection.cursor() as cursor:
              source_id = get_or_create_source(
                   cursor,
                f"{config.company_name} Careers",
                   config.company_website,
              )
        connection.commit()

        run_workday_source(connection, source_id, config)
    finally:
        connection.close()

    print("Done.")


if __name__ == "__main__":
    main()
