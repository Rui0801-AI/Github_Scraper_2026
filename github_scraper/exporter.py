from __future__ import annotations

import csv
import re


EMAIL_PATTERN = re.compile(r"[\w\.-]+@[\w\.-]+")


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


def export_profiles_to_csv(details: list[dict], file_path: str) -> int:
    seen: set[str] = set()
    exported_count = 0

    with open(file_path, "w", newline="", encoding="utf-8") as file_obj:
        writer = csv.writer(file_obj)
        writer.writerow(["username", "url", "location", "email", "linkedin"])

        for detail in details:
            username = detail.get("login")
            if not username or username in seen:
                continue

            seen.add(username)
            email = detail.get("email") or extract_email(detail.get("bio"))
            linkedin = extract_linkedin(detail.get("blog"), detail.get("bio"))

            writer.writerow(
                [
                    username,
                    detail.get("html_url"),
                    detail.get("location"),
                    email,
                    linkedin,
                ]
            )
            exported_count += 1

    return exported_count
