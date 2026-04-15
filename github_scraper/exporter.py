from __future__ import annotations

import csv
import re
from pathlib import Path


EMAIL_PATTERN = re.compile(r"[\w\.-]+@[\w\.-]+")
CSV_HEADERS = ["username", "url", "location", "email", "linkedin"]


def extract_email(text: str | None) -> str:
    if not text:
        return ""

    match = EMAIL_PATTERN.search(text)
    return match.group(0) if match else ""


def extract_linkedin(blog: str | None, bio: str | None) -> str:
    for text in (blog, bio):
        if text and "linkedin.com/in/" in text.lower():
            return text
    return ""


def _load_existing_usernames(file_path: Path) -> set[str]:
    if not file_path.exists():
        return set()

    with file_path.open("r", newline="", encoding="utf-8") as file_obj:
        reader = csv.DictReader(file_obj)
        return {row["username"] for row in reader if row.get("username")}


def export_profiles_to_csv(details: list[dict], file_path: str) -> int:
    csv_path = Path(file_path)
    seen = _load_existing_usernames(csv_path)
    appended_count = 0
    write_header = not csv_path.exists() or csv_path.stat().st_size == 0

    with csv_path.open("a", newline="", encoding="utf-8") as file_obj:
        writer = csv.writer(file_obj)
        if write_header:
            writer.writerow(CSV_HEADERS)

        for detail in details:
            username = detail.get("login")
            if not username or username in seen:
                continue

            email = detail.get("email") or extract_email(detail.get("bio"))
            linkedin = extract_linkedin(detail.get("blog"), detail.get("bio"))
            if not email and not linkedin:
                continue

            seen.add(username)

            writer.writerow(
                [
                    username,
                    detail.get("html_url"),
                    detail.get("location"),
                    email,
                    linkedin,
                ]
            )
            appended_count += 1

    return appended_count
