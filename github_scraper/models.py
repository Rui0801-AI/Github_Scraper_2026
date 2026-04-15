from __future__ import annotations

from dataclasses import dataclass
import re


DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")


@dataclass(slots=True)
class SearchFilters:
    location: str
    created_after: str = ""
    min_repos: str = ""
    max_repos: str = ""
    min_followers: str = ""
    max_followers: str = ""

    def validate(self) -> str | None:
        if not self.location.strip():
            return "Location is required."

        if self.created_after and not DATE_PATTERN.match(self.created_after):
            return "Created After must use YYYY-MM-DD format."

        numeric_fields = {
            "Min Repos": self.min_repos,
            "Max Repos": self.max_repos,
            "Min Followers": self.min_followers,
            "Max Followers": self.max_followers,
        }

        for label, value in numeric_fields.items():
            if value and not value.isdigit():
                return f"{label} must be a whole number."

        return None
