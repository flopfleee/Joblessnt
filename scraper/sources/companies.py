"""
Registry of companies to scrape, grouped by which platform they run their
careers site on. To add a new Workday employer:

  1. Go to their careers site and open a specific job posting.
  2. Read the tenant / wd_host / site out of the URL (see the docstring at
     the top of sources/workday.py for how to do this).
  3. Add a WorkdayConfig entry below.

Not every company uses Workday — Greenhouse, Lever, SmartRecruiters and
iCIMS are other common ATS platforms worth building scrapers for later,
following the same pattern as workday.py (find their JSON API, parse into
Job objects).
"""

from sources.workday import WorkdayConfig


WORKDAY_COMPANIES = [
    WorkdayConfig(
        tenant="ag",
        wd_host="wd3",
        site="Airbus",
        company_name="Airbus",
        company_website="https://www.airbus.com",
        search_text="placement",
    ),

    # Add more Workday employers here, e.g.:
    # WorkdayConfig(
    #     tenant="gsk",
    #     wd_host="wd3",
    #     site="GSK",
    #     company_name="GSK",
    #     company_website="https://www.gsk.com",
    #     search_text="placement",
    # ),
]
