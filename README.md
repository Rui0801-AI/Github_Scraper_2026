# GitHub Scraper 2026

A desktop Tkinter app for searching public GitHub profiles by location and optional filters, then exporting the results to CSV.

## Features

- Search GitHub users by required location
- Narrow results with optional keyword, creation date, repository count, and follower count filters
- Export profile details to CSV
- Include email and LinkedIn details when they are publicly available
- Track progress while profile details are being fetched

## Requirements

- Python 3.10+
- `aiohttp`

## Install

```bash
pip install aiohttp
```

## Run

```bash
python main.py
```

## Exported Columns

The generated CSV includes:

- `username`
- `url`
- `location`
- `email`
- `linkedin`

## Notes

- A GitHub token is optional, but recommended to reduce rate-limit issues.
- `Location` is the only required search field.
- `Creation Date` must use `YYYY-MM-DD`.
- Min and max repo/follower fields must be whole numbers.

## Project Structure

```text
main.py
github_scraper/
  exporter.py
  models.py
  scraper.py
  ui.py
```

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).
