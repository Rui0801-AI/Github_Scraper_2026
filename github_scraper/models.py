from __future__ import annotations

from dataclasses import dataclass
import re


DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
GOOGLE_SHEET_URL_PATTERN = re.compile(r"/spreadsheets/d/([a-zA-Z0-9-_]+)")

DESTINATION_LOCAL = "local machine"
DESTINATION_GOOGLE_SHEET = "google sheet"


@dataclass(slots=True)
class SearchFilters:
    location: str
    specific_query: str = ""
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


@dataclass(slots=True)
class ExportSettings:
    destination: str = DESTINATION_LOCAL
    local_path: str = ""
    spreadsheet_id_or_url: str = ""
    worksheet_name: str = "Sheet1"
    apps_script_url: str = ""
    service_account_file: str = ""

    def validate(self) -> str | None:
        if self.destination == DESTINATION_LOCAL:
            if not self.local_path.strip():
                return "Choose a local CSV file."
            return None

        if self.destination != DESTINATION_GOOGLE_SHEET:
            return "Choose a valid save destination."

        if not self.spreadsheet_id_or_url.strip():
            return "Enter a Google Sheet URL or spreadsheet ID."

        if not self.worksheet_name.strip():
            return "Enter a Google Sheet tab name."

        if not self.apps_script_url.strip() and not self.service_account_file.strip():
            return "Enter a Google Apps Script Web App URL or choose a service account JSON file."

        return None

    def spreadsheet_id(self) -> str:
        raw_value = self.spreadsheet_id_or_url.strip()
        match = GOOGLE_SHEET_URL_PATTERN.search(raw_value)
        if match:
            return match.group(1)
        return raw_value
