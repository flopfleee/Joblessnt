"""
Heuristic subject tagging: matches keywords in a job's title/description
against your fixed `subjects` table. This is a starting point, not a real
classifier — tune the keyword lists as you see what scrapers pull in.
"""

SUBJECT_KEYWORDS = {
    "Computer Science": ["software", "computer science", "developer", "programming", "data science"],
    "Software Engineering": ["software engineer", "software engineering", "full stack", "backend", "frontend", "devops"],
    "Finance": ["finance", "financial", "accounting", "audit", "treasury", "investment"],
    "Business": ["business", "commercial", "operations", "strategy", "consulting"],
    "Engineering": ["engineering", "engineer", "mechanical", "electrical", "civil", "aerospace", "manufacturing"],
    "Marketing": ["marketing", "brand", "communications", "social media", "pr "],
    "Mathematics": ["mathematics", "actuarial", "statistics", "quantitative"],
}


def tag_subjects(title: str, description: str | None = None) -> list[str]:
    text = f"{title} {description or ''}".lower()

    matched = []
    for subject, keywords in SUBJECT_KEYWORDS.items():
        if any(keyword in text for keyword in keywords):
            matched.append(subject)

    return matched
